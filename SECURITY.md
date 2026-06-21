# Security Policy

## Reporting a Vulnerability

Report security vulnerabilities via GitHub Security Advisories
(Security → Advisories → New draft advisory) or by email to the maintainer.

Do not open a public issue for security vulnerabilities.

## Credential Handling

- All credentials are supplied via environment variables. No secrets are stored on disk.
- `app_password_create` returns the generated password to the caller but never logs it.
- The server binds to `127.0.0.1` only — it is not exposed to the network.
- `config_set` can modify Nextcloud system configuration. Restrict access accordingly.
