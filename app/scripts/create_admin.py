"""One-time seed script — run directly, never through the API.
Usage: uv run python -m app.scripts.create_admin admin@veriflow.dev somepassword
"""
import sys
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

def create_admin(email: str, password: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            existing.role = UserRole.ADMIN
            db.commit()
            print(f"Existing user '{email}' promoted to admin.")
            return
        user = User(email=email, hashed_password=hash_password(password), role=UserRole.ADMIN)
        db.add(user); db.commit()
        print(f"Admin account created: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: uv run python -m app.scripts.create_admin <email> <password>")
        sys.exit(1)
    create_admin(sys.argv[1], sys.argv[2])