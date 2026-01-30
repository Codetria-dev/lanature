"""
Script to create initial admin user
Run: python create_admin.py
"""
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if admin already exists
    admin = db.query(User).filter(User.email == "admin@lanature.com").first()
    if admin:
        print("Admin user already exists!")
    else:
        # Create admin user
        admin = User(
            name="Admin",
            email="admin@lanature.com",
            password_hash=get_password_hash("Admin123!"),
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin)
        db.commit()
        print("Admin criado com sucesso")
        print("Email: admin@lanature.com")
        print("Password: Admin123!")
except Exception as e:
    db.rollback()
    print(f"[ERROR] Error creating admin user: {e}")
    raise
finally:
    db.close()
