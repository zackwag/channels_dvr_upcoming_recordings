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
2. Restart Home Assistant
3. If your Channels DVR installation is discovered via Zeroconf, you will get a notification and will be able to configure the integration without the need to specify the host and port.  Otherwise, add the integration from Configuration->Integrations->Add Integration.  Search for "Channels".
4. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
5. Add the code for the card to your `ui-lovelace.yaml`.

### Options

This integration can only be configuration through the UI (Configuration->Integrations), and the options below can be configured when the integration is added (`host` and `port` aren't needed for a Zeroconf configuration).

| key             | default                                          | required | description                                                                                                                                    |
| --------------- | ------------------------------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| name            | Recently_Recorded                                | no       | Name of the sensor.                                                                 |
| host            | localhost                                        | yes      | The host Channels DVR is running on (not required if the installation is automatically discovered).                                  |
| port            | 8089                                             | yes      | The port Channels DVR is running on (not required if the installation is automatically discovered).                                  |
| max             | 5                                                | no       | Max number of items to show in sensor.                                                                                                         |
| download_images | true                                             | no       | Setting this to false will turn off downloading of images.                                                                                     |
| img_dir         | '/upcoming-media-card-images/recently_recorded/' | no       | This option allows you to choose a custom directory to store images in if you enable download_images. Directory must start and end with a `/`. |

#### By default this addon automatically downloads images from the Channels site to your /www/custom-lovelace/upcoming-media-card/ directory. The directory is automatically created & only images reported in the upcoming list are downloaded. Images are small in size and are removed automatically when no longer needed.

</br></br>
**Do not just copy examples, please use config options above to build your own!**

### Sample for ui-lovelace.yaml:

```yaml
- type: custom:upcoming-media-card
  entity: sensor.recently_recorded
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
