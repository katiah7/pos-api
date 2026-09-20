import getpass
import sys

from fastapi import HTTPException
from pydantic import ValidationError

import models  
from app.database import Base, engine, session
from schemas.user import UserCreate
from services import user_service


def main():
    Base.metadata.create_all(bind=engine)

    username = input("Admin username: ").strip()
    full_name = input("Full name: ").strip()
    password = getpass.getpass("Password (at least 8 characters): ")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords do not match.")

    try:
        data = UserCreate(
            username=username, full_name=full_name, role="admin", password=password
        )
        with session() as db:
            user = user_service.create_user(db, data)
            print(f"Admin '{user.username}' created (user_id={user.user_id}).")
    except ValidationError as exc:
        sys.exit(f"Invalid input: {exc.errors()[0]['msg']}")
    except HTTPException as exc:
        sys.exit(exc.detail)


if __name__ == "__main__":
    main()
