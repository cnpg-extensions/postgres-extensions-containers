# Security Policy

## Supported Versions

This project follows CloudNativePG's community support policy. For details,
please refer to the
[supported releases documentation](https://cloudnative-pg.io/docs/devel/supported_releases/).
The shared [CNPG version workflow](.github/workflows/cnpg-versions.yml)
selects the CloudNativePG versions used to test these extension images.

## Reporting a Vulnerability

**Please do not report vulnerabilities through public issues, discussions,
pull requests or Slack.** Report any potential security issues in this project
using GitHub's
[private vulnerability reporting form](https://github.com/cnpg-extensions/postgres-extensions-containers/security/advisories/new).
Include the affected extension(s), image tag(s) or digest(s), a description of
the impact, and steps to reproduce.

## Response Timeframes

These are targets for a volunteer-maintained project. We will tell the reporter
if we expect to miss one.

- **Acknowledgement:** within 10 business days of the report.
- **Initial assessment:** within 4 weeks, confirming whether it is a
  vulnerability and its severity.
- **Closure:** within 6 months, with updated images made available for
  [supported versions](#supported-versions) and a GitHub security advisory
  published (with a CVE where appropriate).

Details stay private until a fix is available, and the disclosure date is
coordinated with the reporter, who is credited unless they prefer otherwise.

Past advisories are listed on the
[security advisories page](https://github.com/cnpg-extensions/postgres-extensions-containers/security/advisories).
