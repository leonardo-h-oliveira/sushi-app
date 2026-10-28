"""Create private PostgreSQL dumps or restore into an explicitly named test DB."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit, parse_qs, unquote


def connection_environment(variable, restore=False):
    url = urlsplit(os.environ.get(variable, ""))
    database = unquote(url.path.lstrip("/"))
    if url.scheme not in {"postgres", "postgresql"} or not url.hostname or not database:
        raise ValueError(f"Set {variable} to the intended PostgreSQL connection URL.")
    if restore and not database.endswith("_restore_test"):
        raise ValueError("Restore is restricted to databases ending in _restore_test.")
    env = os.environ.copy()
    env.update(PGHOST=url.hostname, PGPORT=str(url.port or 5432), PGDATABASE=database,
               PGUSER=unquote(url.username or ""), PGPASSWORD=unquote(url.password or ""),
               PGSSLMODE=parse_qs(url.query).get("sslmode", ["require"])[0])
    return env


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["backup", "restore"])
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    path = args.file.resolve()
    command = "pg_dump" if args.operation == "backup" else "pg_restore"
    if not shutil.which(command):
        raise ValueError(f"Install the PostgreSQL client tools containing {command}.")
    if args.operation == "backup":
        env = connection_environment("DATABASE_URL")
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        subprocess.run([command, "--format=custom", "--no-owner", "--no-acl", "--file", str(path)], env=env, check=True, capture_output=True)
        path.with_suffix(path.suffix + ".sha256").write_text(digest(path) + "\n", encoding="ascii")
        print("Backup and SHA-256 checksum created. Store both in encrypted, access-controlled storage.")
    else:
        env = connection_environment("RESTORE_DATABASE_URL", restore=True)
        expected = path.with_suffix(path.suffix + ".sha256").read_text(encoding="ascii").strip()
        if digest(path) != expected:
            raise ValueError("Backup checksum does not match.")
        subprocess.run([command, "--no-owner", "--no-acl", "--exit-on-error", "--dbname", env["PGDATABASE"], str(path)], env=env, check=True, capture_output=True)
        print("Restore completed in the test database. Validate data and application behavior before accepting the recovery procedure.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError):
        raise SystemExit("Operation failed. Verify client tools, connection configuration, destination and backup integrity in a private environment. Partial backup files must not be accepted.")
