import pymysql
from datetime import datetime

def get_db_connection():
    return pymysql.connect(
        host='sgp.domcloud.co',
        user='moneytracker',
        password=')_W#laodbu#60*4',
        database='moneytracker_db'
    )

def add_created_at_column():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Cek apakah kolom created_at sudah ada
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_NAME = 'Transaction' 
                AND COLUMN_NAME = 'created_at'
                AND TABLE_SCHEMA = 'moneytracker_db'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("Adding created_at column...")
                # Tambah kolom created_at
                cursor.execute("""
                    ALTER TABLE Transaction
                    ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                """)
                
                # Update existing records
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("""
                    UPDATE Transaction 
                    SET created_at = %s 
                    WHERE created_at IS NULL
                """, (current_time,))
                
                connection.commit()
                print("Successfully added created_at column!")
            else:
                print("created_at column already exists")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    add_created_at_column() 