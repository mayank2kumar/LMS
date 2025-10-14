from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)
## models

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(32), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    transactions = db.relationship('transaction', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    # so when someone tries to get the password it will raise this error.

    def __init__(self, email, username, password, is_admin):
        self.email = email
        self.username = username
        self.passhash = generate_password_hash(password)
        self.is_admin = is_admin
    def check_password(self, password):
        return check_password_hash(self.passhash, password)  

class book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_name = db.Column(db.String(32), unique=True, nullable=False)
    book_author = db.Column(db.String(32), unique=True, nullable=False)
    pub_year = db.Column(db.String(512), nullable=False)
    is_issued = db.Column(db.Boolean, default=False, nullable=False)
    total_copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(512), nullable=True)
    def __init__(self, book_name, book_author, pub_year, total_copies, available_copies, description=None):
        self.book_name = book_name
        self.book_author = book_author
        self.pub_year = pub_year
        self.total_copies = total_copies
        self.available_copies = available_copies
        self.description = description
    transactions = db.relationship('transaction', backref='book', lazy=True)

class transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issue_date = db.Column(db.String(32), nullable=False)
    return_date = db.Column(db.String(32), nullable=True)
    is_returned = db.Column(db.Boolean, default=False, nullable=False)
    due_date = db.Column(db.String(32), nullable=True)
    def __init__(self, issue_date, return_date, user_id, book_id, due_date=None, is_returned=False):
        self.issue_date = issue_date
        self.return_date = return_date
        self.user_id = user_id
        self.book_id = book_id
        self.due_date = due_date
        self.is_returned = is_returned
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)



# creeate database if not exists
with app.app_context():
    db.create_all()
    # create admin user if not exists
    if not User.query.filter_by(is_admin=True).first():
        admin = User(username='admin',password='admin',is_admin=True,email='')
        db.session.add(admin)
        db.session.commit()
        # create a default admin user if not exists
        # this is a default admin user with username and password as admin
        # it will be created at start of app when database is created
        # so no one else will be able to create admin user as it is already created