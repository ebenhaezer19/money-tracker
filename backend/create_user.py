from flask_bcrypt import Bcrypt
import pymysql
from utils import generate_id

# Inisialisasi Bcrypt
bcrypt = Bcrypt()

# Konfigurasi database
DB_CONFIG = {
    'host': 'sgp.domcloud.co',  # Bukan localhost
    'user': 'moneytracker',
    'password': ')_W#laodbu#60*4',
    'database': 'moneytracker_db'
}

# Buat koneksi
connection = pymysql.connect(**DB_CONFIG)

def create_user(username, password):
    try:
        with connection.cursor() as cursor:
            # Cek username
            cursor.execute("SELECT username FROM User WHERE username = %s", (username,))
            if cursor.fetchone():
                print(f"Username {username} sudah digunakan!")
                return False
            
            # Generate ID dan hash password
            user_id = generate_id()
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Insert user
            cursor.execute(
                "INSERT INTO User (id_user, username, password) VALUES (%s, %s, %s)",
                (user_id, username, password_hash)
            )
            
            # Buat kategori default
            default_titles = ('A', 'B', 'C', 'D', 'E')
            for title in default_titles:
                category_id = generate_id()
                cursor.execute(
                    "INSERT INTO Category (id_category, title, user_id) VALUES (%s, %s, %s)",
                    (category_id, title, user_id)
                )
            
            connection.commit()
            print(f"User {username} berhasil dibuat!")
            print(f"ID: {user_id}")
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}")
        connection.rollback()
        return False

if __name__ == "__main__":
    try:
        username = input("Masukkan username: ")
        password = input("Masukkan password: ")
        create_user(username, password)
    finally:
        connection.close() 