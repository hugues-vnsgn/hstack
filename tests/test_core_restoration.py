"""Historical 0.2.0 restoration contract suite, never current-layout evidence."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

class HistoricalRestoration(unittest.TestCase):
    def test_frozen_0_2_0_restoration_contracts(self):
        archive = Path(__file__).parent / 'fixtures/release-0.2.0.tar.gz'
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), '8b6afedc7dc188d6d0bf85262b208707f5cbb4d15b2317c68925750d36904f5b')
        with tempfile.TemporaryDirectory(prefix='hstack-release02-') as folder:
            with tarfile.open(archive) as stream:
                # Older 3.9 stdlibs lack extraction filters; the exact archive is hash-bound above.
                stream.extractall(folder, **({'filter': 'data'} if hasattr(tarfile, 'data_filter') else {}))
            result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                                     '-p', 'test_core_restoration.py', '-v'],
                                    cwd=folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Ran 50 tests', result.stderr)
            # A bare OK summary: skipped nested cases must not count as passed contracts.
            self.assertRegex(result.stderr, r'\nOK\n*\Z')
