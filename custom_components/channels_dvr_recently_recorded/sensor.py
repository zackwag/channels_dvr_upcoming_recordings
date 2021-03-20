"""
Home Assistant component to feed the Upcoming Media Lovelace card with
Channels DVR recently recorded shows.

https://github.com/custom-cards/upcoming-media-card

"""
from json.decoder import JSONDecodeError
from custom_components.channels_dvr_recently_recorded import DOMAIN, VERSION, request
import logging
import json
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.helpers.entity import Entity
from dateutil.parser import parse
from urllib.parse import urlparse
from datetime import timedelta


SCAN_INTERVAL = timedelta(seconds=30)
_LOGGER = logging.getLogger(__name__)

FILES_ENDPOINT = "/dvr/files?all=true"
DEFAULT_PORT = 8089

CONF_DL_IMAGES = "dl_images"
CONF_HOSTNAME = "hostname"
CONF_IMG_DIR = "img_dir"
CONF_MAX = "max"
CONF_VERIFICATION = "verification"

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

DEFAULT_NAME = "Recently Recorded"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor entity."""
    async_add_entities([ChannelsDVRRecentlyRecordedSensor(hass, config_entry)])


class ChannelsDVRRecentlyRecordedSensor(Entity):
    def __init__(self, hass, conf):
        self._name = conf.data.get(CONF_NAME)
        self.conf_dir = str(hass.config.path()) + "/"
        self._dir = conf.data.get(CONF_IMG_DIR)
        if self._name:
            self._dir = self._dir + self._name.replace(" ", "_") + "/"
        self.max_items = int(conf.data.get(CONF_MAX))
        self.dl_images = conf.data.get(CONF_DL_IMAGES)
        self.server_ip = conf.data.get(CONF_HOST)
        self.port = conf.data.get(CONF_PORT)
        self.hostname = conf.data.get(CONF_HOSTNAME)
        self.verification = conf.data.get(CONF_VERIFICATION)
        self._state = None
        self._attrs = []
        self.version = hass.data[DOMAIN][conf.entry_id][VERSION]
        _LOGGER.debug(f"{self.version}")

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def state_attributes(self):
        if not len(self._attrs):
            return
        return {"data": self._attrs}

    @property
    def unique_id(self):
        """Return unique ID."""
        return self.verification

    @property
    def device_info(self):
        _LOGGER.debug(f"Version: {self.version}")
        """Device info."""
        return {
            "identifiers": {(DOMAIN, self.verification)},
            "name": "Channels DVR Recordings",
            "manufacturer": "Channels",
            "model": "DVR Server",
            "default_name": "Channels DVR Recordings",
            "entry_type": "service",
            "sw_version": self.version,
        }

    @callback
    async def async_added_to_hass(self):
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_update(self):
        import os
        import re

        files_uri = f"http://{self.server_ip}:{self.port}{FILES_ENDPOINT}"
        _LOGGER.debug(f"Updating")

        """Retrieve recorded show info and server version"""
        try:
            resp = await request(files_uri)
            json_string = resp.decode("utf-8")
            files = json.loads(json_string)
            if not files:
                self._state = "%s cannot be reached" % self.server_ip
                return

        except OSError:
            _LOGGER.warning("Host %s is not available", self.server_ip)
            self._state = "%s cannot be reached" % self.server_ip
            return

        except JSONDecodeError:
            _LOGGER.warning("Couldn't decode data returned from %s", self.server_ip)
            self._state = "Couldn't decode data returned from %s" % self.server_ip
            return

        self._state = "Online"

        """Only look for recorded programs"""
        recordings = [x for x in files if x["JobID"] != "" and x["Deleted"] == False]
        recordings.sort(
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
            ICON: "mdi:eye",
        }

        self._attrs.append(attr)

        num_items = 0

        for recording in recordings:
            episode = recording["Airing"]

            num_items += 1
            if num_items > self.max_items:
                break

            attr = {
                AIRDATE: ""
                if not episode["Raw"].get("startTime", None)
                else parse(episode["Raw"]["startTime"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                AIRED: episode.get("OriginalDate", ""),
                FLAG: recording.get("Watched", False),
                TITLE: episode.get("Title", ""),
                EPISODE: episode.get("EpisodeTitle", ""),
                NUMBER: "S%02d" % episode.get("SeasonNumber", 0)
                + "E%02d" % episode.get("EpisodeNumber", 0),
                RUNTIME: episode["Raw"].get("duration", 0),
                GENRES: episode.get("Genres", ""),
                RATING: ""
                if not episode["Raw"]["ratings"]
                else episode["Raw"]["ratings"][0]["code"],
                POSTER: episode["Raw"]["program"]["preferredImage"].get("uri", ""),
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

        _LOGGER.debug(f"Finished updating")
