import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///education_system.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'py', 'html', 'css', 'js', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create default users if they don't exist
    from models import User, Class, StudentClass
    from werkzeug.security import generate_password_hash
    
    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@school.edu',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            full_name='System Administrator'
        )
        db.session.add(admin_user)
        logging.info("Default admin user created: admin/admin123")
    
    # Create demo teachers
    demo_teachers = [
        {
            'username': 'teacher1',
            'email': 'teacher1@school.edu',
            'full_name': 'Dr. Sarah Johnson',
            'password': 'teacher123'
        },
        {
            'username': 'teacher2', 
            'email': 'teacher2@school.edu',
            'full_name': 'Prof. Michael Chen',
            'password': 'teacher123'
        }
    ]
    
    for teacher_data in demo_teachers:
        if not User.query.filter_by(username=teacher_data['username']).first():
            teacher = User(
                username=teacher_data['username'],
                email=teacher_data['email'],
                full_name=teacher_data['full_name'],
                role='teacher',
                password_hash=generate_password_hash(teacher_data['password'])
            )
            db.session.add(teacher)
            logging.info(f"Demo teacher created: {teacher_data['username']}/{teacher_data['password']}")
    
    # Create demo students - 35 for Class XI and 22 for Class XII
    demo_students = []
    
    # Class XI students (35 students)
    xi_students = [
        'Aadhya Sharma', 'Aarav Patel', 'Aisha Khan', 'Akash Singh', 'Ananya Gupta',
        'Arjun Reddy', 'Avani Joshi', 'Diya Mehta', 'Harsh Agarwal', 'Ishaan Kumar',
        'Kavya Rao', 'Kiran Nair', 'Manav Shah', 'Meera Verma', 'Nisha Chandra',
        'Pranav Iyer', 'Priya Malhotra', 'Rahul Bansal', 'Riya Kapoor', 'Rohan Tiwari',
        'Saanvi Bhat', 'Sanjay Mishra', 'Shreya Pandey', 'Siddharth Jain', 'Tanvi Saxena',
        'Varun Khanna', 'Vedika Sinha', 'Vikram Goyal', 'Yash Oberoi', 'Zara Ali',
        'Dev Thakur', 'Hiya Roy', 'Kiara Bajaj', 'Neel Chopra', 'Rhea Sethi'
    ]
    
    # Class XII students (22 students)  
    xii_students = [
        'Aditi Sharma', 'Amit Kumar', 'Arya Patel', 'Deepika Singh', 'Gaurav Gupta',
        'Harini Reddy', 'Ishan Joshi', 'Jiya Mehta', 'Karthik Agarwal', 'Lavanya Rao',
        'Madhav Nair', 'Navya Shah', 'Ojas Verma', 'Pallavi Chandra', 'Qasim Khan',
        'Ravi Iyer', 'Simran Malhotra', 'Tarun Bansal', 'Urvi Kapoor', 'Vaibhav Tiwari',
        'Wisha Bhat', 'Yuvraj Mishra'
    ]
    
    # Generate student data with username as student name and password as 123456
    for i, name in enumerate(xi_students, 1):
        username = name.lower().replace(' ', '')
        demo_students.append({
            'username': username,
            'email': f'{username}@student.edu',
            'full_name': name,
            'password': '123456',
            'grade': 'XI'
        })
    
    for i, name in enumerate(xii_students, 1):
        username = name.lower().replace(' ', '')
        demo_students.append({
            'username': username,
            'email': f'{username}@student.edu', 
            'full_name': name,
            'password': '123456',
            'grade': 'XII'
        })
    
    for student_data in demo_students:
        if not User.query.filter_by(username=student_data['username']).first():
            student = User(
                username=student_data['username'],
                email=student_data['email'],
                full_name=student_data['full_name'],
                role='student',
                password_hash=generate_password_hash(student_data['password'])
            )
            db.session.add(student)
            logging.info(f"Demo student created: {student_data['username']}/{student_data['password']}")
    
    db.session.commit()
    
    # Create demo classes and assign teachers
    demo_classes = [
        {
            'name': 'XI-A',
            'grade': 'XI',
            'section': 'A',
            'teacher_username': 'teacher1'
        },
        {
            'name': 'XI-B',
            'grade': 'XI', 
            'section': 'B',
            'teacher_username': 'teacher2'
        },
        {
            'name': 'XII-A',
            'grade': 'XII',
            'section': 'A',
            'teacher_username': 'teacher1'
        },
        {
            'name': 'XII-B',
            'grade': 'XII',
            'section': 'B',
            'teacher_username': 'teacher2'
        }
    ]
    
    for class_data in demo_classes:
        if not Class.query.filter_by(name=class_data['name']).first():
            teacher = User.query.filter_by(username=class_data['teacher_username']).first()
            class_obj = Class(
                name=class_data['name'],
                grade=class_data['grade'],
                section=class_data['section'],
                teacher_id=teacher.id if teacher else None
            )
            db.session.add(class_obj)
            logging.info(f"Demo class created: {class_data['name']}")
    
    db.session.commit()
    
    # Enroll students in classes based on their grade
    xi_class_a = Class.query.filter_by(name='XI-A').first()
    xi_class_b = Class.query.filter_by(name='XI-B').first()
    xii_class_a = Class.query.filter_by(name='XII-A').first()
    xii_class_b = Class.query.filter_by(name='XII-B').first()
    
    # Get all XI and XII students
    xi_students_db = User.query.filter_by(role='student').all()
    xi_students_list = [s for s in xi_students_db if s.username in [name.lower().replace(' ', '') for name in xi_students]]
    xii_students_list = [s for s in xi_students_db if s.username in [name.lower().replace(' ', '') for name in xii_students]]
    
    # Distribute XI students evenly between XI-A and XI-B (35 students total)
    for i, student in enumerate(xi_students_list):
        class_obj = xi_class_a if i % 2 == 0 else xi_class_b  # Alternate between classes
        
        if student and class_obj:
            existing_enrollment = StudentClass.query.filter_by(
                student_id=student.id,
                class_id=class_obj.id
            ).first()
            
            if not existing_enrollment:
                enrollment = StudentClass(
                    student_id=student.id,
                    class_id=class_obj.id
                )
                db.session.add(enrollment)
                logging.info(f"Enrolled {student.username} in {class_obj.name}")
    
    # Distribute XII students evenly between XII-A and XII-B (22 students total)
    for i, student in enumerate(xii_students_list):
        class_obj = xii_class_a if i % 2 == 0 else xii_class_b  # Alternate between classes
        
        if student and class_obj:
            existing_enrollment = StudentClass.query.filter_by(
                student_id=student.id,
                class_id=class_obj.id
            ).first()
            
            if not existing_enrollment:
                enrollment = StudentClass(
                    student_id=student.id,
                    class_id=class_obj.id
                )
                db.session.add(enrollment)
                logging.info(f"Enrolled {student.username} in {class_obj.name}")
    
    db.session.commit()

# Import routes
import routes

# Initialize default data after importing routes
with app.app_context():
    routes.create_default_data()
