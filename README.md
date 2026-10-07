# Celery Man for Muse

Your desk requires a little more Tayne.

**Tayne, Celery Man, and Oyster as animated Muse companions on the M5Stack StickS3.** They dance while idle and react while Muse listens and speaks. Switch back to Muse's original pet any time.

| Tayne | Celery Man | Oyster |
| :---: | :---: | :---: |
| ![Tayne dancing](avatar/tayne/idle.gif) | ![Celery Man dancing](avatar/celery-man/idle.gif) | ![Oyster dancing](avatar/oyster/idle.gif) |
| Hat wobble included. | Business on top. Business everywhere. | Ready to entertain you. |

This is a fan-made character pack for the [Muse Gadget SDK](https://github.com/facebookincubator/muse-gadget-sdk), inspired by the [Celery Man sketch](https://www.youtube.com/watch?v=a8K6QUPmv8Q). It adds a character picker and a **Pet** shortcut that restores the default Muse avatar. Muse still handles voice, conversations, pairing, and connectivity.

## What works

- Three custom characters plus the original Muse pet; the choice is saved across restarts.
- Boot, idle, listening, thinking, speaking, happy, error, and shutdown animation.
- Listening and speaking poses respond to Muse's audio levels.
- A two-button menu on the StickS3; no touchscreen required.
- Sixteen 64×64 RGB565 frames per custom character: 384 KiB total sprite data and one shared 8 KiB custom render buffer. The original pet keeps its SDK renderer and buffers.

**Early hardware prototype:** the pack has been built and flashed to a real StickS3, connected to Muse, and restored a saved character after a restart. On-device menu tests confirm Pet restores the default avatar from all three dancers. Intermittent brownouts during Wi-Fi startup/USB resets remain unresolved. See [validation notes](docs/validation.md).

## Install into the Muse SDK

You need Git, Python 3, ESP-IDF **v6.0.1**, an M5Stack **StickS3**, and a USB data cable. A Muse account/app and your own SDK token are required for pairing; follow the [SDK setup instructions](https://github.com/facebookincubator/muse-gadget-sdk/blob/1b56662588c0ea00bdee24b9bcd1835e12848e9a/esp32/README.md).

Start with the SDK revision used to develop this pack:

```sh
git clone https://github.com/bruceblay/celery-man-muse.git
git clone https://github.com/facebookincubator/muse-gadget-sdk.git
git -C muse-gadget-sdk checkout 1b56662588c0ea00bdee24b9bcd1835e12848e9a
python3 celery-man-muse/tools/install.py muse-gadget-sdk
```

The installer checks compatibility, applies the two-file menu/build patch, and copies the runtime assets into the SDK's custom-avatar directory. It refuses to overwrite a different custom avatar. `--check` performs the checks without changing anything. Re-running an unchanged installation is safe. It also upgrades an unmodified first-release installation; locally edited avatar files are preserved and rejected rather than overwritten.

To update, pull this repo, run the installer again, then rebuild and flash. The default pet is compiled directly from the SDK's original renderer; its artwork is not copied into this repository.

The SDK deliberately ignores its custom-avatar directory in Git. Keep this repo as the source of the pack.

## Build and flash

Activate your ESP-IDF v6.0.1 environment, then run from `muse-gadget-sdk/esp32`:

```sh
idf.py -B build-muse-m5stack-sticks3 -DIDF_TARGET=esp32s3 \
  -DSDKCONFIG=build-muse-m5stack-sticks3/sdkconfig \
  '-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;devices/sdkconfig.muse;devices/sdkconfig.muse-m5stack-sticks3' menuconfig
```

Set your own SDK token in the ESP32 Device SDK settings, as described upstream. Then build:

```sh
idf.py -B build-muse-m5stack-sticks3 -DIDF_TARGET=esp32s3 \
  -DSDKCONFIG=build-muse-m5stack-sticks3/sdkconfig \
  '-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;devices/sdkconfig.muse;devices/sdkconfig.muse-m5stack-sticks3' build
```

Identify the attached board before flashing. For a StickS3 running Muse, `python tools/muse/chat.py --status` reports the board name. The SDK's port helper lists connected devices:

```sh
python tools/muse/ports.py --list
tools/muse/board.sh flash sticks3 YOUR_SERIAL_PORT
```

Replace `YOUR_SERIAL_PORT` with the identified StickS3 port. Flashing replaces its firmware. The normal flash layout preserves Wi-Fi/pairing storage; do not erase flash to install this pack. For a new device, complete pairing in the Muse app afterward.

No prebuilt firmware is published: build with your own SDK configuration. If a USB reset produces a brownout or an unresponsive console, a physical restart restored our test unit; the underlying issue still needs investigation.

## Controls

1. Press the **side button** to open the menu.
2. **Character** is the first entry. Press the **front button** to open it.
3. Use the side button to move through **Tayne → Celery Man → Oyster → Default pet → Back**.
4. Press the front button to choose. The menu closes and the character reacts.

**Pet**, the second menu entry, immediately restores Muse's original default pet and saves that choice. To return to a dancer, use **Character**. The first release incorrectly treated Pet as a petting action; this has been corrected.

## Develop without hardware

Run the renderer's sanitizer checks using Python 3, a C compiler, and the pinned SDK checkout:

```sh
python3 tools/verify.py --sdk ../muse-gadget-sdk
```

The SDK headers in `sdk-headers/` are unmodified snapshots from the pinned revision, used only for host verification and preview generation. Firmware builds use the SDK's own headers.

To regenerate sprites and GIFs, install [Pillow](https://pillow.readthedocs.io/) in a virtual environment (`python3 -m pip install -r requirements-art.txt`), then:

```sh
python3 avatar/tayne/pack_sprites.py
python3 avatar/pack_sprites.py celery-man
python3 avatar/pack_sprites.py oyster
python3 avatar/tayne/export_preview.py --character tayne
python3 avatar/tayne/export_preview.py --character celery-man
python3 avatar/tayne/export_preview.py --character oyster
```

The GIFs come from the actual C renderer. Preview audio levels are simulated. See [art sources and prompts](docs/art.md) for the original generated sheets.

## Credits and license

Inspired by Tim & Eric's Celery Man sketch and Paul Rudd's characters. An unofficial fan project, unaffiliated with or endorsed by the original creators, Adult Swim, Meta/Muse, or M5Stack.

Code is licensed under [Apache-2.0](LICENSE). Upstream SDK attribution is retained in [NOTICE](NOTICE). Character artwork is AI-generated fan art; the code license does not grant rights to third-party characters, likenesses, or trademarks. See [art provenance](docs/art.md).

Contributions welcome—especially reproducible hardware testing, animation improvements, and investigating the startup brownouts. Please omit credentials and personal device logs from public issues.
