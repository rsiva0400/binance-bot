#!/usr/bin/env python3
"""
Database initialization script.
Creates all required tables for the trading bot.

Supports both LOCAL (PostgreSQL) and SUPABASE databases.

Usage:
    python init_database.py
"""

import asyncio
from config.settings import settings
import structlog

logger = structlog.get_logger()

# SQL Schema
SCHEMA_SQL = """
-- Create trades table
CREATE TABLE IF NOT EXISTS trades (
    trade_id UUID PRIMARY KEY,
    symbol TEXT NOT NULL,
    entry_price NUMERIC NOT NULL,
    exit_price NUMERIC,
    quantity NUMERIC NOT NULL,
    pnl NUMERIC,
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP
);

-- Create decisions table (optional, for future use)
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY,
    symbol TEXT,
    decision TEXT,
    reason TEXT,
    created_at TIMESTAMP NOT NULL
);

-- Create bot_events table
CREATE TABLE IF NOT EXISTS bot_events (
    id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at DESC);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_closed_at ON trades(closed_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON bot_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON bot_events(event_type);
"""

# Supabase-specific RLS policies
SUPABASE_RLS_SQL = """
-- Enable Row Level Security (RLS)
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_events ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow service role full access to trades" ON trades;
DROP POLICY IF EXISTS "Allow service role full access to decisions" ON decisions;
DROP POLICY IF EXISTS "Allow service role full access to bot_events" ON bot_events;
DROP POLICY IF EXISTS "Allow anon insert to trades" ON trades;
DROP POLICY IF EXISTS "Allow anon select on trades" ON trades;
DROP POLICY IF EXISTS "Allow anon insert to bot_events" ON bot_events;
DROP POLICY IF EXISTS "Allow anon select on bot_events" ON bot_events;

-- Create policies for service role (full access)
CREATE POLICY "Allow service role full access to trades"
ON trades FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow service role full access to decisions"
ON decisions FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow service role full access to bot_events"
ON bot_events FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Create policies for anon key (limited access)
CREATE POLICY "Allow anon insert to trades"
ON trades FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow anon select on trades"
ON trades FOR SELECT
TO anon
USING (true);

CREATE POLICY "Allow anon insert to bot_events"
ON bot_events FOR INSERT
TO anon
WITH CHECK (true);

CREATE POLICY "Allow anon select on bot_events"
ON bot_events FOR SELECT
TO anon
USING (true);
"""


async def init_local_database():
    """Initialize local PostgreSQL database."""
    print("\n" + "="*60)
    print("INITIALIZING LOCAL POSTGRESQL DATABASE")
    print("="*60 + "\n")

    try:
        import asyncpg

        print(f"Connecting to: {settings.database_url}")

        conn = await asyncpg.connect(settings.database_url)

        try:
            # Execute schema
            print("Creating tables...")
            await conn.execute(SCHEMA_SQL)
            print("✅ Tables created successfully!")

            # Verify tables
            print("\nVerifying tables...")
            tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('trades', 'bot_events', 'decisions')
                ORDER BY table_name
            """)

            print("\nCreated tables:")
            for table in tables:
                print(f"  ✅ {table['table_name']}")

            # Check indexes
            print("\nVerifying indexes...")
            indexes = await conn.fetch("""
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND indexname LIKE 'idx_%'
                ORDER BY indexname
            """)

            print("\nCreated indexes:")
            for idx in indexes:
                print(f"  ✅ {idx['indexname']}")

            print("\n✅ Local database initialized successfully!")
            return True

        finally:
            await conn.close()

    except ImportError:
        print("❌ Error: asyncpg not installed")
        print("   Install with: pip install asyncpg")
        return False
    except Exception as exc:
        print(f"❌ Error initializing database: {exc}")
        return False


async def init_supabase_database():
    """Initialize Supabase database."""
    print("\n" + "="*60)
    print("INITIALIZING SUPABASE DATABASE")
    print("="*60 + "\n")

    try:
        from supabase import create_client

        print(f"Connecting to: {settings.supabase_url[:30]}...")

        client = create_client(settings.supabase_url, settings.supabase_key)

        # Test connection
        try:
            result = client.table("trades").select("count", count="exact").limit(0).execute()
            print("✅ Connection successful!")
        except Exception as e:
            if "does not exist" in str(e):
                print("ℹ️  Tables don't exist yet (expected)")
            else:
                raise

        print("\n⚠️  IMPORTANT: Supabase tables must be created via SQL Editor")
        print("="*60)
        print("\nFollow these steps:")
        print("\n1. Go to your Supabase project dashboard")
        print("   URL: " + settings.supabase_url.replace("/rest/v1", ""))

        print("\n2. Click 'SQL Editor' in the left sidebar")

        print("\n3. Click 'New Query'")

        print("\n4. Copy and paste the following SQL:\n")
        print("-"*60)
        print(SCHEMA_SQL)
        print("-"*60)

        print("\n5. Click 'Run' to execute the SQL")

        print("\n6. (Optional) For Row Level Security, also run:\n")
        print("-"*60)
        print(SUPABASE_RLS_SQL)
        print("-"*60)

        print("\n7. Verify tables in 'Table Editor'")

        print("\n" + "="*60)
        print("\n💡 TIP: You can also copy the SQL from:")
        print("   - SUPABASE_SETUP.md (step-by-step guide)")
        print("   - persistence/schema.sql (basic schema)")
        print("\n" + "="*60 + "\n")

        # Offer to copy SQL to clipboard (if available)
        try:
            import pyperclip
            pyperclip.copy(SCHEMA_SQL + "\n\n" + SUPABASE_RLS_SQL)
            print("✅ SQL copied to clipboard! Paste it in Supabase SQL Editor.\n")
        except ImportError:
            pass

        return True

    except ImportError:
        print("❌ Error: supabase not installed")
        print("   Install with: pip install supabase")
        return False
    except Exception as exc:
        print(f"❌ Error: {exc}")
        return False


async def verify_database():
    """Verify database is working."""
    print("\n" + "="*60)
    print("VERIFYING DATABASE CONNECTION")
    print("="*60 + "\n")

    if settings.database_type == "SUPABASE":
        try:
            from supabase import create_client

            client = create_client(settings.supabase_url, settings.supabase_key)

            # Test querying each table
            tables = ["trades", "bot_events", "decisions"]
            for table_name in tables:
                try:
                    result = client.table(table_name).select("count", count="exact").limit(0).execute()
                    print(f"✅ {table_name}: accessible")
                except Exception as e:
                    print(f"❌ {table_name}: {str(e)[:50]}")

            print("\n✅ Supabase database verification complete!")
            return True

        except Exception as exc:
            print(f"❌ Verification failed: {exc}")
            return False

    else:  # LOCAL
        try:
            import asyncpg

            conn = await asyncpg.connect(settings.database_url)

            try:
                # Check each table
                tables = await conn.fetch("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('trades', 'bot_events', 'decisions')
                """)

                print("Available tables:")
                for table in tables:
                    # Get row count
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['table_name']}")
                    print(f"  ✅ {table['table_name']}: {count} rows")

                if len(tables) >= 2:  # trades and bot_events minimum
                    print("\n✅ Local database verification complete!")
                    return True
                else:
                    print("\n⚠️  Some tables are missing!")
                    return False

            finally:
                await conn.close()

        except Exception as exc:
            print(f"❌ Verification failed: {exc}")
            return False


async def main():
    """Main initialization flow."""
    print("\n🗄️  DATABASE INITIALIZATION TOOL")
    print("="*60)

    print(f"\nDatabase Type: {settings.database_type}")

    if settings.database_type == "SUPABASE":
        await init_supabase_database()
        print("\n📝 After creating tables in Supabase, run this again with:")
        print("   python init_database.py --verify")
        print("\nOr run the bot and it will report any missing tables.")

    elif settings.database_type == "LOCAL":
        success = await init_local_database()
        if success:
            await verify_database()

    else:
        print(f"❌ Unknown database type: {settings.database_type}")
        print("   Set DATABASE_TYPE=LOCAL or DATABASE_TYPE=SUPABASE in .env")

    print("\n" + "="*60)
    print("✅ INITIALIZATION COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys

    if "--verify" in sys.argv:
        asyncio.run(verify_database())
    else:
        asyncio.run(main())
