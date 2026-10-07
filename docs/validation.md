# Validation and known issues

Recorded 2026-10-07 against Muse Gadget SDK commit
`1b56662588c0ea00bdee24b9bcd1835e12848e9a`, ESP-IDF v6.0.1, M5Stack StickS3.

## Completed

- StickS3 firmware build passed: application size `0x271000`, 37% app-slot space free.
- SDK host suite: 143 tests run, 140 passed, 3 skipped.
- AddressSanitizer/UBSan renderer checks: three distinct characters, invalid
  selections rejected, all seven Muse modes, and six output sizes. Partial
  strips matched full frames and buffer guards remained intact. Happy poses
  were included; this is not exhaustive animation or persistence testing.
- Browser previews: character selection, Pet, pause, and state selection.
- Flash completed with esptool's written-data hash verification.
- Device identified itself as M5Stack StickS3 and initialized its 135×240 UI.
- After a physical restart, device status reported Muse Connected and Link Online.
- Subsequent restart logs loaded the saved Celery Man selection, confirming
  saved-choice restoration on that device.

The local firmware build also included pre-existing voice-session edits
unrelated to this pack. Those edits are not distributed here. The published
package contains only the avatar renderer, assets, and menu/build integration.
The original firmware validation is therefore not a claim that a clean
upstream build has had identical end-to-end device testing.

## Still open

Intermittent brownouts occur during Wi-Fi startup or after a USB-driven reset.
The console can then stop responding. A physical restart restored the test
unit. Brownouts were also observed before the original Tayne-only firmware,
but their cause has not been established. No power protections were disabled.

Real spoken-audio testing, prolonged stability,
and physical frame timing remain unverified. This is an early prototype,
not a production-ready hardware release.

Raw device logs, configuration, firmware binaries, identifiers, and pairing
material are intentionally excluded from this public repository.

## Public package checks

The installer was exercised against a clean checkout of the pinned SDK:
check-only left it unchanged, conflicting custom artwork was preserved and
rejected, installation succeeded, and a second installation made no changes.
The installed renderer passed the same sanitizer checks against the SDK's
real headers. The bundled host headers matched upstream byte for byte.
GitHub Actions repeats renderer verification and clean/repeated installation.

## Default-pet correction

Pet now selects the original Muse avatar rather than triggering a short happy
animation. Default pet is also the fourth Character entry. It uses the SDK's
original renderer, with the saved ID `muse`; existing dancer IDs are unchanged.

Host sanitizer checks cover four distinct avatars and pixel-for-pixel default
renderer routing across all seven modes and six output sizes, plus switching
back from every dancer. The installer was checked for safe upgrades from the
first release, refusal to overwrite local edits, and repeated installation.

The corrected StickS3 build and SDK host suite passed, and esptool verified
the flash. One startup brownout occurred; the board then recovered and
established its Muse session. On-device serial menu tests selected each of
Tayne, Celery Man and Oyster and used Pet to return to Default pet each time.
The selection log is emitted only after the NVS commit succeeds. Final status
reported Muse Connected and Link Online, with Default pet left selected.
No additional USB reset was sent for a persistence check of this revision.
