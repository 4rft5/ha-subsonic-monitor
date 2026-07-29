import os
import aiohttp
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerState
from homeassistant.util import dt as dt_util
from urllib.parse import quote_plus
from .const import DOMAIN

# Mapping from OpenSubsonic playbackReport state strings to HA MediaPlayerState.
# "starting" is treated as PLAYING since buffering has begun.
_SUBSONIC_STATE_MAP = {
    "starting": MediaPlayerState.PLAYING,
    "playing": MediaPlayerState.PLAYING,
    "paused": MediaPlayerState.PAUSED,
    "stopped": MediaPlayerState.IDLE,
}


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
        self._media_duration = None
        self._media_image_url = None
        self._current_cover_id = None
        self._icon = "mdi:stop"
        self._playback_state = None
        self._position_ms = None
        self._playback_rate = None
        self._position_updated_at = None

    @property
    def unique_id(self):
        """Stable unique ID derived from server + username."""
        return f"subsonic_{self._server}_{self._username}"

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

        now_playing = (
            data.get("subsonic-response", {})
            .get("nowPlaying", {})
            .get("entry", [])
        )

        if isinstance(now_playing, dict):
            now_playing = [now_playing]

        if not now_playing:
            self._set_idle()
            return

        item = now_playing[0]

        self._media_title = item.get("title")
        self._media_artist = item.get("displayArtist") or item.get("artist")
        self._media_album = item.get("album")
        self._media_duration = item.get("duration")  # seconds, standard Subsonic field

        # --- OpenSubsonic playbackReport fields ---
        raw_state = item.get("state")
        self._playback_state = raw_state
        self._playback_rate = item.get("playbackRate")

        position_ms = item.get("positionMs")
        if position_ms is not None:
            # Server supports playbackReport extension — use exact value.
            self._position_ms = position_ms
            self._position_updated_at = dt_util.utcnow()
        elif item.get("minutesAgo") is not None and self._media_duration is not None:
            # Fallback: estimate from minutesAgo, clamped to track duration.
            elapsed_seconds = item["minutesAgo"] * 60
            self._position_ms = min(elapsed_seconds, self._media_duration) * 1000
            self._position_updated_at = dt_util.utcnow()
        else:
            self._position_ms = None
            self._position_updated_at = None

        # Derive HA state from server-reported playback state if present,
        # otherwise fall back to PLAYING (entry exists = something is playing).
        if raw_state in _SUBSONIC_STATE_MAP:
            self._state = _SUBSONIC_STATE_MAP[raw_state]
        else:
            self._state = MediaPlayerState.PLAYING

        # Icon shows the *action* you'd take, not the current state.
        # Playing → show pause bars; paused/idle → show play triangle.
        self._icon = (
            "mdi:pause"
            if self._state == MediaPlayerState.PLAYING
            else "mdi:play"
        )

        # --- Cover art ---
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
                            await self._hass.async_add_executor_job(
                                _write_image, img_path, img_bytes
                            )
                            self._current_cover_id = cover_id
                            self._media_image_url = f"/local/{img_filename}?v={cover_id}"
            except Exception:
                self._media_image_url = None
        elif not cover_tag:
            self._media_image_url = None

    def _set_idle(self):
        self._state = MediaPlayerState.IDLE
        self._media_title = None
        self._media_artist = None
        self._media_album = None
        self._media_duration = None
        self._media_image_url = None
        self._icon = "mdi:stop"
        self._playback_state = None
        self._position_ms = None
        self._playback_rate = None
        self._position_updated_at = None

    # ----- HA MediaPlayerEntity properties -----

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"subsonic_{self._server}_{self._username}"

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
    def media_duration(self):
        """Total track duration in seconds."""
        return self._media_duration

    @property
    def media_position(self):
        """Current position in seconds, derived from positionMs."""
        if self._position_ms is not None:
            return self._position_ms / 1000
        return None

    @property
    def media_position_updated_at(self):
        """UTC timestamp of when media_position was last sampled.
        Required by HA to display and interpolate the seek bar."""
        return self._position_updated_at

    @property
    def extra_state_attributes(self):
        attrs = {
            "artist": self._media_artist,
            "album": self._media_album,
        }
        if self._playback_state is not None:
            attrs["playback_state"] = self._playback_state
        if self._position_ms is not None:
            attrs["position_ms"] = self._position_ms
        if self._playback_rate is not None:
            attrs["playback_rate"] = self._playback_rate
        return attrs
