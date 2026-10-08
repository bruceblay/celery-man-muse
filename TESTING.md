# Testing and known issues

Checked on 2026-10-07 with ESP-IDF v6.0.1 and Muse SDK revision `1b56662588c0ea00bdee24b9bcd1835e12848e9a`.

## Firmware builds

Each profile is built in a separate, clean SDK checkout. These builds contain the published pack and integration patch, without the unrelated voice-session edits in the original development checkout.

| Profile | Result | Physical device |
| --- | --- | --- |
| StickS3 | Passed | Tested |
| StickC Plus2 | Passed | Not tested |
| AIPI Lite | Passed | Not tested |
| SenseCAP Watcher | Passed | Not tested |
| Waveshare S3 1.75C | Passed | Not tested |
| Waveshare C6 1.8 | Passed | Not tested |

A successful build does not verify touch input, audio, power use, or frame rate on that board. Touchscreen character selection still needs physical-device testing.

## Automated checks

- Four avatars, seven Muse modes, and fourteen output sizes under AddressSanitizer and UBSan.
- Complete custom-character animation cycles, including Tayne's 1.6-second video loops. Every idle, listening, and thinking frame must match its packed source frame, in order, at exact 15 fps boundaries.
- Tayne's speech sequence follows its source frames even with zero or low audio-level input, restarts on re-entry to speaking mode, and returns to idle when that mode ends. Microphone levels do not interrupt the listening dance; thinking dots remain below the boots.
- Approved idle/happy sprite sheets and GIFs are unchanged by the conversation-state update. Celery Man and Oyster render identically to the previous version across 840 sampled poses.
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

The attached StickS3 now runs the approved Tayne video update. Flashing preserved its existing device configuration, pairing, and local voice-session fixes. The new touchscreen integration does not change its button menu.

Tayne's video update was flashed with written-data hash verification. The boot log loaded Tayne and reached Muse startup without a panic or reboot loop during the check. The board reported its pairing intact and its Muse link online. It continued responding after console-driven listening, thinking, speaking, happy, and idle states, and was left idle. Physical animation appearance and timing, and speech driven by real audio, still need visual and listening checks.

## Known issues

Intermittent brownouts can occur during Wi-Fi startup or a USB-driven reset. The console may stop responding afterward. A physical restart restored the test unit; on another occasion it recovered by itself. The cause remains unresolved, and power protections remain enabled.

Long-term stability, real spoken-audio testing, and physical frame timing remain unverified. Please remove credentials and personal device details before sharing logs in an issue.
