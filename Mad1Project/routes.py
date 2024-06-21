from flask import Flask, render_template, request, redirect, url_for, flash, session
from app import app
from models import db, User, Section, Book, Request, Confirmation, Issue, Feedback
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta



@app.route('/')
def index():
    return render_template('index.html')
        
@app.route('/main')
def main():
    user = User.query.get(session['user.roll_no'])
    if user.is_librarian:
        return redirect(url_for('librarian'))
    
    parameter = request.args.get('parameter')
    query = request.args.get('query')

    sections = Section.query.all()
    parameters = {
        'sec_name': 'Section',
        'book_name': 'Book',
        'author': 'Author '
    }

    if parameter == 'sec_name':
        sections = Section.query.filter(Section.name.ilike(f'%{query}%')).all()
        return render_template('main.html', sections=sections, parameters=parameters, query=query)
    elif parameter == 'book_name':
        return render_template('main.html', sections=sections, param=parameter, book_name=query, parameters=parameters, query=query)
    elif parameter == 'author':
        
        return render_template('main.html', secions=sections, param=parameter, author=query, parameters=parameters, query=query)


    return render_template('main.html', sections=sections, parameters=parameters)
        

@app.route('/student_register', methods=["GET"])
def student_register():
    return render_template('student_register.html')

@app.route('/student_register', methods=["POST"])
def student_register_post():
    roll_no = request.form.get('roll_no')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not roll_no or not username or not password or not confirm_password:
        print(roll_no,username,password,confirm_password)
        flash('Please fill out all fields')
        return redirect(url_for('student_register'))
    
    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('student_register'))
    
    user = User.query.filter_by(roll_no=roll_no).first()

    if user:
        flash('Username already exists')
        return redirect(url_for('student_register'))
    
    password_hash = generate_password_hash(password)
    
    new_user = User(roll_no=roll_no, username=username, passhash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('student_login'))


@app.route('/student_login', methods=["GET"])
def student_login():
    return render_template('student_login.html')

@app.route('/student_login', methods=['POST'])
def student_login_post():
    roll_no = request.form.get('roll_no')
    username = request.form.get('username')
    password = request.form.get('password')

    if not roll_no or not username or not password:
        flash('Please fill out all fields')
        return redirect(url_for('student_login'))
    
    user = User.query.filter_by(roll_no=roll_no).first()
    
    if not user:
        flash('Username does not exist')
        return redirect(url_for('student_login'))
    
    if not check_password_hash(user.passhash, password):
        flash('Incorrect password')
        return redirect(url_for('student_login'))
    
    session['user.roll_no'] = user.roll_no
    session['user.is_admin'] = False
    
    flash('Login successful')
    return redirect(url_for('main'))


@app.route('/librarian_login', methods=["GET"])
def librarian_login():
    return render_template('librarian_login.html')

@app.route('/librarian_login', methods=["POST"])
def librarian_login_post():
    roll_no = request.form.get('roll_no')
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Please fill out all fields')
        return redirect(url_for('librarian_login'))
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash('Username does not exist')
        return redirect(url_for('librarian_login'))
    
    session['user.roll_no'] = user.roll_no
    session['user.is_admin'] = True
    
    return redirect(url_for('main'))

   
@app.route('/profile' , methods=['GET'])
def profile():
    if 'user.roll_no' in session:
        user = User.query.get(session['user.roll_no'])
        return render_template('profile.html', user=user)
    else:
        flash("Please Login")
        return redirect(url_for('index'))

@app.route('/profile', methods=['POST'])
def profile_post():
    roll_no = request.form.get('roll_no')
    username = request.form.get('username')
    current_password = request.form.get('current_password')
    password = request.form.get('password')
    
    if not roll_no or not username or not current_password or not password:
       
        flash('Please fill out all fields')
        return redirect(url_for('profile'))
    
    user = User.query.get(session['user.roll_no'])
    if not check_password_hash(user.passhash, current_password):
        flash('Incorrect Password')
        return redirect(url_for('profile'))
    
    if roll_no != user.roll_no :
        new_roll_no = User.query.filter_by(roll_no=roll_no).first()
        if new_roll_no :
            flash ('Roll_No already exists')
            return redirect(url_for('profile'))

    if username != user.username :
        new_username = User.query.filter_by(username=username).first()
        if new_username :
            flash ('Username already exists')
            return redirect(url_for('profile'))    
        
    new_password_hash = generate_password_hash(password)
    user.roll_no = roll_no
    user.username = username
    user.passhash = new_password_hash
    db.session.commit()
    flash('Successfully Updated the Profile')
    return redirect(url_for('profile'))
    
@app.route('/logout')

def logout():
    if 'user.roll_no' in session:
        session.pop('user.roll_no')
        return redirect(url_for('student_login'))
    else:
        flash("Please Login")
        return redirect(url_for('index'))


def librarian_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user.roll_no' not in session:
            flash('Please login')
            return redirect(url_for('librarian_login'))
        user = User.query.get(session['user.roll_no'])
        if not user.is_librarian:
            flash('You are not authorized Librarian')
            return redirect(url_for('librarian_login'))
        return func(*args, **kwargs)
    return inner


@app.route('/librarian')
@librarian_required
def librarian():
    sections = Section.query.all()
    section_names= [section.name for section in sections]
    book_names = [len(section.books) for section in sections]
    return render_template('librarian.html',sections=sections, section_names=section_names, book_names=book_names )

@app.route('/section/add')
@librarian_required
def add_section():
    return render_template('section/add.html')

@app.route('/section/add', methods=['POST'])
@librarian_required
def add_section_post():
    name= request.form.get('name')
    description = request.form.get('description')

    section = Section(name=name, description=description)
    db.session.add(section)
    db.session.commit()

    flash('Section Added Successfully !!!')
    return redirect(url_for('librarian'))


@app.route('/section/<int:id>/')
@librarian_required
def show_section(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('librarian'))
    return render_template('section/show.html', section=section)

@app.route('/section/<int:id>/edit')
@librarian_required
def edit_section(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exists !!!')
        return redirect(url_for('librarian'))
    return render_template('section/edit.html',section=section)

@app.route('/section/<int:id>/edit', methods=['POST'])
@librarian_required
def edit_section_post(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('librarian'))
    name= request.form.get('name')
    description = request.form.get('description')
    
    if not name or not description  :
        flash('Please fill out all fields')
        return redirect(url_for('edit_section', id=id))
    section.name = name
    section.description = description
    db.session.commit()
    flash('Section updated successfully')
    return redirect(url_for('librarian'))


@app.route('/section/<int:id>/delete')
@librarian_required
def delete_section(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('librarian'))
    return render_template('section/delete.html', section=section)

@app.route('/section/<int:id>/delete', methods=['POST'])
@librarian_required
def delete_section_post(id):
    section = Section.query.get(id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('Librarian'))
    db.session.delete(section)
    db.session.commit()

    flash('Section deleted successfully')
    return redirect(url_for('librarian'))


@app.route('/book/add/<int:section_id>')
@librarian_required
def add_book(section_id):
    sections = Section.query.all()
    section = Section.query.get(section_id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('librarian'))
    return render_template('book/add.html', section=section, sections=sections)

@app.route('/book/add/', methods=['POST'])
@librarian_required
def add_book_post():
    name = request.form.get('name')
    content = request.form.get('content')
    author = request.form.get('author')
    section_id = request.form.get('section_id')
    
    section = Section.query.get(section_id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('librarian'))

    if not name or not content or not author :
        flash('Please fill out all fields')
        return redirect(url_for('add_book', section_id=section_id))
    

    book = Book(name=name, content=content, section=section, author=author)
    db.session.add(book)
    db.session.commit()

    flash('Book added successfully')
    return redirect(url_for('show_section', id=section_id))


@app.route('/book/<int:id>/edit')
@librarian_required
def edit_book(id):
    sections = Section.query.all()
    book = Book.query.get(id)
    return render_template('book/edit.html', sections=sections, book=book)

@app.route('/product/<int:id>/edit', methods=['POST'])
@librarian_required
def edit_book_post(id):
    name = request.form.get('name')
    content = request.form.get('content')
    author = request.form.get('author')
    section_id = request.form.get('section_id')
    
    section = Section.query.get(section_id)
    if not section:
        flash('Section does not exist')
        return redirect(url_for('librarian'))

    if not name or not content or not author:
        flash('Please fill out all fields')
        return redirect(url_for('add_book', section_id=section_id))
    
    book = Book.query.get(id)
    book.name = book
    book.content = content
    book.section = section
    book.author = author
    db.session.commit()

    flash('Book edited successfully')
    return redirect(url_for('show_section', id=section_id))

@app.route('/book/<int:id>/delete')
@librarian_required
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('librarian'))
    return render_template('book/delete.html', book=book)

@app.route('/book/<int:id>/delete', methods=['POST'])
@librarian_required
def delete_book_post(id):
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('librarian'))
    section_id = book.section.id
    db.session.delete(book)
    db.session.commit()

    flash('Book deleted successfully')
    return redirect(url_for('show_section', id=section_id))



@app.route('/revoke_access', methods=['POST'])
def revoke_access():
    if not session.get('user.roll_no'):
        flash('User not logged in')
        return redirect(url_for('main'))

    # Get the list of book IDs to revoke access for from the form
    book_ids = request.form.getlist('book_ids')
    
    # Query the database for the user's issued books
    issues_to_revoke = Issue.query.filter(
        Issue.confirmation.has(user_roll_no=session['user.roll_no']),
        Issue.book_id.in_(book_ids)
    ).all()

    for issue in issues_to_revoke:
        # Remove the issue entry to revoke access
        db.session.delete(issue)

    db.session.commit()

    flash('Access revoked successfully')
    return redirect(url_for('history_librarian'))



@app.route('/add_to_request/<int:book_id>', methods=['POST'])
def add_to_request(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('main'))
    

    user_roll_no = session.get('user.roll_no')
    if not user_roll_no:
        flash('User not logged in')
        return redirect(url_for('main'))

    user_requests_count = Request.query.filter_by(user_id=user_roll_no).count()
    if user_requests_count >= 5:
        flash('You cannot make more than 5 requests at a time')
        return redirect(url_for('main'))
    
    existing_request = Request.query.filter_by(user_id=user_roll_no, book_id=book_id).first()

    if existing_request:
        flash('You have already requested this book')
    else:
        new_request = Request(user_id=user_roll_no, book_id=book_id)
        db.session.add(new_request)
        db.session.commit()
        flash('Book added to cart successfully')

   
    return redirect(url_for('main'))



@app.route('/book-request')
def book_request():
    
    requests = Request.query.all()
    return render_template('request.html', requests=requests)


@app.route('/request/<int:id>/delete', methods=['POST'])
def delete_request(id):
    request = Request.query.get(id)
    if not request:
        flash('Request does not exist')
        return redirect(url_for('book_request'))
    
    db.session.delete(request)
    db.session.commit()
    flash('Request deleted successfully')
    return redirect(url_for('book_request'))



@app.route('/issue', methods=['POST'])
def issue():
    requests = Request.query.all()
    if not requests:
        flash('There are no requests')
        return redirect(url_for('book_request'))

    confirm = Confirmation(user_roll_no=session['user.roll_no'], issue_date=datetime.now())
    for request in requests:
        issue_date = datetime.now()
        return_date = issue_date + timedelta(days=7)  # Change 7 to the desired number of days

        issue = Issue(confirmation_id=request.id, book_id=request.book_id, issue_date=issue_date, return_date=return_date)
        db.session.add(issue)
        db.session.delete(request)

    # Check for overdue books and revoke access
    overdue_issues = Issue.query.filter(Issue.return_date < datetime.now()).all()
    for issue in overdue_issues:
        db.session.delete(issue)

    db.session.add(confirm)
    db.session.commit()

    flash('Book Issued')
    return redirect(url_for('history_user'))


@app.route('/history-librarian')
def history_librarian():
    confirmations = Confirmation.query.all()
    return render_template('history_librarian.html', confirmations=confirmations)



@app.route('/return-book', methods=['POST'])
def return_book():
    if not session.get('user.roll_no'):
        flash('User not logged in')
        return redirect(url_for('main'))

    # Get the list of book IDs to revoke access for from the form
    book_ids = request.form.getlist('book_ids')
    
    # Query the database for the user's issued books
    issues_to_revoke = Issue.query.filter(
        Issue.confirmation.has(user_roll_no=session['user.roll_no']),
        Issue.book_id.in_(book_ids)
    ).all()

    for issue in issues_to_revoke:
        # Remove the issue entry to revoke access
        db.session.delete(issue)

    db.session.commit()

    flash('Book returned successfully')
    return redirect(url_for('history_user'))





@app.route('/history-user')
def history_user():
    confirmations = Confirmation.query.filter_by(user_roll_no=session.get('user.roll_no')).all()
    return render_template('history_user.html', confirmations=confirmations)


@app.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        username = request.form['username']
        bookname = request.form['bookname']
        rating = request.form['rating']
        comment = request.form['comment']
        
        # Save the feedback to the database or process it as needed
        
        # For demonstration, assuming you have a Feedback model
        feedback = Feedback(user_name=username, book_name=bookname, rating=rating, comment=comment)
        db.session.add(feedback)
        db.session.commit()
        
        # Redirect to the librarian dashboard after submitting feedback
        return redirect(url_for('main'))
    else:
        return render_template('feedback.html')



