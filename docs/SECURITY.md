# Security & Keys

- Keys are provided by the **user** via environment variables.
- Keys are never logged or stored in artifacts.
- MLflow artifacts must not include secrets.
- Rendered page images may contain sensitive data — warn users to handle artifacts securely.
- Add a `--redact-artifacts` option later if needed.

## Vulnerability Reporting

Please report vulnerabilities privately via GitHub Security Advisories or email the maintainers. Do not open a public issue for security-sensitive reports.

## Data Handling

- Use ephemeral temp directories for rendered images and intermediate JSON.
- Avoid uploading sensitive documents to third-party providers if policies prohibit it.
- Provide a `--save-intermediate` flag to explicitly persist intermediates; otherwise delete on completion.
