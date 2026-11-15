from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare import platform_base


class BaseResolutionTest(unittest.TestCase):
    def test_platform_child_is_resolved_from_the_current_debian_base_tag(self):
        reference = "ghcr.io/example/postgres:18-minimal-bookworm"
        index_digest = "sha256:" + "a" * 64
        amd64_digest = "sha256:" + "b" * 64
        arm64_digest = "sha256:" + "c" * 64
        manifests = {
            reference: {
                "digest": index_digest,
                "manifests": [
                    {
                        "digest": amd64_digest,
                        "platform": {"os": "linux", "architecture": "amd64"},
                    },
                    {
                        "digest": arm64_digest,
                        "platform": {"os": "linux", "architecture": "arm64"},
                    },
                ],
            }
        }

        self.assertEqual(
            platform_base(reference, "linux/arm64", manifests),
            (reference + "@" + arm64_digest, index_digest),
        )


if __name__ == "__main__":
    unittest.main()
