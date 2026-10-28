"""Create a staff account or reset its password without printing credentials."""
import argparse
import getpass

from app.database import SessionLocal
from app.services.admin_identity import create_admin, reset_password


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("--reset-password", action="store_true")
    args = parser.parse_args()
    password = getpass.getpass("New password: ")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords do not match.")
    try:
        with SessionLocal() as db:
            if args.reset_password:
                reset_password(db, args.username, password)
            else:
                create_admin(db, args.username, password)
    except ValueError as error:
        raise SystemExit(str(error))
    print("Administrator account updated. Previous sessions are invalid after a password reset.")
