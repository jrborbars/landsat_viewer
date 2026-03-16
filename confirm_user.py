#!/usr/bin/env python3
"""
Utility script to manually confirm a user's email in the database.
Usage: python3 confirm_user.py <email>
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to sys.path to allow importing app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.core.config import settings
from app.models.user import User

def confirm_user(email: str):
    """Confirm user by email"""
    # Use environment variable if set, otherwise use settings
    # Note: Inside docker, this should point to /app/data/test.db
    database_url = os.environ.get('DATABASE_URL', settings.DATABASE_URL)
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ Error: User with email '{email}' not found.")
            return

        if user.email_confirmed:
            print(f"ℹ️ User '{email}' is already confirmed.")
            return

        user.email_confirmed = True
        user.email_confirmation_token = None
        db.commit()
        print(f"✅ Success: User '{email}' has been confirmed.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 confirm_user.py <email>")
        sys.exit(1)

    user_email = sys.argv[1]
    confirm_user(user_email)
