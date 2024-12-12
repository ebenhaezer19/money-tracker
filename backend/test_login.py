import requests

def test_login(username, password):
    # URL endpoint login
    url = "http://localhost:5001/api/auth/login"
    
    # Data login
    data = {
        "username": username,
        "password": password
    }
    
    try:
        # Kirim request login
        response = requests.post(url, json=data)
        
        # Tampilkan hasil
        print("\nStatus Code:", response.status_code)
        print("Response:", response.json())
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Test login dengan kredensial yang baru dibuat
    username = input("Masukkan username untuk login: ")
    password = input("Masukkan password untuk login: ")
    
    test_login(username, password) 