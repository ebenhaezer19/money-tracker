import pymysql
from urllib.parse import quote_plus

# Konfigurasi database
DB_CONFIG = {
    'host': 'sgp.domcloud.co',
    'user': 'moneytracker',
    'password': ')_W#laodbu#60*4',
    'database': 'moneytracker_db'
}

try:
    # Koneksi ke database
    connection = pymysql.connect(**DB_CONFIG)
    
    with connection.cursor() as cursor:
        # Cek user eben
        cursor.execute("SELECT id_user, username FROM User WHERE username = %s", ('eben',))
        user = cursor.fetchone()
        
        if user:
            print(f"User ditemukan:")
            print(f"ID: {user[0]}")
            print(f"Username: {user[1]}")
        else:
            print("User 'eben' tidak ditemukan")
            
        # Tampilkan semua user
        print("\nDaftar semua user:")
        cursor.execute("SELECT id_user, username FROM User")
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}")

finally:
    if 'connection' in locals():
        connection.close() 