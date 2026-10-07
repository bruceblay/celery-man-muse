# Devices and screen sizes

The pack uses the display drivers and layout already provided by the pinned [Muse SDK](https://github.com/facebookincubator/muse-gadget-sdk/blob/1b56662588c0ea00bdee24b9bcd1835e12848e9a/esp32/devices/README.md).

| Device | Build name | Display | Avatar area | Controls | Hardware tested |
| --- | --- | --- | --- | --- | --- |
| M5Stack StickS3 | `sticks3` | 135×240 | 128×128 | Buttons | Yes |
| M5Stack StickC Plus2 | `plus2` | 135×240 | 128×128 | Buttons | No |
| AIPI Lite | `aipi` | 128×128 | 96×96 | Buttons | No |
| SenseCAP Watcher | `watcher` | 412×412, round | 256×256 | Touchscreen | No |
| Waveshare ESP32-S3-Touch-AMOLED-1.75C | `s3` | 466×466, round | 320×320 | Touchscreen | No |
| Waveshare ESP32-C6-Touch-AMOLED-1.8 | `c6` | 368×448 | 320×320 | Touchscreen | No |

All six have build profiles and a character picker. Firmware build results are recorded in [TESTING.md](TESTING.md). Only StickS3 has been checked on a physical device.

## Controls

Button boards use their existing menu and select buttons. On touchscreen boards, swipe to Settings and open **Character**, then tap a name. **Pet** restores the default avatar on both interfaces. Touching a character on the main screen retains Muse's normal happy reaction.

## Scaling

The table lists the normal avatar area, not the full panel. Muse leaves space for captions and controls, and keeps art away from the edges of round displays. Some UI states resize the avatar further.

The same 64×64 sprites scale to each square area with nearest-neighbor sampling. The renderer supports sizes from 1 to 512 pixels, including sizes between whole multiples of 64. Scaling keeps the character's proportions; it does not generate new detail. No separate sprite pack is needed per board.

Tests cover native avatar sizes, panel widths, and intermediate sizes. Use the [preview exporter](DEVELOPMENT.md#artwork-and-previews) to inspect a particular size.

## Hardware differences

The C6 board has no PSRAM: upstream Muse uses voice notes with text replies and does not support image display. The StickC Plus2 has a buzzer rather than the StickS3's speaker. The character pack inherits these limits.

Devices with only a status screen, an LED ring, or e-paper do not use this avatar interface. Supporting them requires a separate UI or SDK port. New boards should first work with Muse's original pet before adding this pack.
