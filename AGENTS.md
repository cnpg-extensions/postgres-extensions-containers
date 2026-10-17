# Testing philosophy

Prioritize tests for realistic mistakes that could pass the build while producing
incorrect or incomplete results, especially package inventory, ownership, licenses,
and downstream hook output. Avoid duplicating failures that the build already
reports with a debuggable error, or testing third-party validators themselves.
Keep build-time validation and end-to-end integration checks.
