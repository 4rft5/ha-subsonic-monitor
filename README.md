# Subsonic Monitor for Home Assistant

A Home Assistant integration that monitors a Subsonic API and allows it to be displayed as a card.

## Information
This add-on tries to bridge a gap that somehow exists between Home Assistant and Subsonic APIs. As of right now, it gets information from the API (username, password, server url) and passes it through to make the card.

The add-on uses the API to calculate playback state/location, display album art and the title and artist of the song. The playback state status is represented and updated as the icon for the card.

## Installation

### HACS

1. Add this repo to HACS as a custom repository:
   
[![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=4rft5&repository=ha-subsonic-monitor&category=Integration)

2. Install the integration from HACS

3. Restart Home Assistant

4. Setup the integration using the UI:
 
[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ha_subsonic_monitor)

5. Add the newly-created entity to your cards or dashboard.

### Manual

1. Download the latest version of the add-on from <a href="https://github.com/4rft5/ha-subsonic-monitor/releases">Releases</a>.

2. Place the extracted ha_subsonic_monitor folder into your `custom_components` folder.
   
3. Add Integration by clicking "Add Integration" and searching for "Subsonic Monitor".

4. Setup the integration using the UI:
 
[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ha_subsonic_monitor)

5. Add the newly-created entity to your cards or dashboard.

## Screenshots
A Regular Card:

<img width="200" height="48" alt="image" src="https://github.com/user-attachments/assets/79063b43-7568-4736-abd9-2cb69e85ebaa" />

Regular Card with playback information:

<img width="200" height="48" alt="image" src="https://github.com/user-attachments/assets/1090061d-234c-4f20-8b51-bdf7e1e6358a" />

Examples of the media-control card:

<img width="414" height="120" alt="image" src="https://github.com/user-attachments/assets/c5957ffa-e962-40fb-96c0-507f8b4ca943" />

## Contributions

Pull Requests and other contributions are welcome, especially with things like the icon for the integrations menu.

### Issues

Media Controls are not supported as the Subsonic API does not allow for remote control. This integration can only view and report what is playing on your server.

