# Production acceptance and recovery

The first release is intended for real restaurant orders. A successful deployment
or CI run alone does not authorize opening the store. Keep operational readiness
disabled until the restaurant and release owner approve the remaining items.

## Evidence already automated

CI covers backend/frontend checks, the production build, delivery/pickup flows,
staff configuration, keyboard/mobile checks at 320px and 390px, and a separate
PostgreSQL acceptance job. The PostgreSQL job applies migrations, seeds twice,
completes an order, checks tracking privacy and session revocation, dumps the
database, restores into a separate database and checks restored row counts. It
then rolls migrations back and reapplies them.

These test databases contain only fictitious data. Their restoration is distinct
from the production provider's scheduled backups and recovery drill.

## Deployment details still required

Record frontend/API/database accounts, chosen plans, public domains, spending
limit, service owner and incident contact. The existing Render blueprint is for
staging; do not assume its free plan is the approved production service.

Configure explicit HTTPS CORS origins, apply all migrations, provision the staff
account with `backend/admin_account.py`, and deploy matching frontend/API versions.
Verify cross-site cookie behavior in the actual browsers/domains. Old signed
sessions do not survive the new identity migration.

Run the read-only API probes:

```text
python backend/check_deployment.py https://your-api-host --require-closed
```

`/health` checks process liveness. `/ready` checks database connectivity and
returns a safe 503 on failure. Configure an external monitor for `/ready` and the
frontend. Verify a simulated failure reaches the agreed incident contact. Error
and staff logs contain a request reference and route template, not request bodies
or customer data. Set access and retention at the hosting provider.

## Production backup and restore

Choose a provider-supported automatic backup schedule and encrypted restricted
storage. Agree recovery objectives and retention with the owner before opening.
Do not store database dumps in Git or public CI artifacts.

The helper requires PostgreSQL client tools compatible with the server. Set the
source `DATABASE_URL` privately in the execution environment, then:

```text
python backend/backup_database.py backup private-backups/release.dump
```

The helper refuses an existing output path and writes a SHA-256 sidecar. Failed
or interrupted files must not be accepted. Transfer completed dumps/checksums to
the approved encrypted storage; local files alone are not an automatic backup.

Create an empty isolated restore database whose name ends in `_restore_test`.
Set its separate `RESTORE_DATABASE_URL` privately, then:

```text
python backend/backup_database.py restore private-backups/release.dump
```

The helper verifies the checksum, restores without ownership/ACL changes and
stops on errors. Never point a test restore at the operational database. Confirm
order counts, catalog, staff access and an isolated test order. Record backup time,
restore duration, source and restored version, reviewer and outcome privately.

## Manual restaurant acceptance

- Approve actual menu names, prices, images, required variations and add-ons.
- Configure neighborhoods, fee, minimum, weekly hours and exceptional closures.
- Approve payment instructions and cash-change behavior.
- Test delivery, pickup, cancellation and every valid completion path.
- Confirm orders appear and refresh in the staff dashboard.
- Verify customer tracking, closed-store errors and changed-price reconfirmation.
- Test representative Android/iPhone browsers and PWA installation on HTTPS.
- Approve customer information using the review draft in this folder.
- Confirm the real provider's monitoring and restored production backup.

## Rollback and release

Record the previous frontend/API commit and a verified pre-release backup before
deployment. Close the store first if checkout integrity is uncertain. Prefer a
forward repair for database changes; never downgrade a live database simply to
match an older application without reviewing data loss and schema compatibility.
Rehearse rollback in staging, probe readiness and repeat an isolated order flow.

Only after the required evidence and owner acceptance are recorded in issue #14
should the release owner create `v0.1.0` and enable live ordering.
