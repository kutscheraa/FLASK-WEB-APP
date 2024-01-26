from flask import Flask
from flask_login import LoginManager, login_user, logout_user, login_required, current_app
from auth import load_user, authenticate, is_authenticated

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['LOGIN_DISABLED'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def user_loader(email):
    return load_user(email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if authenticate(email, password):
            user = User()
            user.id = email
            login_user(user)
            return redirect(url_for('protected'))
        else:
            return 'Invalid email or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected page'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users:
            return 'Email already exists'
        users[email] = {
            "email": email,
            "password": password,
        }
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/shopping-cart')
def login():
    return render_template('shopping-cart.html')

@app.route('/contacts')
def login():
    return render_template('contacts.html')

@app.route('/team')
def login():
    return render_template('team.html')

@app.route('/product')
def login():
    return render_template('product.html')

@app.route('/subs')
def login():
    return render_template('subs.html')

@app.route('/salads')
def login():
    return render_template('salads.html')