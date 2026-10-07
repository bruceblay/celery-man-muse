# Development

## How it fits into Muse

`avatar/muse_pixel.c` implements Muse's existing render interface. Each dancer has sixteen 64×64 RGB565 frames. Together they use 384 KiB of flash and share one 8 KiB render buffer. The default pet uses the SDK's original renderer and its own buffers.

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
python3 avatar/pack_sprites.py celery-man
python3 avatar/pack_sprites.py oyster
```

Export animations from the C renderer:

```sh
python3 avatar/tayne/export_preview.py --character tayne
python3 avatar/tayne/export_preview.py --character oyster --size 128 --output /tmp/oyster-preview
```

`--size` accepts 1–512 pixels and defaults to 320. State atlases stay at 64×64; GIFs use the requested output size. `--sdk` selects the SDK checkout. Preview audio levels are simulated.

## Adding boards

This pack supports boards that already have Muse's full avatar UI. To expose another such board, add its profile to `tools/boards.py`, verify its overlay and dimensions against the SDK, and add its native render size to the tests. Build it before recording build support; test the physical screen and inputs before recording hardware support.

A new display driver, e-paper support, or an entirely different device platform requires an SDK port. Those changes do not belong in the sprite scaler.

Keep credentials, device logs, generated firmware, and personal identifiers out of commits and public issues.
