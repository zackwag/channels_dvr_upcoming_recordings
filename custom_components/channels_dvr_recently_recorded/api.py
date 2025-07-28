import aiohttp
import async_timeout
import json
import logging
import time
from json.decoder import JSONDecodeError

_LOGGER = logging.getLogger(__name__)

VERSION = "version"
STATUS_ENDPOINT = "/status"
FILES_ENDPOINT = "/dvr/files?all=true"
JOBS_ENDPOINT = "/dvr/jobs"
AUTH_ENDPOINT = "/auth"

DEFAULT_PORT = 8089


class ChannelsDVR:
    def __init__(self, host, port):
        self._version = None
        self.host = host
        self.port = port

    async def request(self, uri):
        """Request content from a URI."""
        async with aiohttp.ClientSession() as session:
            try:
                with async_timeout.timeout(8):
                    async with session.get(uri) as response:
                        return (
                            await response.content.read()
                            if response.status == 200
                            else None
                        )
            except Exception:
                return None

    @property
    def version(self):
        """Return the version number of the server software."""
        return self._version

    async def request_data(self, uri):
        """Request data from an endpoint."""
        try:
            resp = await self.request(uri)
        except (OSError, AttributeError):
            msg = f"Host {self.host} is not available"
            _LOGGER.error(msg)
            raise ConnectionFail(msg)
        except Exception:
            msg = "Unexpected exception"
            _LOGGER.exception(msg)
            raise ConnectionFail(msg)

        if resp is not None:
            json_string = resp.decode("utf-8")
            data = json.loads(json_string)
            if not data:
                msg = "Response cannot be decoded"
                _LOGGER.warning(msg)
                raise ConnectionFail(msg)
        else:
            msg = f"{self.host} cannot be reached"
            _LOGGER.warning(msg)
            raise ConnectionFail(msg)

        return data

    async def init_data(self):
        """Get the version number of the server"""
        status_uri = f"http://{self.host}:{self.port}{STATUS_ENDPOINT}"
        status = await self.request_data(status_uri)
        self._version = {VERSION: status[VERSION]}

    async def get_files(self):
        """Get the list of recorded files from the server."""
        files_uri = f"http://{self.host}:{self.port}{FILES_ENDPOINT}"
        _LOGGER.debug("Updating recorded files")
        return await self.request_data(files_uri)

    async def get_upcoming(self):
        """Get the list of upcoming scheduled recordings from the server."""
        jobs_uri = f"http://{self.host}:{self.port}{JOBS_ENDPOINT}"
        _LOGGER.debug("Updating upcoming recordings")
        jobs = await self.request_data(jobs_uri)

        now = time.time()
        # Only keep jobs with no FileID (not recorded yet) and future start time
        upcoming = [
            job for job in jobs
            if not job.get("FileID") and job.get("Time", 0) > now
        ]

        # Sort by start time
        upcoming.sort(key=lambda j: j.get("Time", 0))
        return upcoming

    async def get_poster(self, image_uri):
        """Get the poster for a show from the server."""
        return await self.request(image_uri)

    async def get_auth(self):
        """Make sure we can reach the server and get the unique ID (verification)"""
        auth_uri = f"http://{self.host}:{self.port}{AUTH_ENDPOINT}"
        return await self.request_data(auth_uri)


class ConnectionFail(Exception):
    """Error to indicate there is no connection."""

    def __init__(self, msg):
        self.msg = msg
