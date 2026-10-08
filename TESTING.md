# Testing and known issues

Checked on 2026-10-08 with ESP-IDF v6.0.1 and Muse SDK revision `1b56662588c0ea00bdee24b9bcd1835e12848e9a`.

## Firmware builds

All six profiles were rebuilt on 2026-10-08 with the Oyster video update, so every board carries the same animations. These builds used the development SDK checkout, which also has unrelated voice-session edits.

| Profile | Result | App partition free | Physical device |
| --- | --- | --- | --- |
| StickS3 | Passed | 5% | Tested |
| StickC Plus2 | Passed | 6% | Not tested |
| AIPI Lite | Passed | 8% | Not tested |
| SenseCAP Watcher | Passed | 6% | Not tested |
| Waveshare S3 1.75C | Passed | 8% | Not tested |
| Waveshare C6 1.8 | Passed | 1% | Not tested |

The Waveshare C6 has about 60 KiB of app space left. More frames for any character will likely need smaller sprites or a larger partition on that board.

A successful build does not verify touch input, audio, power use, or frame rate on that board. Touchscreen character selection still needs physical-device testing.

## Automated checks

- Four avatars, seven Muse modes, and fourteen output sizes under AddressSanitizer and UBSan.
- Complete custom-character animation cycles, including Tayne's 1.6-second video loops. Every idle, listening, and thinking frame must match its packed source frame, in order, at exact 15 fps boundaries.
- Tayne's speech sequence follows its source frames even with zero or low audio-level input, restarts on re-entry to speaking mode, and returns to idle when that mode ends. Microphone levels do not interrupt the listening dance; thinking dots remain below the boots.
- Tayne matches the prior renderer across 1,680 sampled poses.
- Oyster's idle, listening, speaking, and thinking loops follow the packed source frames, including the printout's held smile, and happy returns to idle.
- Celery Man’s three video loops follow the approved source frames across idle, listening, thinking, speaking, and happy. Checks cover repeated loops, zero audio level, state re-entry, and return from happy to idle.
- Partial display strips match full-frame output; buffer guards remain intact.
- Default pet output matches the original SDK renderer, including after switching from each dancer.
- Clean and repeated installation; upgrades from both earlier integration patches; refusal to overwrite custom artwork; preservation of unrelated edits.
- Upgrade from the previous dance artwork, with changed local artwork still protected.
- Board profiles use their own chip target, configuration, and SDK flash helper.
- Preview GIF export at 96×96 using the native renderer's scaling.
- SDK host suite: 143 tests, 140 passed, 3 skipped on the development checkout.

The speaking-freeze regression fails against the previous renderer: zero audio-level input holds one frame there. The corrected renderer advances through all twelve speech frames at zero, low, and normal levels. Its StickS3 firmware build passed and was flashed with hash verification.

GitHub Actions runs the renderer, profile, and installer tests on each push. Full firmware builds are currently checked locally.

## StickS3 hardware checks

The default-pet release was flashed with written-data verification. The board connected to Muse, and menu tests selected each dancer and restored Default pet from each one. Selection writes completed successfully. Saved-character restoration was also confirmed after an earlier restart.

The earlier Tayne video update was tested on the attached StickS3. Flashing preserved its existing device configuration, pairing, and local voice-session fixes. The new touchscreen integration does not change its button menu.

Tayne's video update was flashed with written-data hash verification. The boot log loaded Tayne and reached Muse startup without a panic or reboot loop during the check. The board reported its pairing intact and its Muse link online. It continued responding after console-driven listening, thinking, speaking, happy, and idle states, and was left idle. Physical animation appearance and timing, and speech driven by real audio, still need visual and listening checks.

Celery Man’s video update was flashed on 2026-10-08 with written-data hash verification. The app uses `0x361000` bytes of the `0x3e0000`-byte partition (13% free). The board booted with Celery Man selected and reached Muse startup without a panic, brownout, or reboot loop during the 12-second boot check. Device configuration and local voice-session fixes were preserved. The board responded after listening, thinking, speaking, happy, and idle commands, and was left idle. Physical animation appearance and real-audio behavior still need a user check.

Oyster's video update was flashed on 2026-10-08 with written-data hash verification. The app uses `0x3b1000` bytes of the `0x3e0000`-byte partition (5% free). Oyster's animations were reviewed visually on the device.

## Known issues

Intermittent brownouts can occur during Wi-Fi startup or a USB-driven reset. The console may stop responding afterward. A physical restart restored the test unit; on another occasion it recovered by itself. The cause remains unresolved, and power protections remain enabled.

Long-term stability, real spoken-audio testing, and physical frame timing remain unverified. Please remove credentials and personal device details before sharing logs in an issue.
