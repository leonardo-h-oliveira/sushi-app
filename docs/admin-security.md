# Staff identities and sessions

Staff accounts and sessions are stored in PostgreSQL. Passwords are protected
with Python's standard-library scrypt, using an independent random salt and
N=32768, r=8, p=3. These parameters follow an OWASP minimum configuration:
[password storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#scrypt).
Implementation: [Python hashlib](https://docs.python.org/3/library/hashlib.html#hashlib.scrypt).

Sessions contain 32 random bytes encoded for transport. Only a SHA-256 digest is
stored in the database. They expire after eight hours. Logout revokes the stored
session immediately; resetting a password revokes every session for that user.
Inactive accounts and roles other than `admin` cannot access protected routes.
Old signed tokens are intentionally invalid after this migration.

## Production account setup

Apply migrations through `0009_admin_identity` in the intended environment, then
run from the repository root using that environment's Python installation:

```text
python backend/admin_account.py restaurant-owner
```

The command prompts for the new password twice without displaying it. Choose
12–200 characters. Do not pass passwords as arguments, paste them into issues or
commit them. Existing usernames are not silently overwritten.

To recover access or rotate a password:

```text
python backend/admin_account.py restaurant-owner --reset-password
```

The legacy environment username/password bootstrap is available only in
development/test, after a correct login and only for an absent account. Staging
and production always require an explicitly provisioned database account.
Environment password changes do not reset existing accounts.

## Browser and abuse controls

Deployed cookies use HttpOnly, Secure and SameSite=None for the separate frontend
and API hosts. Browser mutations with cookie authentication require an Origin
in the explicit CORS allowlist. Third-party cookie restrictions may still affect
cross-site deployments; verify the chosen production domains in real browsers.
Bearer authentication is available for controlled API clients. Do not store it
in browser local storage.

Five failed attempts lock the account for 15 minutes, persisted in the database.
The existing per-IP limiter also applies. Per-IP limits are process-local; a
multi-instance deployment must add an edge/shared limiter before approval.

Structured `staff_request` logs record user ID when authenticated, HTTP method,
route template and response status. They exclude passwords, tokens, request
bodies, customer names, telephone numbers and addresses. Configure retention and
access at the hosting provider before receiving real orders.

## Release checks

- Confirm an explicitly provisioned staff account can log in over HTTPS.
- Confirm anonymous requests and untrusted browser origins are rejected.
- Capture a test bearer token privately, log out, then confirm it receives 401.
- Confirm a password reset revokes earlier sessions.
- Confirm account lockout and cookie behavior on the actual production domains.
- Establish an owner responsible for account recovery and log access.

These checks remain part of #41 and the #14 release gate until production-like
acceptance is recorded.
