# test_db_connection.py
import asyncio

import asyncpg


async def test_connection():
    # Connection parameters
    database_url = "postgresql+asyncpg://koval@localhost:5432/ecodata"

    # Extract connection details from URL
    # For URL: postgresql+asyncpg://koval@localhost:5432/ecodata
    username = "koval"
    password = ""  # Empty password as per your URL
    host = "localhost"
    port = 5432
    database = "ecodata"

    print(f"Attempting to connect to PostgreSQL...")
    print(f"Host: {host}")
    print(f"Database: {database}")
    print(f"User: {username}")

    try:
        # Establish connection
        conn = await asyncpg.connect(
            user=username, password=password, host=host, port=port, database=database
        )

        print("✅ Successfully connected to PostgreSQL!")

        # Test query - get PostgreSQL version
        version = await conn.fetchval("SELECT version()")
        print(f"\nPostgreSQL version: {version}")

        # Test current database
        current_db = await conn.fetchval("SELECT current_database()")
        print(f"Current database: {current_db}")

        # Test current user
        current_user = await conn.fetchval("SELECT current_user")
        print(f"Current user: {current_user}")

        # List all tables (optional)
        tables = await conn.fetch("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)

        if tables:
            print(f"\nTables in database:")
            for table in tables:
                print(f"  - {table['tablename']}")
        else:
            print("\nNo tables found in the database.")

        # Close connection
        await conn.close()
        print("\n🔒 Connection closed.")

    except asyncpg.InvalidPasswordError:
        print("❌ Invalid password or authentication failed")
    except asyncpg.CannotConnectNowError:
        print("❌ Cannot connect now - database might be starting up")
    except asyncpg.PostgresConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
