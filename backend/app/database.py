from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/kisan_vani")

print("=" * 60)
print("📊 DATABASE CONNECTION ATTEMPT")
print("=" * 60)
print(f"Database URL: {DATABASE_URL}")

try:
    # Create engine with better error handling
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections every hour
        pool_size=5,
        max_overflow=10
    )
    
    # Test connection immediately
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connected successfully!")
        
        # Check if database exists
        result = conn.execute(text("SELECT DATABASE()"))
        current_db = result.fetchone()[0]
        print(f"✅ Current database: {current_db}")
        
except Exception as e:
    print("=" * 60)
    print("❌ DATABASE CONNECTION FAILED!")
    print("=" * 60)
    print(f"Error: {e}")
    print("\nPossible fixes:")
    print("1. Make sure MySQL is running")
    print("2. Check DATABASE_URL in .env file")
    print("3. Create database: CREATE DATABASE kisan_vani;")
    print("4. Install PyMySQL: pip install pymysql cryptography")
    print("=" * 60)
    raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Database dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import models after Base is defined
from . import models

# Create all tables
try:
    print("\n📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Verify table was created
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"✅ Tables in database: {tables}")
        
        if 'chat_history' in tables:
            # Check table structure
            result = conn.execute(text("DESCRIBE chat_history"))
            columns = [row[0] for row in result]
            print(f"✅ chat_history columns: {columns}")
        else:
            print("⚠️ WARNING: chat_history table not found!")
    
    print("=" * 60)
    
except Exception as e:
    print("=" * 60)
    print("❌ FAILED TO CREATE TABLES!")
    print("=" * 60)
    print(f"Error: {e}")
    print("=" * 60)