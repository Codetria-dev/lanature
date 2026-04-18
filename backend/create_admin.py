"""
Script to create initial admin user
Run: python create_admin.py
"""
import os
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
admin_email = os.getenv("ADMIN_EMAIL")
admin_password = os.getenv("ADMIN_PASSWORD")

if not admin_email or not admin_password:
    raise RuntimeError("Set ADMIN_EMAIL and ADMIN_PASSWORD environment variables before running this script.")
if len(admin_password) < 12:
    raise RuntimeError("ADMIN_PASSWORD must be at least 12 characters long.")

try:
    # Check if admin already exists
    admin = db.query(User).filter(User.email == admin_email).first()
    if admin:
        print("Admin user already exists!")
    else:
        # Create admin user
        admin = User(
            name="Admin",
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin)
        db.commit()
        print("Admin criado com sucesso")
        print(f"Email: {admin_email}")
except Exception as e:
    db.rollback()
    print(f"[ERROR] Error creating admin user: {e}")
    raise
finally:
    db.close()
