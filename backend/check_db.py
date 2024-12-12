import pymysql
from sqlalchemy import create_engine, text

# Koneksi database
connection = pymysql.connect(
    host='sgp.domcloud.co',
    user='moneytracker',
    password=')_W#laodbu#60*4',
    database='moneytracker_db'
)

try:
    with connection.cursor() as cursor:
        # Lihat daftar tabel
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nDaftar tabel:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Lihat struktur tiap tabel
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  {column[0]}: {column[1]}")
            print()
        
        # Lihat data User lengkap
        print("\nData User Lengkap:")
        cursor.execute("SELECT id_user, username, password FROM User")
        users = cursor.fetchall()
        if users:
            for user in users:
                print(f"ID: {user[0]}")
                print(f"Username: {user[1]}")
                print(f"Password Hash: {user[2]}")  # Password dalam bentuk hash
                print("-" * 50)
        else:
            print("Belum ada user yang terdaftar")

finally:
    connection.close() 