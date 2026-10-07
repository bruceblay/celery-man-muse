# Install and update

You need Git, Python 3, ESP-IDF **v6.0.1**, a [compatible device](DEVICES.md), and a USB data cable. Follow the [Muse SDK setup guide](https://github.com/facebookincubator/muse-gadget-sdk/blob/1b56662588c0ea00bdee24b9bcd1835e12848e9a/esp32/README.md) for your account, SDK token, and phone pairing.

## Get the source

```sh
git clone https://github.com/bruceblay/celery-man-muse.git
git clone https://github.com/facebookincubator/muse-gadget-sdk.git
git -C muse-gadget-sdk checkout 1b56662588c0ea00bdee24b9bcd1835e12848e9a
cd celery-man-muse
python3 tools/install.py ../muse-gadget-sdk
```

The installer preserves unrelated SDK edits and refuses to replace a different custom avatar. Add `--check` to inspect compatibility without changing files.

## Configure and build

Activate your ESP-IDF v6.0.1 environment first. Pick your board from `python3 tools/build.py --list`. For a StickS3:

```sh
python3 tools/build.py sticks3 configure
python3 tools/build.py sticks3 build
```

In configuration, enter your own SDK token under the ESP32 Device SDK settings. The helper uses the sibling `muse-gadget-sdk` checkout by default; pass `--sdk /path/to/muse-gadget-sdk` to use another one. Each board gets its own build directory. When developing for several boards, use a separate SDK checkout per board so their managed dependencies stay separate.

## Flash

Identify the attached device before writing firmware. A board already running Muse reports its name with `python tools/muse/chat.py --status` from the SDK's `esp32` directory. `python tools/muse/ports.py --list` lists ports.

From this repository, replace `YOUR_SERIAL_PORT` with the port of that board:

```sh
python3 tools/build.py sticks3 flash --port YOUR_SERIAL_PORT
```

The helper uses the SDK's board-specific uploader, including its special handling for the Watcher and StickC Plus2. It replaces firmware while preserving pairing storage; do not erase flash to install this pack. New devices still need pairing in the Muse app.

For a factory-fresh board, read the SDK's [device notes](https://github.com/facebookincubator/muse-gadget-sdk/blob/1b56662588c0ea00bdee24b9bcd1835e12848e9a/esp32/devices/README.md) first. StickS3's factory firmware needs a special USB setup step; Watcher has factory data to back up.

## Update

```sh
git pull
python3 tools/install.py ../muse-gadget-sdk
python3 tools/build.py sticks3 build
python3 tools/build.py sticks3 flash --port YOUR_SERIAL_PORT
```

Unmodified earlier versions of this pack upgrade automatically. If the installer finds your own avatar edits, back them up and reconcile them before continuing. The SDK ignores its custom-avatar directory in Git, so keep this repository as your source copy.

Firmware binaries are built locally with your configuration; none are published here. For startup trouble, see [TESTING.md](TESTING.md).
