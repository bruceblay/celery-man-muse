from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from boards import BOARDS
from build import command


class BoardTests(unittest.TestCase):
    def test_upstream_avatar_layout(self):
        for name, board in BOARDS.items():
            with self.subTest(board=name):
                small = board.height < 200 or board.width < 200
                size = board.height*3//4 if small else 320
                if size > board.width:
                    size = board.width//64*64
                dy = int((board.height-466)/2)
                if not small and board.round and dy < 0:
                    size = (320+2*dy)//64*64
                self.assertEqual(board.avatar, size)
                self.assertLessEqual(size, min(board.width, board.height))

    def test_build_uses_each_boards_target_and_overlay(self):
        for alias, board in BOARDS.items():
            cmd = command(alias, 'build')
            self.assertIn(f'-DIDF_TARGET={board.target}', cmd)
            self.assertIn(f'-DSDKCONFIG=build-muse-{board.profile}/sdkconfig', cmd)
            self.assertTrue(any(s.endswith('devices/sdkconfig.muse-'+board.profile) for s in cmd))
            self.assertEqual(cmd[-1], 'build')

    def test_flash_preserves_sdk_special_uploaders(self):
        for alias in BOARDS:
            self.assertEqual(command(alias, 'flash', '/dev/test'),
                             ['bash', 'tools/muse/board.sh', 'flash', alias, '/dev/test'])
            with self.assertRaises(ValueError):
                command(alias, 'flash')

    def test_configure_opens_menuconfig(self):
        self.assertEqual(command('sticks3', 'configure')[-1], 'menuconfig')
