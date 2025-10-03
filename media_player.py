import aiohttp
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerState
from urllib.parse import quote_plus
from .const import DOMAIN

async def fetch_subsonic_users(username, password, server):
    import urllib.parse
    u = urllib.parse.quote_plus(username)
    p = urllib.parse.quote_plus(password)
    url = f"{server}/rest/getNowPlaying.view?u={u}&p={p}&v=1.16.1&f=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            try:
                data = await resp.json()
                return data.get("subsonic-response", {}).get("nowPlaying", {}).get("entry", [])
            except Exception:
                return []

class SubsonicPlayer(MediaPlayerEntity):
    def __init__(self, username, password, server):
        self._attr_name = f"Subsonic - {username}"
        self._username = username
        self._password = password
        self._server = server
        self._state = MediaPlayerState.IDLE
        self._media_title = None
        self._media_artist = None
        self._media_album = None
        self._media_image_url = None
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
        if cover_tag:
            self._media_image_url = (
                f"{self._server}/rest/getCoverArt.view"
                f"?id={item.get('id')}&tag={cover_tag}"
                f"&u={quote_plus(self._username)}&p={quote_plus(self._password)}"
                f"&c=ha-subsonic&v=1.16.1"
            )
        else:
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


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    username = data["username"]
    password = data["password"]
    server = data["server_url"]
    player = SubsonicPlayer(username, password, server)
    async_add_entities([player])
