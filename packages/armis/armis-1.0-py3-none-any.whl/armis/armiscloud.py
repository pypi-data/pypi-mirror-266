#!/usr/bin/python3

import contextlib
import gzip
import logging
import logging.handlers
import math
import pathlib as pl
import tempfile
import warnings

import httpx
import msgspec
import pendulum
from furl import furl
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from .__version__ import __version__


class ArmisCloud:
    """Armis class for interfacing with the Armis cloud."""

    # NOTE: Per Armis' API Guide 1.8 (dated 5/30/2023), the Armis
    # API has a maximum page size of 5,000.
    ARMIS_MAXIMUM_API_PAGE_SIZE: int = 5_000

    def __init__(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Construct an Armis class.

        Parameters
        ----------
        api_secret_key : str
            The secret key to use when talking to the Armis cloud.
        api_page_size : int
            Page size to use when talking to the Armis cloud, maximum is 5,000.
        tenant_hostname : str
            The hostname of the Armis cloud tenant, e.g. customer.armis.com
        log_level : {'INFO','CRITICAL','ERROR','WARNING','DEBUG','NOTSET'}
            Log level to log at, e.g. CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET.
        temporary_directory : str
            Location of temporary directory, or if blank, one will be
            automatically assigned.

        Examples
        --------
        ::

            armis = ArmisCloud(
                api_page_size=2_500,
                api_secret_key="secretkeyhere",
                tenant_hostname="customer1.armis.com",
            )

        Returns
        -------
        Armis
            Armis object.
        """
        self.log = logging.getLogger("Armis")
        self.log.setLevel(logging.INFO)
        log_level = kwargs.get("log_level", "INFO")
        self.log.info("log_level=%s", str(log_level))

        if log_level not in logging._nameToLevel:
            self.log.info("log level not found, setting to info")
            warnings.warn(
                "log level not found, setting to info",
                stacklevel=2,
            )

            self.log.setLevel(logging.INFO)
        else:
            logging_log_level = logging.getLevelName(log_level)
            self.log.info(
                "logging log level looked up and is=%s",
                str(logging_log_level),
            )
            self.log.setLevel(logging_log_level)

        self._authorization_token = 0
        self._authorization_token_expiration = 0

        self.temporary_directory = kwargs.get("temporary_directory", None)
        if self.temporary_directory is None:
            self.temporary_directory = tempfile.TemporaryDirectory()

        self.log.info("temporary_directory=%s", str(self.temporary_directory.name))

        self._http_timeout: int = 100

        self.ARMIS_API_PAGE_SIZE: int = kwargs.get(
            "api_page_size",
            self.ARMIS_MAXIMUM_API_PAGE_SIZE,
        )
        if self.ARMIS_API_PAGE_SIZE > self.ARMIS_MAXIMUM_API_PAGE_SIZE:
            self.log.info(
                "page size requested=%s, page size maximum is=%s",
                self.ARMIS_API_PAGE_SIZE,
                self.ARMIS_MAXIMUM_API_PAGE_SIZE,
            )
            warnings.warn(
                "page size requested="
                + str(self.ARMIS_API_PAGE_SIZE)
                + ", page size maximum="
                + str(self.ARMIS_MAXIMUM_API_PAGE_SIZE),
                stacklevel=2,
            )
        self.log.debug("api_page_size=%s", str(self.ARMIS_API_PAGE_SIZE))
        self.API_SECRET_KEY: str = kwargs.get("api_secret_key", None)
        if self.API_SECRET_KEY is None:
            raise ValueError("No secret key provided")

        self.HTTP_RETRY_MAX: int = 5
        self._httpx_limits = httpx.Limits(
            max_keepalive_connections=50,
            max_connections=200,
            keepalive_expiry=120,
        )
        self.httpx_client = self._get_httpx_client()

        tenant_hostname = kwargs.get("tenant_hostname", None)
        if tenant_hostname is None:
            raise ValueError("tenant_hostname is required")

        self.TENANT_BASE_URL = furl()
        self.TENANT_BASE_URL.scheme = "https"
        self.TENANT_BASE_URL.host = tenant_hostname
        self.TENANT_BASE_URL.path = "/api/"

        # Note that if you're making multiple calls to decode, it's more efficient
        # to create a Decoder once and use the Decoder.decode method instead.
        self._json_decoder = msgspec.json.Decoder()
        self._json_encoder = msgspec.json.Encoder()

    # cleanup
    def __del__(self):
        # close all outstanding httpx connections
        with contextlib.suppress(Exception):
            self.httpx_client.close()

    @staticmethod
    def _ceiling_up(number, nearest: int):
        if not isinstance(number, (int, float)):
            raise ValueError("number " + str(number) + " is not an int or float")
        if nearest is None:
            raise ValueError("nearest was not provided")

        return math.ceil(number / nearest) * nearest

    def _get_httpx_client(self):
        with contextlib.suppress(AttributeError):
            self.httpx_client.close()

        httpx_client = httpx.Client(
            follow_redirects=True,
            headers={
                "user-agent": f"Armis Python Library {__version__}",
            },
            http2=True,
            limits=self._httpx_limits,
            timeout=self._http_timeout,
            trust_env=False,
        )
        return httpx_client  # noqa: RET504

    def _api_http_request(self, **kwargs):
        """Wrap the request function and handles the authorization token.

        Parameters
        ----------
        method : str
            HTTP method, one of DELETE, GET, PATCH, POST, PUT, etc.
        url : str|furl
            the URL endpoint
        content : str, optional
            content to pass along
        headers : dict, optional
            headers to pass along
        json : dict, optional
            json to pass along
        params : str, optional
            params to pass along
        maximum_retries : int, optional
            maximum number of times to retry connection

        Raises
        ------
        ValueError
            If data provided is invalid.

        Returns
        -------
        response : request.response object
        """
        self.log.debug("kwargs=%s", str(kwargs))

        method: str = kwargs.get("method", None)
        url = kwargs.get("url", None)
        content: str = kwargs.get("content", "")
        headers: dict = kwargs.get("headers", {})
        json: dict = kwargs.get("json", {})
        params: str = kwargs.get("params", "")
        maximum_retries: int = kwargs.get("maximum_retries", self.HTTP_RETRY_MAX)

        if len(content) > 0 and len(json) > 0:
            raise ValueError("You can send content or JSON, not both")

        if method is None or url is None:
            raise ValueError("no method or url")

        if isinstance(url, str):
            url = furl(url)

        method = method.upper()

        if method not in {
            "DELETE",
            "GET",
            "PATCH",
            "POST",
        }:
            raise ValueError("method must be one of DELETE, GET, PATCH, or POST")

        for attempt in Retrying(  # noqa: RET503
            retry=retry_if_exception_type(httpx.HTTPStatusError)
            | retry_if_exception_type(msgspec.DecodeError)
            | retry_if_exception_type(httpx.RemoteProtocolError)
            | retry_if_exception_type(httpx.ConnectError)
            | retry_if_exception_type(httpx.ReadTimeout),
            wait=wait_random_exponential(multiplier=1, max=10),
            stop=stop_after_attempt(maximum_retries),
        ):
            with attempt:
                self.log.info(
                    "ATTEMPT NUMBER %s of %s",
                    str(attempt.retry_state.attempt_number),
                    str(maximum_retries),
                )
                if attempt.retry_state.attempt_number > 1:
                    self.log.info(
                        "attempt number >1, reducing page size, was %s",
                        str(url.args["length"]),
                    )
                    url.args["length"] = int(url.args["length"] * 0.75)
                    self.log.info("reducing page size, now %s", str(url.args["length"]))

                self._update_authorization_token()

                if method == "GET":
                    self.log.debug("GETting URL=%s", str(url))
                    r = self.httpx_client.get(str(url), headers=headers, params=params)
                    self.log.debug("r.status_code=%s", str(r.status_code))
                if method == "POST":
                    self.log.debug("POSTing URL=%s", str(url))
                    if len(json) > 0:
                        r = self.httpx_client.post(str(url), json=json, headers=headers)
                    elif len(content) > 0:
                        # r = self.httpx_client.post(str(url), data=data, headers=headers)
                        r = self.httpx_client.post(
                            str(url),
                            content=content,
                            headers=headers,
                        )

                    self.log.debug("r.status_code=%s", str(r.status_code))

                if method == "PATCH":
                    self.log.debug("PATCHing URL=%s", str(url))
                    if len(json) > 0:
                        r = self.httpx_client.patch(
                            str(url),
                            json=json,
                            headers=headers,
                        )
                    elif len(content) > 0:
                        r = self.httpx_client.patch(
                            str(url),
                            content=content,
                            headers=headers,
                        )

                    self.log.debug("r.status_code=%s", str(r.status_code))

                if method == "DELETE":
                    # NOTE: httpx_client.delete method doesn't work as you're
                    # not supposed to send data with a DELETE request.
                    # Instead, we'll use the generic request method to do this.
                    # See
                    # https://tinyurl.com/httpx-delete
                    self.log.debug("DELETEing URL=%s", str(url))
                    if len(json) > 0:
                        r = self.httpx_client.request(
                            "DELETE",
                            str(url),
                            json=json,
                            headers=headers,
                        )
                    elif len(content) > 0:
                        r = self.httpx_client.request(
                            "DELETE",
                            str(url),
                            content=content,
                            headers=headers,
                        )
                    else:
                        r = self.httpx_client.request(
                            "DELETE",
                            str(url),
                            headers=headers,
                        )

                self.log.debug("response http version=%s", str(r.http_version))

                try:
                    _ = self._json_decoder.decode(r.text)
                except msgspec.DecodeError as err:
                    self.log.critical("exception: %s", str(err))
                    self.log.debug("text of response=%s", r.text)
                    raise err

                self.log.debug("size of return text=%s", str(len(r.text)))
                if len(r.text) < 1000:
                    self.log.debug("return text=%s", r.text)

                return r

    def _update_authorization_token(self) -> None:
        """Fetch an authorization token.

        Check if the token we have is still valid.  If not, get a new token and
        stash it in the object and update the HTTPX client header.
        """
        self.log.debug("BEGIN")
        now = pendulum.now().timestamp()
        remaining_time = self._authorization_token_expiration - now
        self.log.debug("now=%s", str(now))
        self.log.debug("remaining_time=%s", str(remaining_time))

        if remaining_time < 1_000:
            self.log.debug("remaining_time < 1000")
            self.log.debug("expires=%s", str(self._authorization_token_expiration))
            self.log.debug("now > _authorization_token_expiration")
            self.log.debug("_authorization_token expired, getting new one")
            url = str(self.TENANT_BASE_URL / "v1/access_token/")
            r = self.httpx_client.post(
                url,
                data={
                    "secret_key": self.API_SECRET_KEY,
                },
            )
            returnjson = self._json_decoder.decode(r.text)
            self.log.info("returnjson=%s", str(returnjson))

            if "access_token" in returnjson["data"]:
                self._authorization_token = returnjson["data"]["access_token"]
                self.log.debug(
                    "RAW expiration_utc=%s",
                    str(returnjson["data"]["expiration_utc"]),
                )
                self._authorization_token_expiration = pendulum.parse(
                    returnjson["data"]["expiration_utc"],
                ).timestamp()
                self.log.debug("RAW authorization_token=%s", self._authorization_token)
                self.log.debug(
                    "parsed authorization_token_expiration=%s",
                    str(self._authorization_token_expiration),
                )
            else:
                self.log.debug("access_token=None")  # pragma: no cover
        else:
            self.log.debug("expires=%s", str(self._authorization_token_expiration))
            self.log.debug("now < _authorization_token_expiration")

        self.httpx_client.headers["Authorization"] = self._authorization_token

        self.log.debug("END")

    def get_device_count(self, **kwargs: dict) -> int:
        """Get count of devices matching ASQ.

        Parameters
        ----------
        asq : str
            ASQ to execute.

        Returns
        -------
        int
            Count of devices matching ASQ.
        """
        asq = kwargs.get("asq", None)

        if asq is None:
            raise ValueError("asq is required")
        self.log.info("asq=%s", asq)

        url = self.TENANT_BASE_URL / "v1" / "devices" / "/"
        url.args["search"] = asq
        url.args["length"] = 1
        url.args["from"] = 0
        url.args["fields"] = "id"
        self.log.debug("url=%s", str(url))

        inventory_total_request = self._api_http_request(method="GET", url=url)
        if inventory_total_request.status_code != httpx.codes.OK:
            raise Exception(
                "inventory issue",
                inventory_total_request.text,
            )  # pragma: no cover

        inventory_total = int(
            self._json_decoder.decode(inventory_total_request.text)["data"]["total"],
        )
        self.log.info("inventory_total=%s", str(inventory_total))
        return inventory_total

    def get_devices(self, **kwargs: dict) -> list:
        """Get devices from inventory matching ASQ.

        Parameters
        ----------
        asq : str
            ASQ to execute.
        fields_wanted : list
            List of fields wanted.

        Returns
        -------
        inventory: list
            Inventory items matching ASQ.
        """
        get_devices_start = pendulum.now()
        asq = kwargs.get("asq", None)
        if asq is None:
            raise ValueError("no asq provided")
        self.log.info("asq=%s", asq)

        fields_wanted = kwargs.get("fields_wanted", [])
        self.log.info("fields_wanted=%s", str(",".join(fields_wanted)))

        url = self.TENANT_BASE_URL / "v1" / "devices" / "/"
        url.args["search"] = asq
        url.args["from"] = 0
        url.args["length"] = self.ARMIS_API_PAGE_SIZE

        # NOTE:
        # From the API Guide v1.8:
        # Iterating over a set of results it is recommended best practice to
        # orderBy a fixed parameter (deviceId for example) in order to not to
        # miss data between pages. This is because the default order is by
        # lastSeen, so results can change.
        url.args["orderBy"] = "id"

        inventory = []
        inventory_total = self.get_device_count(asq=asq)
        self.log.debug("inventory_total=%s", str(inventory_total))

        if inventory_total == 0:
            return []

        remaining_time = -1
        filenames = []
        filenumber = 1

        while url.args["from"] is not None:
            page_fetch_start = pendulum.now()
            self.log.info(
                "fetching %s - %s of a total of %s",
                str(url.args["from"]),
                str(url.args["from"] + self.ARMIS_API_PAGE_SIZE),
                str(inventory_total),
            )
            device_details = self._api_http_request(method="GET", url=url)

            if device_details.status_code != httpx.codes.OK:  # pragma: no cover
                self.log.critical("STATUS CODE !=200")  # pragma: no cover
                self.log.critical(
                    "status_code=%s",
                    str(device_details.status_code),
                )  # pragma: no cover
                self.log.critical("text=%s", device_details.text)  # pragma: no cover
                self.log.critical("continuing")  # pragma: no cover
                continue  # pragma: no cover

            devices = self._json_decoder.decode(device_details.text)
            totaldevices = devices["data"]["total"]

            if len(devices["data"]["data"]) > 0:
                fetchedcolumns = list(devices["data"]["data"][0].keys())
                self.log.debug("Fetched columns=%s", str(fetchedcolumns))
                setdiff = set(fields_wanted).difference(fetchedcolumns)
                if len(setdiff) > 0:
                    self.log.info(
                        "Fields missing from wanted columns=%s",
                        ",".join(list(setdiff)),
                    )
                    raise ValueError(
                        "Fields wanted="
                        + ",".join(fields_wanted)
                        + "\nFields fetched="
                        + ",".join(fetchedcolumns)
                        + "\nFields missing from wanted columns="
                        + ",".join(list(setdiff)),
                    )
            else:
                self.log.debug(
                    "can't find fields, return from this iteration=%s",
                    str(devices),
                )  # pragma: no cover
                return []  # pragma: no cover

            now = pendulum.now()
            filename = pl.Path(
                str(self.temporary_directory.name)
                + "/"
                + f"devices_{now.float_timestamp}.json.gz",
            )

            self.log.info("devices filename=%s", str(filename))
            # using default zlib compression level (i.e. -1 AKA 6)
            filename.write_bytes(gzip.compress(device_details.content))
            filenames.append(filename)
            filenumber += 1

            now = pendulum.now()
            self.log.debug("now=%s", str(now))
            self.log.debug("get_devices_start=%s", str(get_devices_start))

            total_elapsed_time = now.timestamp() - get_devices_start.timestamp()
            self.log.debug("total_elapsed_time=%s", str(total_elapsed_time))

            page_fetch_time = now.timestamp() - page_fetch_start.timestamp()
            self.log.info("page fetch time=%s", str(page_fetch_time))

            # if the page_fetch_time exceeds 90% of the http timeout,
            # start reducing the size of our pages so we can fit the page request
            # into the http timeout period.
            if page_fetch_time > self._http_timeout * 0.9:
                self.ARMIS_API_PAGE_SIZE = self._ceiling_up(
                    self.ARMIS_API_PAGE_SIZE * 0.90,
                    100,
                )  # pragma: no cover
                url.args["length"] = self.ARMIS_API_PAGE_SIZE  # pragma: no cover

                self.log.info(
                    r"page_fetch_time > %s, reducing page size by 10%% to %s",
                    str(int(self._http_timeout * 0.9)),
                    str(self.ARMIS_API_PAGE_SIZE),
                )  # pragma: no cover

            if url.args["from"] > 0:
                time_per_device = (
                    total_elapsed_time / url.args["from"]
                )  # pragma: no cover
                self.log.debug(
                    "time_per_device=%s",
                    str(time_per_device),
                )  # pragma: no cover

                remaining_devices = (
                    inventory_total - url.args["from"]
                )  # pragma: no cover
                self.log.debug(
                    "remaining_devices=%s",
                    str(remaining_devices),
                )  # pragma: no cover

                remaining_time = remaining_devices * time_per_device  # pragma: no cover
                self.log.debug(
                    "remaining_time=%s",
                    str(remaining_time),
                )  # pragma: no cover

            if remaining_time < 0:
                estimated_end_time = now
            else:
                estimated_end_time = now.add(seconds=remaining_time)  # pragma: no cover

            self.log.info("estimated_end_time=%s", str(estimated_end_time))

            url.args["from"] = devices["data"]["next"]

        # reproduce inventory here
        for filename in filenames:
            self.log.info("reading %s", str(filename.name))
            j = self._json_decoder.decode(gzip.decompress(filename.read_bytes()))
            self.log.info("appending %s records", str(len(j["data"]["data"])))
            inventory.extend(j["data"]["data"])

        self.log.debug("inventory size=%s", str(len(inventory)))

        return inventory

    def tag_device(self, **kwargs: dict) -> None:
        """Add or remove a device from a deviceid.

        Parameters
        ----------
        device_id : int
            Device ID to tag.
        tags: list|str
            Tags to add to or remove from the device ID.
        action: {'add', 'remove'}
            Action to perform, one of add or remove.
        """
        self.log.debug("tag_device")
        device_id = kwargs.get("device_id", None)
        if device_id is None:
            raise ValueError("no device_id specified")

        self.log.debug("device_id=%s", str(device_id))

        tags = kwargs.get("tags", [])
        self.log.debug("tags type=%s", str(type(tags)))

        if isinstance(tags, str):
            self.log.debug("type was string, converting to list")
            tags = [tags]

        self.log.debug("tags=[%s]", str(",".join(tags)))
        action: str = kwargs.get("action", "add")
        action = str(action).lower()
        self.log.debug("action=%s", str(action))

        if len(tags) == 0:
            raise ValueError("no tag provided")

        if action not in {"add", "remove"}:
            raise ValueError("no valid action provided, should be one of add or remove")

        url = self.TENANT_BASE_URL / "v1" / "devices" / str(device_id) / "tags/"
        self.log.debug("url=%s", str(url))

        tag_payload = {"tags": tags}
        self.log.debug("json currently=%s", str(tag_payload))
        self.log.info(
            "tagging, action=%s, deviceid=%s, tags=%s",
            action,
            device_id,
            str(",".join(tags)),
        )

        if action == "add":
            tag_device_update = self._api_http_request(
                method="POST",
                url=url,
                json=tag_payload,
            )
        if action == "remove":
            tag_device_update = self._api_http_request(
                method="DELETE",
                url=url,
                json=tag_payload,
            )

        self.log.debug("return text=%s", str(tag_device_update.text))
        self.log.debug("status_code=%s", str(tag_device_update.status_code))
        if tag_device_update.status_code != httpx.codes.OK:
            self.log.info("FAILED DEVICE TAG for device ID: %s", str(device_id))
            self.log.debug(tag_device_update.text)
            raise Exception("tag_device_update issue", tag_device_update.text)

        return tag_device_update.text
