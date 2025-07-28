# Channels DVR Upcoming Recordings Component

Home Assistant integration to feed [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card) with upcoming scheduled recordings from a [Channels DVR Server](https://getchannels.com/).

---

## Installation

### HACS

1. Open HACS
2. Go to the Integrations section
3. Click the "+ Explore & Add Repositories" button (bottom right)
4. Search for **Channels DVR**
5. Select **Install this repository**
6. Restart Home Assistant

### Manual

1. Copy [these files](https://github.com/zackwag/channels_dvr_upcoming_recordings) to `custom_components/channels_dvr_upcoming_recordings/`
2. Restart Home Assistant

---

## Configuration

1. If your Channels DVR installation is discovered via Zeroconf, you will get a notification and can configure the integration without specifying host and port. Otherwise, add the integration manually via Configuration → Integrations → Add Integration and search for **Channels DVR Upcoming Recordings**.
2. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
3. Add the card to your Lovelace UI either in `ui-lovelace.yaml` or via the UI. See the [Upcoming Media Card docs](https://github.com/custom-cards/upcoming-media-card) for details.

---

## Options

This integration is configured only via the UI (Configuration → Integrations). Options available on setup (host and port aren't needed if using Zeroconf):

| Key             | Default                                      | Required | Description                                                                                                 |
|-----------------|----------------------------------------------|----------|-------------------------------------------------------------------------------------------------------------|
| name            | Upcoming Recordings                          | No       | Name of the sensor entity.                                                                                   |
| host            | localhost                                   | Yes      | Host running Channels DVR (not required if discovered automatically).                                        |
| port            | 8089                                        | Yes      | Port Channels DVR listens on (not required if discovered automatically).                                     |
| max             | 5                                           | No       | Maximum number of upcoming recordings to show in the sensor.                                                |
| download_images | true                                        | No       | Set false to disable automatic downloading of show images.                                                  |
| img_dir         | '/upcoming-media-card-images/upcoming/'    | No       | Directory for storing downloaded images (must start and end with `/`).                                       |

**Note:** By default, images are downloaded to your `/www/` folder under the directory specified by `img_dir`. The directory is created if missing, and only images for upcoming shows are downloaded and cleaned up automatically.

---

## Sample Lovelace Card Configuration

```yaml
- type: custom:upcoming-media-card
  entity: sensor.upcoming_recordings
  title: Upcoming Recordings
```

### Card Content Defaults

| key   | default                      | example                                             |
| ----- | ---------------------------- | --------------------------------------------------- |
| title | $title                       | "The Walking Dead"                                  |
| line1 | $episode                     | "What Comes After"                                  |
| line2 | $day, $date $time            | "Monday, 10/31 10:00 PM" Displays time of download. |
| line3 | $number - $rating - $runtime | "S01E12 - ★ 9.8 - 01:30"                            |
| line4 | $genres                      | "Action, Adventure, Comedy"                         |
| icon  | mdi:eye-off                  | <https://materialdesignicons.com/icon/eye-off>      |

### Examples

TBD
