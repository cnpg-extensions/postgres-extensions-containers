"""Read back published tags without accepting a different index digest."""
import hashlib
import subprocess
import time


def wait_for_index_digest(reference, expected_digest, attempts=6):
    """Allow registry tag visibility to catch up after a successful push."""
    for attempt in range(attempts):
        try:
            raw = subprocess.check_output(['docker', 'buildx', 'imagetools', 'inspect', reference, '--raw'])
        except subprocess.CalledProcessError:
            if attempt == attempts - 1:
                raise
        else:
            actual = 'sha256:' + hashlib.sha256(raw).hexdigest()
            if actual == expected_digest:
                return
            if attempt == attempts - 1:
                raise ValueError(f'registry index digest mismatch for {reference}: '
                                 f'expected {expected_digest}, got {actual}')
        time.sleep(2)
