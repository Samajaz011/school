import subprocess
import sys
import os
import tempfile
import time
from functools import wraps
from flask import session, redirect, url_for, flash

def requires_role(role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page', 'error')
                return redirect(url_for('login'))
            
            if session.get('user_role') != role:
                flash('Access denied', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def execute_python_code(code, timeout=5):
    """
    Execute Python code safely and return the result
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        start_time = time.time()
        
        # Execute the code
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()
        )
        
        execution_time = time.time() - start_time
        
        # Clean up
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout,
                'execution_time': execution_time
            }
        else:
            return {
                'success': False,
                'error': result.stderr,
                'execution_time': execution_time
            }
            
    except subprocess.TimeoutExpired:
        if 'temp_file' in locals():
            os.unlink(temp_file)
        return {
            'success': False,
            'error': f'Code execution timed out after {timeout} seconds'
        }
    except Exception as e:
        if 'temp_file' in locals():
            os.unlink(temp_file)
        return {
            'success': False,
            'error': f'Execution error: {str(e)}'
        }

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M')
    return 'N/A'

# Register template filters
from app import app

@app.template_filter('datetime')
def datetime_filter(dt):
    return format_datetime(dt)

@app.template_filter('timeago')
def timeago_filter(dt):
    """Simple time ago filter"""
    if not dt:
        return 'Never'
    
    from datetime import datetime
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f'{diff.days} days ago'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} hours ago'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} minutes ago'
    else:
        return 'Just now'
