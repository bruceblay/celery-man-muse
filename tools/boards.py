"""Muse full-UI profiles from the pinned SDK's devices/ overlays and muse_ui.c."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Board:
    name: str
    profile: str
    target: str
    width: int
    height: int
    avatar: int
    touch: bool
    round: bool = False


BOARDS = {
    'sticks3': Board('M5Stack StickS3', 'm5stack-sticks3', 'esp32s3', 135, 240, 128, False),
    'plus2': Board('M5Stack StickC Plus2', 'm5stack-stickc-plus2', 'esp32', 135, 240, 128, False),
    'aipi': Board('AIPI Lite', 'aipi', 'esp32s3', 128, 128, 96, False),
    'watcher': Board('SenseCAP Watcher', 'sensecap-watcher', 'esp32s3', 412, 412, 256, True, True),
    's3': Board('Waveshare S3 1.75C', 'waveshare-s3-175c', 'esp32s3', 466, 466, 320, True, True),
    'c6': Board('Waveshare C6 1.8', 'waveshare-c6-18', 'esp32c6', 368, 448, 320, True),
}
