# Security policy

Report vulnerabilities privately through GitHub Security Advisories. Do not include secrets or personal data in issues.

The demo accepts only PDF, TXT and Markdown files, limits upload size, sanitizes filenames, checks content signatures and runs as an unprivileged container user. Uploaded documents are untrusted data: their text is never treated as instructions. For production, add authentication, per-tenant storage, malware scanning, rate limits, encrypted persistence and retention policies.

