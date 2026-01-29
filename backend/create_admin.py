"""
Script to create initial admin user
Run: python create_admin.py
"""
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash

def create_admin_user():
    """Create admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            name="Admin",
            email="admin@admin.com",  # Changed to valid email format
            password_hash=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        print("[OK] Admin user created successfully!")
        print("Email: admin@admin.com")
        print("Password: admin123")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating admin user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    create_admin_user()
