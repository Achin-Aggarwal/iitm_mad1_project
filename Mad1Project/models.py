from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import datetime
db = SQLAlchemy(app)

class User(db.Model):
    roll_no = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    # issued_book = db.column(db.Integer)
    is_librarian = db.Column(db.Boolean, nullable=False, default = False)

    
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=True)
    create_date = db.Column(db.Date, default=datetime.date.today())

    books = db.relationship('Book', backref='section', lazy=True, cascade='all, delete-orphan')

    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    content = db.Column(db.String(256), nullable=True)
    author = db.Column(db.String(32), nullable=False)
    issue_date = db.Column(db.Date, default=datetime.date.today())
    return_date = db.Column(db.Date, default=datetime.date.today()+datetime.timedelta(days=7))

    requests = db.relationship('Request', backref  = 'book', lazy = True, cascade='all, delete-orphan')
    issued = db.relationship('Issue', backref='book', lazy=True, cascade='all, delete-orphan')
    
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.roll_no'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

class Confirmation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_roll_no = db.Column(db.Integer, db.ForeignKey('user.roll_no'), nullable=False)
    issue_date = db.Column(db.Date, default=datetime.date.today())
    return_date = db.Column(db.Date, default=datetime.date.today()+datetime.timedelta(days=7))

    issued = db.relationship('Issue', backref='confirmation', lazy=True, cascade='all, delete-orphan')

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confirmation_id = db.Column(db.Integer, db.ForeignKey('confirmation.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    issue_date = db.Column(db.Date, default=datetime.date.today())
    return_date = db.Column(db.Date, default=datetime.date.today()+datetime.timedelta(days=7))
    
    

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('user.roll_no'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    comment = db.Column(db.String(256))
    rating = db.Column(db.Integer)

    user = db.relationship('User', backref='feedbacks', lazy=True)
    book = db.relationship('Book', backref='feedbacks', lazy=True)



with app.app_context():
    db.create_all()

    librarian = User.query.filter_by(is_librarian=True).first()
    if not librarian:
        password_hash = generate_password_hash('librarian')
        librarian = User(roll_no = 100,username='Librarian', passhash=password_hash, is_librarian=True)
        
        db.session.add(librarian)
        db.session.commit()
    
    
    
    

