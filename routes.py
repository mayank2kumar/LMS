from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db,User,book,transaction
from functools import wraps
from app import app

def auth_required(func):
    @wraps(func)
    # works on the base of session cokkies 
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_admin') == False:
            flash("Access Denied: Admins Only", "danger")
            return redirect(url_for('index'))  # Redirect to home if not admin
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_admin') == True:
            flash("Access Denied: Users Only", "danger")
            return redirect(url_for('index'))  # Redirect to home if not a regular user
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard_redirect():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        # Not logged in → send to login
        return redirect(url_for('login'))

    # Fetch user info
    user = User.query.get(user_id)

    # Redirect according to user type
    if user.is_admin:
        return redirect(url_for('admin_home'))
    else:
        return redirect(url_for('user_dashboard'))


# Routes for the user dashboard
@app.route('/user_dashboard')
@auth_required
@user_required
def user_dashboard():
    books = book.query.all()
    user_id = session['user_id']
    transactions = transaction.query.filter_by(user_id=user_id,is_returned=False).all()
    return render_template('user_dashboard.html', user=User.query.get(user_id), books=books, transactions=transactions)

@app.route('/borrow_book')
@auth_required
@user_required
def borrow_book():
    book_id = request.args.get('book_id')
    Book = book.query.get(book_id)
    if Book.available_copies > 0:
        Book.available_copies -= 1
        issue_date = datetime.utcnow().date()
        due_date = issue_date + timedelta(days=12)

        new_transaction = transaction(
            issue_date=issue_date,
            return_date=None,
            user_id=session['user_id'],
            book_id=Book.id,
            due_date=due_date
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash('Book borrowed successfully')
    else:
        flash('No copies available to borrow')
    return redirect(url_for('user_dashboard'))

@app.route('/return_book')
@auth_required
@user_required
def return_book():
    Book = book.query.get(request.args.get('book_id'))
    transaction_record = transaction.query.get(request.args.get('transaction_id'))
    if transaction_record and transaction_record.user_id == session['user_id']:
        Book.available_copies += 1
        transaction_record.is_returned = True
        transaction_record.return_date = datetime.utcnow().date()
        db.session.commit()
        flash('Book returned successfully')
    else:
        flash('Invalid transaction or unauthorized return attempt')
    return redirect(url_for('user_dashboard'))


@app.route('/delete_user')
@auth_required
@admin_required
def delete_user():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('user_management'))

# Routes for the admin home page

@app.route('/admin_home')
@auth_required
@admin_required
def admin_home():
    users = User.query.filter_by(is_admin=False).all()
    books = book.query.all()
    transactions = transaction.query.all()
    return render_template('admin_home.html', user=User.query.get(session['user_id']), users=users, books=books, transactions=transactions)


@app.route('/new_book')
@auth_required
@admin_required
def new_book():
    return render_template('new_book.html', user=User.query.get(session['user_id']))

@app.route('/new_book', methods=['POST'])
@auth_required
@admin_required
def new_book_post():
    book_name = request.form['book_name']
    book_author = request.form['book_author']
    pub_year = request.form['pub_year']
    total_copies = request.form['total_copies']
    available_copies = request.form['available_copies']
    description = request.form.get('description')
    Book = book(book_name=book_name, book_author=book_author, pub_year=pub_year, total_copies=total_copies, available_copies=available_copies, description=description)
    db.session.add(Book)
    db.session.commit()
    flash('Book added successfully')
    return redirect(url_for('admin_home'))

@app.route('/edit_book')
@auth_required
@admin_required
def edit_book():
    book_id = request.args.get('book_id')
    Book = book.query.get(book_id)
    return render_template('edit_book.html', book=Book)

@app.route('/edit_book', methods=['POST'])
@auth_required
@admin_required
def edit_book_post():
    book_id = request.args.get('book_id')
    book_name = request.form['book_name']
    book_author = request.form['book_author']
    pub_year = request.form['pub_year']
    total_copies = request.form['total_copies']
    available_copies = request.form['available_copies']
    description = request.form.get('description')
    existing_book = book.query.filter(book.id != book_id, book.book_name == book_name).first()
    if existing_book:
        flash('Book with the same name already exists')
        return redirect(url_for('edit_book', book_id=book_id))
    Book = book.query.get(book_id)
    Book.book_name = book_name
    Book.book_author = book_author
    Book.pub_year = pub_year
    Book.total_copies = total_copies
    Book.available_copies = available_copies
    Book.description = description
    db.session.commit()
    flash('Book updated successfully')
    return redirect(url_for('admin_home'))

@app.route('/delete_book')
@auth_required
@admin_required
def delete_book():
    book_id = request.args.get('book_id')
    Book = book.query.get(book_id)
    db.session.delete(Book)
    db.session.commit()
    flash('Book deleted successfully')
    return redirect(url_for('admin_home'))


@app.route('/login')
def login():
    if 'user_id' not in session:
        return render_template('login.html')
    else:
        flash('You are already logged in')
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if username == '' or password == '':
        flash('Username or password cannot be empty')
        return redirect(url_for('login'))
    if not user:
        flash('User does not exist')
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash('Password does not match')
        return redirect(url_for('login'))
    # login successful
    session['user_id'] = user.id
    session['is_admin'] = user.is_admin
    session['username'] = user.username
    flash('Login successful')
    if user.is_admin:
        return redirect(url_for('admin_home'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/register')
def register():
    if 'user_id' not in session:
        return render_template('register.html')
    else:
        flash('You are already logged in')
        return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register_post():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    Confirm_Password = request.form['confirm_password']
    if username != email.split('@')[0]:
        flash('Username must be the same as the email id without @gmail.com')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username=username).first()
    if user:
        flash('User with the same username already exists')
        return redirect(url_for('register'))
    
    if password != Confirm_Password:
        flash('Password does not match')
        return redirect(url_for('register'))
    
    if username == '' or password == '':
        flash('Username or password cannot be empty')
        return redirect(url_for('register'))

    user = User(email=email, username=username, password=password, is_admin=False)
    db.session.add(user)
    db.session.commit()
    flash('User registered successfully')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect(url_for('login'))

from flask import jsonify
from datetime import datetime, timedelta

@app.route('/debug')
def debug():
    return jsonify(dict(session))  # Convert session to JSON and return
