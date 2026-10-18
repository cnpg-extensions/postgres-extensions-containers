# Project priority: track upstream

Tracking the CloudNativePG upstream project is a high-priority goal. Preserve
upstream alignment and keep intentional downstream differences explicit.
Choices inherited from upstream do not need separate justification or entries
in the local workaround register; this includes the inherited OpenTelemetry
dependency overrides.

# Commit trailers

Every commit must include a DCO `Signed-off-by` trailer (`git commit -s`).
AI-assisted commits must also include an `Assisted-By` trailer naming the
assistant and model, for example `Assisted-By: OpenAI Codex (GPT-6.1-Sol)`.

# Testing philosophy

Prioritize tests for realistic mistakes that could pass the build while producing
incorrect or incomplete results, especially package inventory, ownership, licenses,
and downstream hook output. Avoid duplicating failures that the build already
reports with a debuggable error, or testing third-party validators themselves.
Keep build-time validation and end-to-end integration checks.
