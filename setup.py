import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from peewee import PostgresqlDatabase

def setup_database():
    """Initialize the database and load data from dump file"""
    # Load environment variables
    load_dotenv()
    
    # Database configuration from environment
    db_name = os.getenv("DB_NAME", "tsmx")
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "admin")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    # Connect to default PostgreSQL database to create new DB
    admin_db = PostgresqlDatabase(
        "postgres",
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )

    try:
        # Create database if it doesn't exist
        admin_db.execute_sql(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created successfully")
    except Exception as e:
        print(f"Database '{db_name}' already exists or creation failed: {e}")

    # Connect to the newly created database
    db = PostgresqlDatabase(
        db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )

    # Check if dump file exists
    dump_file = Path("data/dump.sql")
    if dump_file.exists():
        print("Loading initial data from dump file...")
        
        # Command to restore dump using psql
        cmd = [
            "psql",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            f"--dbname={db_name}",
            "-f", str(dump_file)
        ]
        
        # Set password in environment for psql
        env = os.environ.copy()
        env["PGPASSWORD"] = db_pass
        
        try:
            subprocess.run(cmd, check=True, env=env)
            print("Data imported successfully from dump file")
        except subprocess.CalledProcessError as e:
            print(f"Error importing dump: {e}")
        except FileNotFoundError:
            print("Error: psql command not found. Please ensure PostgreSQL is installed")
    else:
        print(f"Dump file not found at {dump_file}")

if __name__ == "__main__":
    setup_database()