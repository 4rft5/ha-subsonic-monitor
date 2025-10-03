# Subsonic Monitor

A Home Assistant add-on that monitors a Subsonic API (Navidrome, etc) profile and allows it to be displayed as a card.

## Information
This add-on tries to bridge a gap that somehow exists between Home Assistant and Subsonic APIs. As of right now, it gets information from the API (username, password, server url) and passes it through to make the card.

The add-on uses the API to calculate playback state, display album art and the title and artist of the song. The playback state status is represented and updated as the icon for the card.

Since the API doesn't convey true "idle" or "paused" states, the add-on checks if the song runtime has been idle for thirty seconds. If it has, it is put into the "paused" state. If it doesn't change for more than five minutes, it becomes "Idle".

## Installation
1. Download the latest version of the add-on from <a href="https://github.com/4rft5/ha-subsonic-monitor/releases">Releases</a>.

2. Place the extracted ha-jf-profile-monitor folder into your `custom_components` folder.
   
3. Add Integration by clicking "Add Integration" and searching for "Subsonic Monitor".

4. Input Credentials and Navidrome-Compatible Server IP/hostname (e.g. `subsonic.local`, `localhost:4533` or `192.168.1.1:4533`).

5. Add the newly-created entity to your cards or dashboard.

## Screenshots
A Regular Card:

![image](https://github.com/user-attachments/assets/0f9c02db-bfca-489d-a0db-9c82659f44b8)

Regular Card with playback information:

![image](https://github.com/user-attachments/assets/ae7173f2-4a0a-45f4-aa36-4ddcdc4ff63a)

Example of the "idle" playback state:

![image](https://github.com/user-attachments/assets/3e6f2907-d267-4e6b-900e-6d1a652cf011)


Examples of the media-control card:

![image](https://github.com/user-attachments/assets/209ed0ed-2788-4078-af96-93cda894b8fb)



## Contributions

Pull Requests and other contributions are welcome, especially with things like the icon for the integrations menu and HACS publishing.

Media Controls do not work, as this currently only can display the status of a profile, but would be welcomed additions if someone wanted to tackle them.

### Issues

The console will log that the newly created media_player does not support media_player features (playback). This is intended as playback controls are not integrated.

