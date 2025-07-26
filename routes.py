from flask import render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app import app, db, allowed_file
from models import User, Class, Subject, Assignment, Submission, StudentClass, AssignmentResource, CodeSnippet
from utils import execute_python_code, requires_role
import json
import os
import uuid
from datetime import datetime

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin')
@requires_role('admin')
def admin_dashboard():
    user = User.query.get(session['user_id'])
    total_users = User.query.count()
    total_classes = Class.query.count()
    total_assignments = Assignment.query.count()
    total_submissions = Submission.query.count()
    
    return render_template('admin/dashboard.html', 
                         user=user,
                         total_users=total_users,
                         total_classes=total_classes,
                         total_assignments=total_assignments,
                         total_submissions=total_submissions)

@app.route('/admin/users')
@requires_role('admin')
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/users/create', methods=['POST'])
@requires_role('admin')
def create_user():
    username = request.form['username']
    email = request.form['email']
    full_name = request.form['full_name']
    role = request.form['role']
    password = request.form['password']
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('manage_users'))
    
    if User.query.filter_by(email=email).first():
        flash('Email already exists', 'error')
        return redirect(url_for('manage_users'))
    
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(user)
    db.session.commit()
    flash(f'User {full_name} created successfully', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/classes')
@requires_role('admin')
def manage_classes():
    classes = Class.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('admin/manage_classes.html', classes=classes, teachers=teachers)

@app.route('/admin/classes/create', methods=['POST'])
@requires_role('admin')
def create_class():
    name = request.form['name']
    grade = request.form['grade']
    section = request.form['section']
    teacher_id = request.form.get('teacher_id') or None
    
    class_obj = Class(
        name=name,
        grade=grade,
        section=section,
        teacher_id=teacher_id
    )
    
    db.session.add(class_obj)
    db.session.commit()
    flash(f'Class {name} created successfully', 'success')
    return redirect(url_for('manage_classes'))

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@requires_role('admin')
def edit_student(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Update student information
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate inputs
        if not full_name or not username:
            flash('Name and username are required.', 'error')
            return redirect(url_for('edit_student', user_id=user_id))
        
        # Check if username is already taken by another user
        existing_user = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('edit_student', user_id=user_id))
        
        # Update user information
        user.full_name = full_name
        user.username = username
        
        if email:
            user.email = email
        
        # Update password if provided
        if password:
            user.password_hash = generate_password_hash(password)
        
        try:
            db.session.commit()
            flash('Student information updated successfully!', 'success')
            return redirect(url_for('manage_users'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating student information.', 'error')
            return redirect(url_for('edit_student', user_id=user_id))
    
    return render_template('admin/edit_student.html', user=user)

@app.route('/admin/users/reset_credentials/<int:user_id>', methods=['POST'])
@requires_role('admin')
def reset_student_credentials(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.role != 'student':
        flash('This action can only be performed on student accounts.', 'error')
        return redirect(url_for('manage_users'))
    
    # Generate new credentials: username = student name (no spaces), password = 123456
    new_username = user.full_name.lower().replace(' ', '')
    new_password = '123456'
    
    # Check if username already exists
    existing_user = User.query.filter(User.username == new_username, User.id != user_id).first()
    if existing_user:
        # Add a number suffix if username exists
        counter = 1
        while existing_user:
            test_username = f"{new_username}{counter}"
            existing_user = User.query.filter(User.username == test_username, User.id != user_id).first()
            if not existing_user:
                new_username = test_username
                break
            counter += 1
    
    # Update credentials
    user.username = new_username
    user.password_hash = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        flash(f'Credentials reset for {user.full_name}. New login: {new_username} / {new_password}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error resetting credentials.', 'error')
    
    return redirect(url_for('manage_users'))

# File Upload Routes
@app.route('/assignment/<int:assignment_id>/upload_resource', methods=['POST'])
@requires_role(['teacher', 'admin'])
def upload_assignment_resource(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('teacher_assignments'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('teacher_assignments'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create upload directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Save file info to database
        resource = AssignmentResource(
            assignment_id=assignment_id,
            filename=filename,
            original_filename=file.filename,
            file_size=file_size,
            file_type=file.content_type or 'application/octet-stream',
            uploaded_by=session['user_id']
        )
        
        db.session.add(resource)
        db.session.commit()
        
        flash(f'File "{file.filename}" uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed types: txt, pdf, png, jpg, jpeg, gif, doc, docx, py, html, css, js, json', 'error')
    
    return redirect(url_for('teacher_assignments'))

@app.route('/download_resource/<int:resource_id>')
@requires_role(['teacher', 'student', 'admin'])
def download_resource(resource_id):
    resource = AssignmentResource.query.get_or_404(resource_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], resource.filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=resource.original_filename)
    else:
        flash('File not found', 'error')
        return redirect(url_for('student_dashboard'))

# Code Snippet Routes
@app.route('/snippets')
@requires_role(['teacher', 'student', 'admin'])
def code_snippets():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = CodeSnippet.query.filter_by(is_public=True)
    
    if search:
        query = query.filter(
            (CodeSnippet.title.contains(search)) |
            (CodeSnippet.description.contains(search)) |
            (CodeSnippet.tags.contains(search))
        )
    
    snippets = query.order_by(CodeSnippet.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('snippets/browse.html', snippets=snippets, search=search)

@app.route('/snippets/create', methods=['GET', 'POST'])
@requires_role(['teacher', 'student', 'admin'])
def create_snippet():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        code = request.form.get('code')
        language = request.form.get('language', 'python')
        tags = request.form.get('tags', '')
        is_public = request.form.get('is_public') == 'on'
        
        if not title or not code:
            flash('Title and code are required', 'error')
            return render_template('snippets/create.html')
        
        snippet = CodeSnippet(
            title=title,
            description=description,
            code=code,
            language=language,
            tags=tags,
            is_public=is_public,
            created_by=session['user_id']
        )
        
        db.session.add(snippet)
        db.session.commit()
        
        flash('Code snippet created successfully!', 'success')
        return redirect(url_for('view_snippet', snippet_id=snippet.id))
    
    return render_template('snippets/create.html')

@app.route('/snippets/<int:snippet_id>')
@requires_role(['teacher', 'student', 'admin'])
def view_snippet(snippet_id):
    snippet = CodeSnippet.query.get_or_404(snippet_id)
    
    # Check if user can view this snippet
    if not snippet.is_public and snippet.created_by != session['user_id']:
        flash('You do not have permission to view this snippet', 'error')
        return redirect(url_for('code_snippets'))
    
    # Increment view count
    snippet.view_count += 1
    db.session.commit()
    
    return render_template('snippets/view.html', snippet=snippet)

# Teacher Routes
@app.route('/teacher')
@requires_role('teacher')
def teacher_dashboard():
    user = User.query.get(session['user_id'])
    my_classes = Class.query.filter_by(teacher_id=user.id).all()
    my_assignments = Assignment.query.filter_by(teacher_id=user.id).all()
    
    return render_template('teacher/dashboard.html', 
                         user=user,
                         my_classes=my_classes,
                         my_assignments=my_assignments)

@app.route('/teacher/assignments')
@requires_role('teacher')
def teacher_assignments():
    user = User.query.get(session['user_id'])
    assignments = Assignment.query.filter_by(teacher_id=user.id).all()
    return render_template('teacher/assignments.html', assignments=assignments)

@app.route('/teacher/assignments/create', methods=['GET', 'POST'])
@requires_role('teacher')
def create_assignment():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        subject_id = request.form['subject_id']
        class_id = request.form['class_id']
        starter_code = request.form['starter_code']
        expected_output = request.form['expected_output']
        due_date_str = request.form['due_date']
        max_points = int(request.form['max_points'])
        
        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
        
        assignment = Assignment(
            title=title,
            description=description,
            subject_id=subject_id,
            class_id=class_id,
            teacher_id=session['user_id'],
            starter_code=starter_code,
            expected_output=expected_output,
            due_date=due_date,
            max_points=max_points,
            is_published=True
        )
        
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully', 'success')
        return redirect(url_for('teacher_assignments'))
    
    # GET request - show form
    user = User.query.get(session['user_id'])
    my_classes = Class.query.filter_by(teacher_id=user.id).all()
    subjects = Subject.query.all()
    
    return render_template('teacher/create_assignment.html', 
                         my_classes=my_classes, 
                         subjects=subjects)

# Student Routes
@app.route('/student')
@requires_role('student')
def student_dashboard():
    user = User.query.get(session['user_id'])
    
    # Get student's classes
    student_classes = db.session.query(Class).join(StudentClass).filter(
        StudentClass.student_id == user.id
    ).all()
    
    # Get assignments for student's classes
    class_ids = [sc.id for sc in student_classes]
    assignments = Assignment.query.filter(
        Assignment.class_id.in_(class_ids),
        Assignment.is_published == True
    ).all()
    
    return render_template('student/dashboard.html', 
                         user=user,
                         student_classes=student_classes,
                         assignments=assignments)

@app.route('/student/assignment/<int:assignment_id>')
@requires_role('student')
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    user = User.query.get(session['user_id'])
    
    # Check if student has access to this assignment
    student_class_ids = [sc.class_id for sc in user.student_classes]
    if assignment.class_id not in student_class_ids:
        flash('You do not have access to this assignment', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Get existing submission
    submission = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=user.id
    ).first()
    
    return render_template('student/assignment.html', 
                         assignment=assignment,
                         submission=submission)

@app.route('/student/ide')
@requires_role('student')
def python_ide():
    return render_template('student/ide.html')

@app.route('/execute_code', methods=['POST'])
def execute_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    code = request.json.get('code', '')
    assignment_id = request.json.get('assignment_id')
    
    result = execute_python_code(code)
    
    # If this is for an assignment, save the submission
    if assignment_id:
        user_id = session['user_id']
        assignment = Assignment.query.get(assignment_id)
        
        if assignment:
            # Check if submission already exists
            submission = Submission.query.filter_by(
                assignment_id=assignment_id,
                student_id=user_id
            ).first()
            
            if submission:
                # Update existing submission
                submission.code = code
                submission.output = result.get('output', '')
                submission.error_message = result.get('error', '')
                submission.execution_time = result.get('execution_time', 0)
                submission.submitted_at = datetime.now()
            else:
                # Create new submission
                submission = Submission(
                    assignment_id=assignment_id,
                    student_id=user_id,
                    code=code,
                    output=result.get('output', ''),
                    error_message=result.get('error', ''),
                    execution_time=result.get('execution_time', 0)
                )
                db.session.add(submission)
            
            db.session.commit()
    
    return jsonify(result)

# Initialize default data
def create_default_data():
    # Create default subjects
    subjects_data = [
        ('Computer Science', 'CS', 'XI'),
        ('Computer Science', 'CS', 'XII'),
        ('Mathematics', 'MATH', 'XI'),
        ('Mathematics', 'MATH', 'XII'),
        ('Physics', 'PHY', 'XI'),
        ('Physics', 'PHY', 'XII'),
    ]
    
    for name, code, grade in subjects_data:
        if not Subject.query.filter_by(name=name, grade=grade).first():
            subject = Subject(name=name, code=code, grade=grade)
            db.session.add(subject)
    
    db.session.commit()
    
    # Create demo assignments
    from datetime import datetime, timedelta
    
    # Get references to classes and subjects and teachers
    cs_subject_xi = Subject.query.filter_by(name='Computer Science', grade='XI').first()
    cs_subject_xii = Subject.query.filter_by(name='Computer Science', grade='XII').first()
    class_xi_a = Class.query.filter_by(name='XI-A').first()
    class_xi_b = Class.query.filter_by(name='XI-B').first()
    class_xii_a = Class.query.filter_by(name='XII-A').first()
    teacher1 = User.query.filter_by(username='teacher1').first()
    teacher2 = User.query.filter_by(username='teacher2').first()
    
    if cs_subject_xi and cs_subject_xii and class_xi_a and teacher1:
        demo_assignments = [
            {
                'title': 'Python Basics: Variables and Data Types',
                'description': 'Learn about Python variables, data types (int, float, string, boolean), and basic operations. Write a program that demonstrates different data types and performs basic calculations.',
                'subject_id': cs_subject_xi.id,
                'class_id': class_xi_a.id,
                'teacher_id': teacher1.id,
                'starter_code': '''# Python Basics: Variables and Data Types
# Complete the following tasks:

# Task 1: Create variables of different data types
name = ""  # Your name as a string
age = 0    # Your age as an integer
height = 0.0  # Your height as a float
is_student = False  # Boolean indicating if you are a student

# Task 2: Perform basic operations
# Calculate the area of a rectangle (length = 10, width = 5)
length = 10
width = 5
area = 0  # Calculate area here

# Task 3: Display the results
# Print all variables and the calculated area
print("Name:", name)
print("Age:", age)
print("Height:", height)
print("Is student:", is_student)
print("Rectangle area:", area)''',
                'expected_output': '''Name: Alice
Age: 16
Height: 5.6
Is student: True
Rectangle area: 50''',
                'due_date': datetime.now() + timedelta(days=7),
                'max_points': 100
            },
            {
                'title': 'Control Structures: Loops and Conditionals',
                'description': 'Practice using if-else statements and loops (for and while). Create a program that uses conditional logic and iteration to solve problems.',
                'subject_id': cs_subject_xi.id,
                'class_id': class_xi_a.id,
                'teacher_id': teacher1.id,
                'starter_code': '''# Control Structures: Loops and Conditionals
# Complete the following tasks:

# Task 1: Check if a number is even or odd
number = 15
# Write an if-else statement to check if number is even or odd

# Task 2: Print numbers from 1 to 10 using a for loop
print("Numbers 1 to 10:")
# Your for loop here

# Task 3: Find the sum of numbers from 1 to 100 using a while loop
sum_total = 0
count = 1
# Your while loop here

print("Sum of numbers 1 to 100:", sum_total)''',
                'expected_output': '''15 is odd
Numbers 1 to 10:
1 2 3 4 5 6 7 8 9 10
Sum of numbers 1 to 100: 5050''',
                'due_date': datetime.now() + timedelta(days=10),
                'max_points': 100
            }
        ]
        
        # Add assignments for XI-B class
        if class_xi_b and teacher2:
            demo_assignments.append({
                'title': 'Functions and Modules',
                'description': 'Learn to create and use functions in Python. Understand function parameters, return values, and basic module concepts.',
                'subject_id': cs_subject_xi.id,
                'class_id': class_xi_b.id,
                'teacher_id': teacher2.id,
                'starter_code': '''# Functions and Modules
# Complete the following tasks:

# Task 1: Create a function to calculate the factorial of a number
def factorial(n):
    # Your code here
    pass

# Task 2: Create a function to check if a number is prime
def is_prime(n):
    # Your code here
    pass

# Task 3: Create a function to find the maximum of three numbers
def find_max(a, b, c):
    # Your code here
    pass

# Test your functions
print("Factorial of 5:", factorial(5))
print("Is 17 prime?", is_prime(17))
print("Max of 10, 25, 15:", find_max(10, 25, 15))''',
                'expected_output': '''Factorial of 5: 120
Is 17 prime? True
Max of 10, 25, 15: 25''',
                'due_date': datetime.now() + timedelta(days=14),
                'max_points': 150
            })
        
        # Add advanced assignment for XII class
        if class_xii_a and cs_subject_xii:
            demo_assignments.append({
                'title': 'Object-Oriented Programming Basics',
                'description': 'Introduction to classes and objects in Python. Learn about attributes, methods, and basic OOP concepts.',
                'subject_id': cs_subject_xii.id,
                'class_id': class_xii_a.id,
                'teacher_id': teacher1.id,
                'starter_code': '''# Object-Oriented Programming Basics
# Complete the following tasks:

# Task 1: Create a Student class
class Student:
    def __init__(self, name, age, grade):
        # Initialize attributes
        pass
    
    def display_info(self):
        # Display student information
        pass
    
    def update_grade(self, new_grade):
        # Update the student's grade
        pass

# Task 2: Create student objects and test methods
student1 = Student("Alice", 17, "XI")
student2 = Student("Bob", 18, "XII")

# Display initial information
student1.display_info()
student2.display_info()

# Update grades and display again
student1.update_grade("XII")
student1.display_info()''',
                'expected_output': '''Student: Alice, Age: 17, Grade: XI
Student: Bob, Age: 18, Grade: XII
Student: Alice, Age: 17, Grade: XII''',
                'due_date': datetime.now() + timedelta(days=21),
                'max_points': 200
            })
        
        # Create assignments in database
        for assignment_data in demo_assignments:
            existing = Assignment.query.filter_by(
                title=assignment_data['title'],
                class_id=assignment_data['class_id']
            ).first()
            
            if not existing:
                assignment = Assignment(
                    title=assignment_data['title'],
                    description=assignment_data['description'],
                    subject_id=assignment_data['subject_id'],
                    class_id=assignment_data['class_id'],
                    teacher_id=assignment_data['teacher_id'],
                    starter_code=assignment_data['starter_code'],
                    expected_output=assignment_data['expected_output'],
                    due_date=assignment_data['due_date'],
                    max_points=assignment_data['max_points'],
                    is_published=True
                )
                db.session.add(assignment)
        
        db.session.commit()
