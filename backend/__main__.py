# Standard lib imports
import os

# Third-party imports
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Project imports
pass


# Load env variables
load_dotenv()


app = Flask(__name__)
CORS(app)  # Perbolehkan CORS dari frontend Vue


@app.route('/api/greet', methods=['GET'])
def greet():
    return jsonify({"message": "Hello from Flask!"})


@app.route('/')
@app.route('/<first>')
@app.route('/<first>/<path:rest>')
def fallback(first=None, rest=None):
    return 'This one catches everything else'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
