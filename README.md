# Celery Man for Muse

Your desk requires a little more Tayne.

Tayne, Celery Man, and Oyster as animated companions for [Muse](https://github.com/facebookincubator/muse-gadget-sdk). They dance while idle and react while Muse listens and speaks.

Tayne's dances use frames from the sketch, including the low bounce and Flarhgunnstow sequence.
He swings his arms while listening, kicks with his arms raised while thinking, and switches to the sketch's close-up while speaking.

Celery Man uses three dances from the sketch: hip sway while idle, raised-fist shuffle while listening and speaking, and 4d3d3 when happy. Thinking adds dots below his feet.

Oyster also comes straight from the footage. He headbangs while idle, swings his arms back while listening, waves while speaking and when happy, and prints out his own smiling portrait while thinking.

| Tayne | Celery Man | Oyster |
| :---: | :---: | :---: |
| ![Tayne dancing](avatar/tayne/idle.gif) | ![Celery Man dancing](avatar/celery-man/idle.gif) | ![Oyster dancing](avatar/oyster/idle.gif) |

## Tayne’s moves

| Low bounce | Arm swing | Raised-arm kicks | Close-up | Flarhgunnstow |
| :---: | :---: | :---: | :---: | :---: |
| ![Low bounce](avatar/tayne/idle.gif) | ![Arm swing](avatar/tayne/listening.gif) | ![Raised-arm kicks](avatar/tayne/thinking.gif) | ![Close-up](avatar/tayne/speaking.gif) | ![Flarhgunnstow](avatar/tayne/happy.gif) |
| Idle | Listening | Thinking | Speaking | Happy |

## Celery Man’s moves

| Hip sway | Raised-fist shuffle | 4d3d3 |
| :---: | :---: | :---: |
| ![Hip sway](avatar/celery-man/idle.gif) | ![Raised-fist shuffle](avatar/celery-man/speaking.gif) | ![4d3d3](avatar/celery-man/happy.gif) |
| Idle; thinking adds dots | Listening and speaking | Happy |

## Oyster’s moves

| Headbang | Arms back | Greeting | Printout |
| :---: | :---: | :---: | :---: |
| ![Headbang](avatar/oyster/idle.gif) | ![Arms back](avatar/oyster/listening.gif) | ![Greeting](avatar/oyster/speaking.gif) | ![Printout](avatar/oyster/thinking.gif) |
| Idle | Listening | Speaking and happy | Thinking |

## Supported devices

Animated display mockups cycle through Tayne, Celery Man, and Oyster, including the printout. Screen proportions and avatar sizes follow Muse’s layouts; cases are simplified and not shown to physical scale.

| M5Stack StickS3 | M5Stack StickC Plus2 | AIPI Lite |
| :---: | :---: | :---: |
| ![Tayne, Celery Man, and Oyster on the StickS3 display](docs/devices/sticks3.gif) | ![Tayne, Celery Man, and Oyster on the StickC Plus2 display](docs/devices/plus2.gif) | ![Tayne, Celery Man, and Oyster on the AIPI Lite display](docs/devices/aipi.gif) |
| 135×240 · Buttons | 135×240 · Buttons | 128×128 · Buttons |

| SenseCAP Watcher | Waveshare S3 1.75C | Waveshare C6 1.8 |
| :---: | :---: | :---: |
| ![Tayne, Celery Man, and Oyster on the round SenseCAP Watcher display](docs/devices/watcher.gif) | ![Tayne, Celery Man, and Oyster on the round Waveshare S3 1.75C display](docs/devices/s3.gif) | ![Tayne, Celery Man, and Oyster on the Waveshare C6 1.8 display](docs/devices/c6.gif) |
| 412×412 · Round touchscreen | 466×466 · Round touchscreen | 368×448 · Touchscreen |

All six have build profiles and character selection. Only StickS3 has been tested on hardware. See [devices and screen sizes](DEVICES.md) and [build results](TESTING.md).

## Get started

You'll need a compatible device, a USB data cable, and a Muse account. Start with the [installation guide](INSTALL.md) to build and flash the firmware.

## Choose a character

**Buttons:** open the menu with the side/menu button, choose **Character** with the front/select button, then select a character. Your choice is saved.

**Touchscreens:** swipe to Settings, open **Character**, and tap a name.

**Pet** restores Muse's original avatar. It is also available as **Default pet** in the character list.

Muse still handles conversations, voice, and pairing. This pack changes the character on screen.

## A few things to know

This is an early project. We’re still investigating intermittent power-related resets on the StickS3. A physical restart has recovered our test device. Details and test results are in [TESTING.md](TESTING.md).

Want to change the art or add a device? See [DEVELOPMENT.md](DEVELOPMENT.md). [ART.md](ART.md) records where every animation comes from in the sketch.

Inspired by [Tim & Eric's Celery Man sketch](https://www.youtube.com/watch?v=a8K6QUPmv8Q). An unofficial fan project. Code is [Apache-2.0](LICENSE); that license does not grant rights to the original characters, likenesses, or trademarks. See [credits](NOTICE).
