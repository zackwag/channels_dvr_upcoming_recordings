"""
Home Assistant component to feed the Upcoming Media Lovelace card with
Channels DVR recently added media.

https://github.com/custom-cards/upcoming-media-card

"""
import logging
import json
import aiohttp
import async_timeout
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.helpers.entity import Entity
from dateutil.parser import parse
from urllib.parse import urlparse


SCAN_INTERVAL = timedelta(minutes=3)
_LOGGER = logging.getLogger(__name__)


FILES_ENDPOINT = "/dvr/files?all=true"

AIRDATE = "airdate"
AIRED = "aired"
FLAG = "flag"
RUNTIME = "runtime"
NUMBER = "number"
GENRES = "genres"
RATING = "rating"
POSTER = "poster"
FANART = "fanart"
TITLE = "title"
EPISODE = "episode"
RELEASE = "release"
TITLE_DEFAULT = "title_default"
LINE1_DEFAULT = "line1_default"
LINE2_DEFAULT = "line2_default"
LINE3_DEFAULT = "line3_default"
LINE4_DEFAULT = "line4_default"
ICON = "icon"


async def fetch(session, url):
    try:
        with async_timeout.timeout(8):
            async with session.get(url) as response:
                return await response.content.read()
    except:
        pass


async def request(url):
    async with aiohttp.ClientSession() as session:
        return await fetch(session, url)


CONF_DL_IMAGES = "download_images"
DEFAULT_NAME = "Channels DVR Recently Added"
CONF_SERVER = "server_name"
CONF_MAX = "max"
CONF_IMG_CACHE = "img_dir"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MAX, default=5): cv.string,
        vol.Optional(CONF_SERVER): cv.string,
        vol.Optional(CONF_DL_IMAGES, default=True): cv.boolean,
        vol.Optional(CONF_HOST, default="localhost"): cv.string,
        vol.Optional(CONF_PORT, default="8089"): cv.positive_int,
        vol.Optional(CONF_IMG_CACHE, default="/upcoming-media-card-images/"): cv.string,
    }
)


def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    add_devices([ChannelsDVRRecentlyAddedSensor(hass, config, name)], True)


class ChannelsDVRRecentlyAddedSensor(Entity):
    def __init__(self, hass, conf, name):
        self._name = name
        self.conf_dir = str(hass.config.path()) + "/"
        self._dir = conf.get(CONF_IMG_CACHE)
        if self._name:
            self._dir = self._dir + self._name.replace(" ", "_") + "/"
        self.server_name = conf.get(CONF_SERVER)
        self.max_items = int(conf.get(CONF_MAX))
        self.dl_images = conf.get(CONF_DL_IMAGES)
        self.server_ip = conf.get(CONF_HOST)
        self.port = conf.get(CONF_PORT)
        self._state = None
        self.data = []

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        if not len(self._attrs):
            return
        return {"data": self._attrs}

    async def async_update(self):
        import os
        import re

        url = f"http://{self.server_ip}:{self.port}{FILES_ENDPOINT}"
        _LOGGER.debug(f"{url=}")

        try:
            resp = await request(url)
            json_string = resp.decode("utf-8")
            files = json.loads(json_string)
            if not files:
                self._state = "%s cannot be reached" % self.server_ip
                return
        except OSError:
            _LOGGER.warning("Host %s is not available", self.server_ip)
            self._state = "%s cannot be reached" % self.server_ip
            return
        self._state = "Online"

        self.data = [x for x in files if x["JobID"] != ""]
        self.data.sort(
            reverse=True, key=lambda x: parse(x["Airing"]["Raw"]["startTime"])
        )

        if self.dl_images:
            directory = self.conf_dir + "www" + self._dir
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o777)

            """Make list of images in dir that use our naming scheme"""
            dir_re = re.compile(r"p.+\.jpg")
            dir_images = list(filter(dir_re.search, os.listdir(directory)))
            remove_images = dir_images.copy()

        self._attrs = []

        attr = {
            TITLE_DEFAULT: "$title",
            LINE1_DEFAULT: "$episode",
            LINE2_DEFAULT: "$release",
            LINE3_DEFAULT: "$number - $rating - $runtime",
            LINE4_DEFAULT: "$genres",
            ICON: "mdi:eye-off",
        }

        self._attrs.append(attr)

        num_items = 0

        for recording in self.data:
            episode = recording["Airing"]

            num_items += 1
            if num_items > self.max_items:
                break

            attr = {
                AIRDATE: parse(episode["Raw"]["startTime"]).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                AIRED: episode["OriginalDate"],
                FLAG: not recording["Watched"],
                TITLE: episode["Title"],
                EPISODE: episode["EpisodeTitle"],
                NUMBER: "S"
                + "%02d" % episode["SeasonNumber"]
                + "E"
                + "%02d" % episode["EpisodeNumber"],
                RUNTIME: episode["Raw"]["duration"],
                GENRES: episode["Genres"],
                RATING: episode["Raw"]["ratings"][0]["code"],
                RELEASE: "$day, $date $time",
            }

            image_uri = episode["Raw"]["program"]["preferredImage"]["uri"]

            if not self.dl_images:
                attr[POSTER] = image_uri
            else:
                """Update if media items have changed or images are missing"""
                filename = urlparse(image_uri).path.rsplit("/", 1)[-1]
                if filename not in dir_images:
                    poster_image = await request(image_uri)
                    if poster_image is not None:
                        image_file = directory + filename
                        open(image_file, "wb").write(poster_image)
                elif filename in remove_images:
                    remove_images.remove(filename)
                attr[POSTER] = "/local" + self._dir + filename

            self._attrs.append(attr)

        if self.dl_images:
            """Remove items no longer in the list"""
            _LOGGER.debug(f"Removing {remove_images}")
            [os.remove(directory + x) for x in remove_images]
