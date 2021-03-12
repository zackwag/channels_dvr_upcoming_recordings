# Channels DVR Recently Recorded Component

Home Assistant component to feed [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card) with
recently recorded shows.</br>
</br></br>

### Issues

Read through these two resources before posting issues to GitHub or the forums.

- [troubleshooting guide](https://github.com/custom-cards/upcoming-media-card/blob/master/troubleshooting.md)
- [@thomasloven's lovelace guide](https://github.com/thomasloven/hass-config/wiki/Lovelace-Plugins).

## Installation:

1. Install this component by copying [these files](https://github.com/rccoleman/channels_dvr_recently_recorded) to `custom_components/channels_dvr_recently_recorded/`.
2. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
3. Add the code to your `configuration.yaml` using the config options below.
4. Add the code for the card to your `ui-lovelace.yaml`.
5. **You will need to restart after installation for the component to start working.**

### Options

| key             | default                             | required | description                                                                                                                                    |
| --------------- | ----------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| name            | Channels_DVR_Recently_Recorded      | no       | Name of the sensor. Useful to make multiple sensors with different libraries.                                                                  |
| token           |                                     | yes      | Your Plex token [(Find your Plex token)](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)             |
| host            | localhost                           | yes      | The host Plex is running on.                                                                                                                   |
| port            | 8089                                | yes      | The port Plex is running on.                                                                                                                   |
| max             | 5                                   | no       | Max number of items to show in sensor.                                                                                                         |
| download_images | true                                | no       | Setting this to false will turn off downloading of images, but will require certain Plex settings to work. See below.                          |
| img_dir         | '/upcoming-media-card-images/plex/' | no       | This option allows you to choose a custom directory to store images in if you enable download_images. Directory must start and end with a `/`. |

#### By default this addon automatically downloads images from the Channels site to your /www/custom-lovelace/upcoming-media-card/ directory. The directory is automatically created & only images reported in the upcoming list are downloaded. Images are small in size and are removed automatically when no longer needed.

</br></br>
**Do not just copy examples, please use config options above to build your own!**

### Sample for minimal config needed in configuration.yaml:

```yaml
sensor:
  - platform: channels_dvr_recently_recorded
    host: 192.168.1.42
    port: 8089
```

### Sample for ui-lovelace.yaml:

```yaml
- type: custom:upcoming-media-card
  entity: sensor.channels_dvr_recently_recorded
  title: Recently Recorded
```

### Card Content Defaults

| key   | default                      | example                                             |
| ----- | ---------------------------- | --------------------------------------------------- |
| title | $title                       | "The Walking Dead"                                  |
| line1 | $episode                     | "What Comes After"                                  |
| line2 | $day, $date $time            | "Monday, 10/31 10:00 PM" Displays time of download. |
| line3 | $number - $rating - $runtime | "S01E12 - ★ 9.8 - 01:30"                            |
| line4 | $genres                      | "Action, Adventure, Comedy"                         |
| icon  | mdi:eye-off                  | https://materialdesignicons.com/icon/eye-off        |
