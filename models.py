from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, teacher, student
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationships
    taught_classes = db.relationship('Class', backref='teacher', lazy=True)
    student_classes = db.relationship('StudentClass', backref='student', lazy=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "XI-A", "XII-B"
    grade = db.Column(db.String(10), nullable=False)  # "XI" or "XII"
    section = db.Column(db.String(10), nullable=False)  # "A", "B", etc.
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationships
    students = db.relationship('StudentClass', backref='class_obj', lazy=True)
    assignments = db.relationship('Assignment', backref='class_obj', lazy=True)

class StudentClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=func.now())

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Computer Science, Mathematics, etc.
    code = db.Column(db.String(20), nullable=False)  # CS, MATH, etc.
    grade = db.Column(db.String(10), nullable=False)  # "XI" or "XII"
    
    # Relationships
    assignments = db.relationship('Assignment', backref='subject', lazy=True)

class AssignmentResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    uploader = db.relationship('User', backref=db.backref('uploaded_resources', lazy=True))

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Python specific fields
    starter_code = db.Column(db.Text, default='# Write your Python code here\n')
    expected_output = db.Column(db.Text)
    test_cases = db.Column(db.Text)  # JSON string of test cases
    
    # Assignment metadata
    due_date = db.Column(db.DateTime)
    max_points = db.Column(db.Integer, default=100)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationships
    submissions = db.relationship('Submission', backref='assignment', lazy=True)
    teacher = db.relationship('User', backref='created_assignments', lazy=True)
    resources = db.relationship('AssignmentResource', backref='assignment', lazy=True, cascade='all, delete-orphan')

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Code and results
    code = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text)
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)
    
    # Grading
    points_earned = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=func.now())
    graded_at = db.Column(db.DateTime)

class CodeSnippet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), default='python')
    tags = db.Column(db.String(500))  # Comma-separated tags
    is_public = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    view_count = db.Column(db.Integer, default=0)
    
    creator = db.relationship('User', backref=db.backref('code_snippets', lazy=True))
