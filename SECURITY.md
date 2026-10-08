# Security

If you find a vulnerability in Wren iOS, email Munzzyy1@proton.me. Do not open a public issue for it.

You can expect a reply within 7 days, a verdict within about 14 days of that, and a fix or a clear mitigation within 90 days, sooner for anything that exposes messages. These are targets, not a service level; I am one person. Credit goes in the release notes under the name you pick, and there is no bounty. The Android repo's SECURITY.md spells out the same policy in full and it applies here as written. Problems in the Signal protocol or Signal's servers should go to Signal (security@signal.org). Bugs in inherited Signal-iOS code get reported upstream too.

Wren iOS builds are unsigned and come from GitHub Actions. Check the SHA-256 that comes with the IPA before you sideload it. Signal clients expire about 90 days after their build date, so keep the app updated.
