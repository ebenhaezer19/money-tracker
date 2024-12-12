import requests
import pymysql
from urllib.parse import quote_plus

def test_all_connections():
    # 1. Test Database Connection
    DB_CONFIG = {
        'host': 'sgp.domcloud.co',
        'user': 'moneytracker',
        'password': ')_W#laodbu#60*4',
        'database': 'moneytracker_db'
    }

    print("\n=== Testing Database Connection ===")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ Database connection successful!")
        
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM User")
            users = cursor.fetchall()
            print(f"Found {len(users)} users in database")
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
    finally:
        if 'connection' in locals():
            connection.close()

    # 2. Test Backend API
    print("\n=== Testing Backend API ===")
    try:
        response = requests.get('http://localhost:5001/test-db')
        print(f"Backend Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Backend connection failed: {str(e)}")

    # 3. Test Login API
    print("\n=== Testing Login API ===")
    try:
        login_data = {
            "username": "eben",
            "password": "admin123"
        }
        response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        print(f"Login Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Login API failed: {str(e)}")

if __name__ == "__main__":
    test_all_connections()