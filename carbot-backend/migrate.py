"""
Database Migration Script
Run this to add constraints and indexes to the database
"""

from db import get_connection
import sys

def run_migrations():
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("Starting database migrations...")

        # Create tables if they don't exist
        print("0. Creating tables if they don't exist...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT,
                name VARCHAR(255),
                telegram_username VARCHAR(255)
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id SERIAL PRIMARY KEY,
                make VARCHAR(50),
                model VARCHAR(50),
                year INTEGER,
                price INTEGER,
                mileage INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                latitude FLOAT,
                longitude FLOAT,
                user_id INTEGER
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS car_images (
                id SERIAL PRIMARY KEY,
                car_id INTEGER NOT NULL,
                image_data BYTEA NOT NULL,
                image_order INTEGER DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                car_id INTEGER NOT NULL,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE,
                FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Enable pg_trgm extension for better text search
        print("1. Enabling pg_trgm extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

        # Add NOT NULL constraints to users table
        print("2. Adding constraints to users table...")
        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE users ALTER COLUMN telegram_id SET NOT NULL;
            EXCEPTION
                WHEN others THEN NULL;
            END $$;
        """)

        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE users ALTER COLUMN name SET NOT NULL;
            EXCEPTION
                WHEN others THEN NULL;
            END $$;
        """)

        # Add unique constraint on telegram_id
        print("3. Adding unique constraint on telegram_id...")
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'users_telegram_id_unique'
                ) THEN
                    ALTER TABLE users ADD CONSTRAINT users_telegram_id_unique UNIQUE (telegram_id);
                END IF;
            END $$;
        """)

        # Add NOT NULL constraints to cars table
        print("4. Adding NOT NULL constraints to cars table...")
        for col in ['make', 'model', 'year', 'price', 'mileage', 'description', 'user_id']:
            cur.execute(f"""
                DO $$
                BEGIN
                    ALTER TABLE cars ALTER COLUMN {col} SET NOT NULL;
                EXCEPTION
                    WHEN others THEN NULL;
                END $$;
            """)

        # Add CHECK constraints
        print("5. Adding CHECK constraints...")
        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE cars ADD CONSTRAINT cars_year_valid CHECK (year >= 1900 AND year <= 2100);
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
        """)

        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE cars ADD CONSTRAINT cars_price_positive CHECK (price > 0);
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
        """)

        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE cars ADD CONSTRAINT cars_mileage_positive CHECK (mileage >= 0);
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
        """)

        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE cars ADD CONSTRAINT cars_latitude_valid
                CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90));
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
        """)

        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE cars ADD CONSTRAINT cars_longitude_valid
                CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180));
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
        """)

        # Add foreign key constraint
        print("6. Adding foreign key constraint...")
        cur.execute("""
            DO $$
            BEGIN
                ALTER TABLE cars ADD CONSTRAINT cars_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            EXCEPTION
                WHEN duplicate_object THEN NULL;
            END $$;
        """)

        # Add indexes
        print("7. Creating indexes for performance...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cars_make ON cars (make);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cars_model ON cars (model);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cars_make_model ON cars (make, model);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cars_user_id ON cars (user_id);")

        # Add trigram indexes for better ILIKE performance
        print("8. Creating trigram indexes for text search...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cars_make_trgm ON cars USING gin (make gin_trgm_ops);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cars_model_trgm ON cars USING gin (model gin_trgm_ops);")

        # Add indexes for car_images
        print("9. Creating indexes for car_images...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_car_images_car_id ON car_images (car_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_car_images_order ON car_images (car_id, image_order);")

        # Add indexes for messages
        print("10. Creating indexes for messages...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_car_id ON messages (car_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_from_user ON messages (from_user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_to_user ON messages (to_user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_unread ON messages (to_user_id, is_read);")

        # Add telegram_username column if it doesn't exist
        print("11. Adding telegram_username column to users...")
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='users' AND column_name='telegram_username'
                ) THEN
                    ALTER TABLE users ADD COLUMN telegram_username VARCHAR(255);
                END IF;
            END $$;
        """)

        conn.commit()
        print("\n✅ All migrations completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_migrations()
