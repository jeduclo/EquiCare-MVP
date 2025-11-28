"""
Script to create initial admin user and initialize database
Run this once to set up the application
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import db_manager
from src.database.models import User
from src.auth.password_utils import hash_password
from datetime import datetime


def create_admin_user():
    """Create the initial admin user"""
    
    print("=" * 60)
    print("EquiCare MVP - Database Initialization")
    print("=" * 60)
    
    # Initialize database (create tables)
    print("\n[1/3] Creating database tables...")
    db_manager.init_db()
    print("✓ Database tables created")
    
    # Check if admin already exists
    print("\n[2/3] Checking for existing admin user...")
    with db_manager.get_session() as session:
        existing_admin = session.query(User).filter_by(username='admin').first()
        
        if existing_admin:
            print("⚠ Admin user already exists!")
            print(f"   Username: admin")
            print(f"   Created: {existing_admin.created_at}")
            
            response = input("\nDo you want to reset the admin password? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                existing_admin.password_hash = hash_password('admin123')
                existing_admin.is_active = True
                existing_admin.failed_login_attempts = 0
                existing_admin.locked_until = None
                session.commit()
                print("✓ Admin password reset to: admin123")
            else:
                print("No changes made.")
            return
    
    # Create admin user
    print("\n[3/3] Creating admin user...")
    admin_user = User(
        username='admin',
        password_hash=hash_password('admin123'),
        role='administrator',
        full_name='System Administrator',
        email='admin@equicare.local',
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    with db_manager.get_session() as session:
        session.add(admin_user)
        session.commit()
        print("✓ Admin user created successfully")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\n📋 Login Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n⚠️  IMPORTANT: Change the admin password after first login!")
    print("\n🚀 Run the application:")
    print("   streamlit run src/app.py")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        create_admin_user()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)