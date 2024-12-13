import pymysql
from pymysql import connect

# Koneksi database dengan error handling
def get_db_connection():
    try:
        connection = connect(
            host='sgp.domcloud.co',
            user='moneytracker',
            password=')_W#laodbu#60*4',
            database='moneytracker_db'
        )
        print("Database connection successful")
        return connection
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

def add_color_column():
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            # Cek apakah kolom color sudah ada
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_NAME = 'Category' 
                AND COLUMN_NAME = 'color'
                AND TABLE_SCHEMA = 'moneytracker_db'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("Adding color column...")
                # Tambah kolom color jika belum ada
                cursor.execute("""
                    ALTER TABLE Category
                    ADD COLUMN color VARCHAR(7) DEFAULT '#4CAF50'
                """)
                
                # Default colors untuk kategori yang sudah ada
                colors = [
                    '#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#F44336', 
                    '#009688', '#FF9800', '#03A9F4', '#E91E63', '#8BC34A'
                ]
                
                # Update kategori yang sudah ada dengan warna default
                cursor.execute("SELECT id_category FROM Category")
                categories = cursor.fetchall()
                
                for i, category in enumerate(categories):
                    color = colors[i % len(colors)]
                    cursor.execute("""
                        UPDATE Category 
                        SET color = %s 
                        WHERE id_category = %s
                    """, (color, category[0]))
                    print(f"Updated category {category[0]} with color {color}")
                    
                connection.commit()
                print("Successfully added and populated color column!")
            else:
                print("Color column already exists")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    add_color_column() 