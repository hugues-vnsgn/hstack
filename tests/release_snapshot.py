"""Frozen 0.1.0 fixture; never counts as validation of development guidance."""
import atexit
import hashlib
from pathlib import Path
import tarfile
import tempfile

_snapshot = None

def release_root():
    global _snapshot
    if _snapshot is None:
        archive = Path(__file__).parent / 'fixtures/release-0.1.0.tar.gz'
        if hashlib.sha256(archive.read_bytes()).hexdigest() != "21c1b70aa1814baf2ceb521695c6ad784746fdd0f60fd7633e1858cbe1d6df00":
            raise ValueError('frozen release fixture changed')
        _snapshot = tempfile.TemporaryDirectory(prefix='huguesstack-release-contracts-')
        atexit.register(_snapshot.cleanup)
        with tarfile.open(archive) as stream:
            # Older 3.9 stdlibs lack extraction filters; the exact archive is hash-bound above.
            stream.extractall(_snapshot.name, **({'filter': 'data'} if hasattr(tarfile, 'data_filter') else {}))
    return Path(_snapshot.name)
