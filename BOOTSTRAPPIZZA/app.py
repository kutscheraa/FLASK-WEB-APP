from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['MONGO_URI'] = 'url'

client = MongoClient(app.config['MONGO_URI'])
db = client.get_database()

@app.route('/test')
def test():
    return render_template('base.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user exists in the database
        user = db['users'].find_one({'username': username})
        
        if user:
            # Check if the password is correct
            if check_password_hash(user['password'], password):
                return redirect(url_for('dashboard'))
            else:
                return 'Invalid password'
        else:
            return 'Invalid username'
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        # Insert the new user into the database
        db['users'].insert_one({'username': username, 'password': hashed_password})
        
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')
    
@app.route('/dashboard')
def dashboard():
    return 'Welcome to the dashboard'

if __name__ == '__main__':
    app.run(debug=True)
