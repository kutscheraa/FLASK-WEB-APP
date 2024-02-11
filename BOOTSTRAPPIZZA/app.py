from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from redis import Redis
from flask_login import login_required, logout_user, UserMixin, LoginManager, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MONGO_URI'] = 'mongodb+srv://kutscherabiz:pw@cluster0.mv0rtpy.mongodb.net/?retryWrites=true&w=majority'

client = MongoClient(app.config['MONGO_URI'])
db = client.get_database("pizza")
users = db['users']


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/pizza')
def pizza():
    return render_template('pizza.html')

@app.route('/subs')
def subs():
    return render_template('subs.html')

@app.route('/salads')
def salads():
    return render_template('salads.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        existing_user = users.find_one({"username": username})
        
        if existing_user is not None:
            if check_password_hash(existing_user["password"], password):
                return("Přihlášení bylo úspěšné!")
                #return redirect(url_for('home'))
            else:
                return("Přihlášení bylo úspěšné!")
        else:
            return("Uživatel neexistuje!")
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        existing_user = users.find_one({"username": username})
        
        if existing_user is None:
            new_user = {"username": username, "password": password}
            users.insert_one(new_user)
            
            return("Registrace byla úspěšná!")
            return redirect(url_for('login'))
        elif existing_user is not None:
            return("Uživatel s tímto uživatelským jménem již existuje!")
        
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
