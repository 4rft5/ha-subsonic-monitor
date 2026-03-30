import os
import aiohttp
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerState
from urllib.parse import quote_plus
from .const import DOMAIN

def _write_image(img_path, img_bytes):
    with open(img_path, "wb") as f:
        f.write(img_bytes)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    username = data["username"]
    password = data["password"]
    server = data["server_url"]
    player = SubsonicPlayer(username, password, server, hass)
    async_add_entities([player])


class SubsonicPlayer(MediaPlayerEntity):
    def __init__(self, username, password, server, hass):
        self._attr_name = f"Subsonic - {username}"
        self._username = username
        self._password = password
        self._server = server
        self._hass = hass
        self._state = MediaPlayerState.IDLE
        self._media_title = None
        self._media_artist = None
        self._media_album = None
        self._media_image_url = None
        self._current_cover_id = None
        self._status = "Idle"
        self._icon = "mdi:stop"

    async def async_update(self):
        url = (
            f"{self._server}/rest/getNowPlaying.view"
            f"?u={quote_plus(self._username)}&p={quote_plus(self._password)}"
            f"&v=1.16.1&c=ha-subsonic&f=json"
        )

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        self._set_idle()
                        return
                    data = await resp.json()
            except Exception:
                self._set_idle()
                return

        now_playing = data.get("subsonic-response", {}).get("nowPlaying", {}).get("entry", [])

        if isinstance(now_playing, dict):
            now_playing = [now_playing]

        if not now_playing:
            self._set_idle()
            return

        item = now_playing[0]

        self._media_title = item.get("title")
        self._media_artist = item.get("displayArtist") or item.get("artist")
        self._media_album = item.get("album")

        cover_tag = item.get("coverArt")
        cover_id = item.get("id")

        if cover_tag and cover_id != self._current_cover_id:
            cover_url = (
                f"{self._server}/rest/getCoverArt.view"
                f"?id={cover_id}&tag={cover_tag}"
                f"&u={quote_plus(self._username)}&p={quote_plus(self._password)}"
                f"&c=ha-subsonic&v=1.16.1"
            )
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(cover_url) as img_resp:
                        if img_resp.status == 200:
                            img_bytes = await img_resp.read()
                            www_path = self._hass.config.path("www")
                            os.makedirs(www_path, exist_ok=True)
                            img_filename = f"subsonic_cover_{self._username}.jpg"
                            img_path = os.path.join(www_path, img_filename)
                            await self._hass.async_add_executor_job(_write_image, img_path, img_bytes)
                            self._current_cover_id = cover_id
                            self._media_image_url = f"/local/{img_filename}?v={cover_id}"
            except Exception:
                self._media_image_url = None
        elif not cover_tag:
            self._media_image_url = None

        self._state = MediaPlayerState.PLAYING
        self._status = "Playing"
        self._icon = "mdi:play"

    def _set_idle(self):
        self._state = MediaPlayerState.IDLE
        self._status = "Idle"
        self._media_title = None
        self._media_artist = None
        self._media_album = None
        self._media_image_url = None
        self._icon = "mdi:stop"

    @property
    def state(self):
        return self._status

    @property
    def icon(self):
        return self._icon

    @property
    def entity_picture(self):
        return self._media_image_url

    @property
    def media_title(self):
        return self._media_title

    @property
    def media_artist(self):
        return self._media_artist

    @property
    def media_album_name(self):
        return self._media_album

    @property
    def media_content_type(self):
        return "music"

    @property
    def extra_state_attributes(self):
        return {
            "Artist": self._media_artist,
            "Album": self._media_album,
        }
