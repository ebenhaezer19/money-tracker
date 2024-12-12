import pymysql
from urllib.parse import quote_plus

# Konfigurasi database yang benar
DB_CONFIG = {
    'host': 'sgp.domcloud.co',  # Bukan localhost
    'user': 'moneytracker',
    'password': ')_W#laodbu#60*4',
    'database': 'moneytracker_db'
}

try:
    # Test koneksi
    connection = pymysql.connect(**DB_CONFIG)
    print("Berhasil terhubung ke database!")
    
    with connection.cursor() as cursor:
        # Test query
        cursor.execute("SELECT 1")
        print("Test query berhasil!")
        
        # Lihat daftar tabel
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nDaftar tabel:")
        for table in tables:
            print(f"- {table[0]}")

finally:
    if 'connection' in locals():
        connection.close() 