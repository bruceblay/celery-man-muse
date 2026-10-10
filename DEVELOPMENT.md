# Development

## How it fits into Muse

`avatar/muse_pixel.c` implements Muse's existing render interface. Tayne has eighty-two 64×64 RGB565 frames; Celery Man has seventy-two and Oyster has fifty-four. Together they use 1,664 KiB of flash and share one 8 KiB render buffer. The default pet uses the SDK's original renderer and its own buffers.

Tayne's idle and happy dances each use twenty-four consecutive video samples at 15 fps, for 1.6-second loops. Frame order and timing follow the sketch. Listening uses a twelve-frame arm swing; thinking uses ten frames of raised-arm kicks. Speaking uses a filmed close-up. [ART.md](ART.md) records the source timestamps and extraction recipe.

Speaking loops the twelve-frame greeting at 15 fps while Muse is in speaking mode. It uses time in that mode rather than the audio meter, which can be zero or stale. It returns to the normal dance when Muse leaves speaking mode. Thinking dots sit below the dancer. Boot plays the Flarhgunnstow dance as the screen fades in. Error and off reuse the neutral portrait.

Celery Man uses three twenty-four-frame video loops at 15 fps. Hip sway serves idle and thinking, raised-fist shuffle serves listening and speaking, and 4d3d3 serves happy. Thinking dots sit below his feet. Speech keeps moving at zero audio level. Boot plays the hip sway as the screen fades in. Error and off reuse the first hip-sway frame.

Oyster uses four video loops at 15 fps. Headbang serves idle, arms back serves listening, and the greeting serves speaking and happy. Thinking plays the 28-frame printout, holds the final smile for 0.6 seconds, and repeats. Boot runs the printout as the screen fades in. Error and off reuse a greeting frame.

The SDK chooses the square avatar area for each screen. The renderer scales into that area without stretching the character, and writes display strips rather than allocating a full-screen image. Larger screens keep the same pixel-art style. See [DEVICES.md](DEVICES.md) for native sizes.

The integration patch adds character selection to both the button menu and touchscreen settings. Both use the same saved IDs: `tayne`, `celery-man`, `oyster`, and `muse`. Selection happens on the UI task. Keep these IDs stable when adding characters.

The default-avatar adapter compiles the original renderer directly from the SDK checkout. Its source and artwork are not copied into this repo.

## Verify changes

With the [pinned SDK](INSTALL.md) checked out:

```sh
python3 tools/verify.py --sdk ../muse-gadget-sdk
python3 -m unittest discover -s tests
```

Renderer checks use AddressSanitizer and UBSan, compare full frames with clipped strips, and check that choosing Default pet routes to the original renderer. The headers in `sdk-headers/` are unmodified SDK snapshots for host tests; firmware builds use the SDK's headers.

Build a changed board with `tools/build.py`. Only flash a device whose identity you have verified. Hardware results and gaps belong in [TESTING.md](TESTING.md).

## Artwork and previews

Install Pillow in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-art.txt
```

Rebuild sprite headers from the [source sheets](ART.md):

```sh
python3 avatar/tayne/pack_sprites.py
python3 avatar/celery-man/pack_sprites.py
python3 avatar/pack_sprites.py oyster
```

Export animations from the C renderer:

```sh
python3 avatar/tayne/export_preview.py --character tayne
python3 avatar/tayne/export_preview.py --character oyster --size 128 --output /tmp/oyster-preview
```

`--size` accepts 1–512 pixels and defaults to 320. State atlases stay at 64×64; GIFs use the requested output size. `--sdk` selects the SDK checkout. Preview audio levels are simulated.

Tayne exports GIFs for speaking, listening, and thinking as well as the two dances. The speaking preview shows the same continuous sequence used on the device.

### README device previews

```sh
python3 tools/export_device_previews.py --sdk ../muse-gadget-sdk
```

This rebuilds the six animated display mockups and still previews in `docs/devices/`. Avatar pixels come from the current C renderer at each board’s native avatar size. The display framing and status text are illustrative, not hardware screenshots. The script reads board dimensions from `tools/boards.py` and cycles through all three characters, including Oyster’s printout.

## Adding boards

This pack supports boards that already have Muse's full avatar UI. To expose another such board, add its profile to `tools/boards.py`, verify its overlay and dimensions against the SDK, and add its native render size to the tests. Build it before recording build support; test the physical screen and inputs before recording hardware support.

A new display driver, e-paper support, or an entirely different device platform requires an SDK port. Those changes do not belong in the sprite scaler.

Keep credentials, device logs, generated firmware, and personal identifiers out of commits and public issues.
