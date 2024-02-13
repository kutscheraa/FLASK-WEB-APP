from flask import Flask, render_template, request, redirect, url_for, session, request, flash
from flask_login import UserMixin, login_user, logout_user, current_user
from pymongo import MongoClient
import redis, pickle
from bson import ObjectId
from datetime import datetime
from flask_login import login_required, logout_user, UserMixin, LoginManager, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MONGO_URI'] = 'mongodb+srv://kutscherabiz:pw@cluster0.mv0rtpy.mongodb.net/?retryWrites=true&w=majority'

login_manager = LoginManager()
login_manager.init_app(app) # Inicializace LoginManager

client = MongoClient(app.config['MONGO_URI'])
db = client.get_database("pizza")
users = db['users']
orders = db['orders']
pizza_collection = db['pizza']
sub_collection = db['sub']
salad_collection = db['salad']



redis_client = redis.Redis(
    host='db-redis-fra1-35635-do-user-14112159-0.c.db.ondigitalocean.com',
    port=25061,
    password='AVNS_8rZfeTmtIHGoK--J5NG',
    ssl=True,
)



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_data = redis_client.hgetall('cart')
    if not cart_data:
        return redirect(url_for('cart'))

    cart_items = []
    total_price = 0

    for product_bytes, details_bytes in cart_data.items():
        product_name = product_bytes.decode('utf-8')
        details = pickle.loads(details_bytes)
        total_price += details['price'] * details['quantity']
        cart_items.append({'name': product_name, 'quantity': details['quantity'], 'price': details['price']})

    if request.method == 'POST':
        if current_user.is_authenticated:
            # Získání informací o uživateli z MongoDB
            user_info = users.find_one({'username': current_user.username}, {'firstname': 1, 'lastname': 1, 'address': 1, 'phonenumber': 1})

            if user_info:
                # Uložit informace o uživateli a košíku do databáze
                orders.insert_one({
                    'user_info': user_info,
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'timestamp': datetime.now()
                })
            else:
                flash('Chyba: Nepodařilo se získat informace o uživateli.', 'error')
        else:
            # Pro nepřihlášeného uživatele zpracovat údaje formuláře
            user_info = {
                'firstname': request.form['firstname'],
                'lastname': request.form['lastname'],
                'address': request.form['address'],
                'phonenumber': request.form['phonenumber'],
                # další informace o uživateli, které chcete uložit
            }
            # Uložit informace o uživateli a košíku do databáze
            orders.insert_one({
                'user_info': user_info,
                'cart_items': cart_items,
                'total_price': total_price,
                'timestamp': datetime.now()
            })

        redis_client.delete('cart')  # Vymazat košík v Redis
        return redirect(url_for('thank_you'))

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)



@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')




@app.route('/cart')
def cart():
    cart_items = []
    total_price = 0

    # Redis
    cart_data = redis_client.hgetall('cart') # Získání košíku z Redis
    if cart_data:
        for product_bytes, details_bytes in cart_data.items():
            product_name = product_bytes.decode('utf-8')
            details = pickle.loads(details_bytes)
            total_price += details['price'] * details['quantity']
            cart_items.append({'name': product_name, 'quantity': details['quantity'], 'price': details['price']})

        return render_template('cart.html', cart_items=cart_items, total_price=total_price) # Vykreslení košíku
    else:
        return render_template('cart.html', cart_items=[], total_price=0, message="Your cart is empty.")

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_type = request.form['product_type']
    product_name = request.form['product_name']
    product_price = float(request.form['product_price'])

    # Pokud košík neexistuje, vytvořte jej jako prázdný slovník v relaci
    if 'cart' not in session:
        session['cart'] = {}

    # Zvyšte počet položek v košíku nebo přidejte novou položku s množstvím 1
    if redis_client.hexists('cart', product_name):  
        details = pickle.loads(redis_client.hget('cart', product_name))  
        details['quantity'] += 1
        redis_client.hset('cart', product_name, pickle.dumps(details))  # Update množství v Redis
    else:
        redis_client.hset('cart', product_name, pickle.dumps({'price': product_price, 'quantity': 1}))

    flash('Produkt vložen do košíku', 'success')
    return redirect(url_for(product_type))  # Po přidání do košíku přesměrujte zpět na stránku produktu

@app.route('/remove_from_cart/<product_name>', methods=['POST'])
def remove_from_cart(product_name):
    if redis_client.hexists('cart', product_name):
        details = pickle.loads(redis_client.hget('cart', product_name))  
        details['quantity'] -= 1
        if details['quantity'] == 0:
            redis_client.hdel('cart', product_name)
        else:
            redis_client.hset('cart', product_name, pickle.dumps(details))  # Update množství v Redis

    flash('Produkt odstraněn z košíku', 'error')
    return redirect(url_for('cart'))



@app.route('/pizza')
def pizza():
    pizza = list(pizza_collection.find())
    return render_template('pizza.html', pizza=pizza)

@app.route('/subs')
def subs():
    sub = list(sub_collection.find())
    return render_template('subs.html', sub=sub)

@app.route('/salads')
def salads():
    salad = list(salad_collection.find())
    return render_template('salads.html', salad=salad)

@app.route('/')
def home():
    return render_template('home.html')

class User(UserMixin):
    def __init__(self, username, password, address, firstname, lastname, phonenumber):
        self.username = username
        self.password = password
        self.address = address
        self.firstname = firstname
        self.lastname = lastname
        self.phonenumber = phonenumber

    def get_id(self):
        return self.username



@login_manager.user_loader
def load_user(username):
    user_data = users.find_one({'username': username})
    if user_data:  # Pokud uživatel existuje, vytvořte objekt uživatele
        return User(user_data['username'], user_data['password'],
                    user_data['address'], user_data['firstname'],
                    user_data['lastname'], user_data['phonenumber'])
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.find_one({'username': username}) # Získání uživatele z MongoDB

        if user and check_password_hash(user["password"], password):  # Kontrola hesla
            user_obj = User(username=user['username'], password=user['password'],
                        address=user['address'], firstname=user['firstname'], 
                        lastname=user['lastname'], phonenumber=user['phonenumber'])
            login_user(user_obj)  # Přihlásit uživatele
            return redirect(url_for('home'))
        else:
            flash("Nesprávné uživatelské jméno nebo heslo!", 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required # Uživatel musí být přihlášen
def logout():
    logout_user()
    flash("Byl jste odhlášen!", 'success')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        address = request.form['address']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phonenumber = request.form['phonenumber']
        
        if not (username and password1 and password2 and address and firstname and lastname and phonenumber):
            flash('Všechna pole jsou povinná. Prosím, vyplňte je všechna.', 'error')
            return redirect(url_for('signup'))
        
        if password1 != password2:
            flash('Hesla se neshodují. Zkontrolujte prosím své heslo.', 'error')
            return redirect(url_for('signup'))
        
        hash_password = generate_password_hash(password1) # Hashování hesla

        user_data = { # Uložení uživatele do MongoDB
            'username': username,
            'password': hash_password,
            'address': address,
            'firstname': firstname,
            'lastname': lastname,
            'phonenumber': phonenumber
        }
        users.insert_one(user_data)
        
        flash('Registrace proběhla úspěšně!', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)

