from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from install import install, REVISION, RUNTIME

SDK = Path(os.environ.get('MUSE_TEST_SDK', ROOT.parent/'muse-gadget-sdk'))


@unittest.skipUnless((SDK/'.git').exists(), 'Set MUSE_TEST_SDK to a pinned SDK checkout')
class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='celery-install-test-')
        self.addCleanup(self.tmp.cleanup)
        self.sdk = Path(self.tmp.name)/'sdk'
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(SDK), str(self.sdk)], check=True)
        subprocess.run(['git', '-C', str(self.sdk), 'checkout', '--quiet', REVISION], check=True)

    def diff(self):
        return subprocess.check_output(['git', '-C', str(self.sdk), 'diff'])

    def test_clean_install_and_repeat(self):
        install(self.sdk, check=True)
        self.assertEqual(self.diff(), b'')
        install(self.sdk)
        first = self.diff()
        install(self.sdk)
        self.assertEqual(first, self.diff())
        subprocess.run(['git', '-C', str(self.sdk), 'diff', '--check'], check=True)

    def test_upgrade_previous_menu_versions(self):
        for version in ['v1', 'v2']:
            with self.subTest(version=version):
                subprocess.run(['git', '-C', str(self.sdk), 'restore', '.'], check=True)
                subprocess.run(['git', '-C', str(self.sdk), 'apply', str(ROOT/'patches'/f'{version}-character-menu.patch')], check=True)
                install(self.sdk, check=True)
                install(self.sdk)
                install(self.sdk)

    def test_user_avatar_is_preserved(self):
        avatar = self.sdk/'esp32/components/muse/avatar'
        avatar.mkdir()
        source = avatar/'muse_pixel.c'
        source.write_text('/* Local artwork */\n')
        with self.assertRaisesRegex(RuntimeError, 'differs'):
            install(self.sdk)
        self.assertEqual(source.read_text(), '/* Local artwork */\n')
        self.assertEqual(self.diff(), b'')

    def test_upgrade_previous_artwork(self):
        install(self.sdk)
        avatar = self.sdk/'esp32/components/muse/avatar'
        for revision in ('362e373', '5825a73', '33612ec', '76b5e7f', '17a575f', '26c3610', '3359df2'):
            with self.subTest(revision=revision):
                for name in RUNTIME:
                    previous = subprocess.check_output(['git', '-C', str(ROOT), 'show',
                        revision + ':avatar/' + name])
                    (avatar/name).write_bytes(previous)
                install(self.sdk, check=True)
                install(self.sdk)
                for name in RUNTIME:
                    self.assertEqual((avatar/name).read_bytes(), (ROOT/'avatar'/name).read_bytes())

    def test_modified_previous_artwork_is_preserved(self):
        install(self.sdk)
        source = self.sdk/'esp32/components/muse/avatar/muse_pixel.c'
        source.write_bytes(subprocess.check_output(['git', '-C', str(ROOT), 'show',
            '76b5e7f:avatar/muse_pixel.c']) + b'\n/* Local modification */\n')
        before = source.read_bytes()
        with self.assertRaisesRegex(RuntimeError, 'differs'):
            install(self.sdk)
        self.assertEqual(source.read_bytes(), before)

    def test_upgrade_keeps_unrelated_changes(self):
        subprocess.run(['git', '-C', str(self.sdk), 'apply', str(ROOT/'patches/v2-character-menu.patch')], check=True)
        avatar = self.sdk/'esp32/components/muse/avatar'
        for name in RUNTIME:
            target = avatar/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/'avatar'/name, target)
        unrelated = self.sdk/'README.md'
        unrelated.write_text('My local README\n')
        install(self.sdk)
        self.assertEqual(unrelated.read_text(), 'My local README\n')
