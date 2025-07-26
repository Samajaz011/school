# Education Management System

## Overview

This is a Flask-based education management system designed for high school classes (XI-XII). The system provides role-based access for administrators, teachers, and students. The platform includes user management, class management, assignment creation and submission, and an integrated Python IDE for coding assignments.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (configurable to use PostgreSQL via DATABASE_URL environment variable)
- **Authentication**: Session-based authentication with password hashing using Werkzeug
- **Code Execution**: Subprocess-based Python code execution with timeout protection

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **UI Framework**: Bootstrap 5.3.0
- **Icons**: Feather Icons
- **Fonts**: Inter (UI) and Fira Code (code editor)
- **Code Editor**: Monaco Editor for in-browser Python coding

### Database Schema
The system uses a relational database with the following key entities:
- **User**: Stores user accounts with roles (admin, teacher, student)
- **Class**: Represents school classes (XI-A, XII-B, etc.)
- **Subject**: Academic subjects with grade-specific organization
- **Assignment**: Coding assignments with descriptions and test cases
- **StudentClass**: Many-to-many relationship between students and classes
- **Submission**: Student assignment submissions with code and results

## Key Components

### User Management
- Role-based access control (admin, teacher, student)
- Default admin account creation on first run
- Password hashing for security
- Session-based authentication

### Assignment System
- Teachers can create coding assignments
- Students can submit Python code solutions
- Integrated Monaco code editor
- Code execution with safety timeouts
- Submission tracking and grading

### Python IDE
- Browser-based Python development environment
- Monaco editor with syntax highlighting
- Code execution capabilities
- Save/load functionality

### Class Management
- Grade-based organization (XI, XII)
- Section-based class divisions
- Teacher-class assignments
- Student enrollment tracking

## Data Flow

1. **Authentication Flow**: Users log in → Session created → Role-based dashboard redirect
2. **Assignment Flow**: Teacher creates assignment → Students access via dashboard → Submit code → Teacher reviews submissions
3. **Code Execution Flow**: Student writes code → Monaco editor → AJAX submission → Server-side execution → Results returned

## External Dependencies

### Frontend Libraries
- Bootstrap 5.3.0 (UI framework)
- Monaco Editor (code editing)
- Feather Icons (iconography)
- Google Fonts (typography)

### Python Packages
- Flask (web framework)
- Flask-SQLAlchemy (database ORM)
- Werkzeug (password hashing, proxy handling)
- Standard library: subprocess, tempfile, os, logging

### Code Execution
- Uses Python subprocess for safe code execution
- Temporary file creation for code isolation
- Configurable timeout protection (default 5 seconds)

## Deployment Strategy

### Development Setup
- Flask development server (main.py)
- SQLite database for local development
- Debug mode enabled
- Hot reloading support

### Production Considerations
- Environment variable configuration (SESSION_SECRET, DATABASE_URL)
- ProxyFix middleware for reverse proxy deployment
- Database connection pooling with health checks
- Configurable database backend (SQLite default, PostgreSQL via env var)

### Security Features
- Session secret key configuration
- Password hashing with Werkzeug
- Role-based access control decorators
- Code execution sandboxing with timeouts
- CSRF protection through Flask sessions

The system is designed to be easily deployable on cloud platforms like Replit, with environment variable configuration for production settings and automatic database initialization.