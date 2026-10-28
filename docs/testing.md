# Release acceptance tests

From the repository root, install backend development dependencies in the virtual
environment and frontend dependencies from the committed lockfile. On Windows:

```powershell
backend\.venv\Scripts\Activate.ps1
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend exec playwright install chromium
python -m pytest
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend build
pnpm --dir frontend e2e
```

End-to-end tests start their own API and frontend on ports 8000/3000. Stop local
development servers first; the suite refuses to reuse an existing server. Each
invocation creates a fresh SQLite database in a unique operating-system temporary
directory. It never uses the configured operational database. The database path
is passed to the API through its isolated environment. Temporary test directories
contain only fictitious data and can be removed after all test processes stop.

The suite covers delivery validation, pickup/customer/staff/tracking, protected
store configuration, mobile menu create/edit/deactivation, keyboard dialog
navigation and serious/critical accessibility checks at 320px and 390px. These
Chromium viewport checks do not replace installation and cookie tests on actual
Android/iPhone production browsers.

CI also runs a separate PostgreSQL service. Its dedicated acceptance test refuses
a database whose name does not end in `_test`. It verifies migrations, seed,
staff identities, order completion, public tracking and logout revocation. CI
dumps/restores into another test database and validates rollback/reapplication.
Local pytest skips that test unless `TEST_POSTGRES_URL` is explicitly configured
to the same isolated PostgreSQL test database as `DATABASE_URL`.

Screenshots/traces for failures are uploaded by CI with short retention. No real
customer data or operational database backups belong in these artifacts.
