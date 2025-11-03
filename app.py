from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from functools import wraps

# --- 1. Initialization and Configuration ---
import os
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'demo-secret-key-change-in-production')
# Configure Database - Use PostgreSQL on Render, SQLite locally
database_url = os.environ.get('DATABASE_URL', 'sqlite:///attendance_system.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Verify connections before using
    'connect_args': {'connect_timeout': 10},  # Connection timeout
    'pool_recycle': 300,  # Recycle connections after 5 minutes
}
# Initialize SQLAlchemy (lazy initialization - only connects when used)
db = SQLAlchemy(app)

# --- 2. Database Models (E-R Diagram Implementation) ---

class Student(db.Model):
    # Primary Key
    enroll_no = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    attendance_records = db.relationship('AttendanceRecord', backref='student_ref', lazy=True)

class Course(db.Model):
    # Primary Key
    course_id = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    attendance_records = db.relationship('AttendanceRecord', backref='course_ref', lazy=True)

class AttendanceRecord(db.Model):
    # Simple Primary Key
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False) # 'Present', 'Absent'

    # Foreign Keys (FKs) linking to Student and Course
    enroll_no = db.Column(db.String(20), db.ForeignKey('student.enroll_no'), nullable=False)
    course_id = db.Column(db.String(10), db.ForeignKey('course.course_id'), nullable=False)
    
    # Composite unique constraint to prevent duplicate marks for the same day/class/student
    __table_args__ = (
        db.UniqueConstraint('enroll_no', 'course_id', 'date', name='_enroll_course_date_uc'),
    )

# --- 3. Helper Functions ---

# Helper function for security (Simulated Authorization - checks SRS requirement)
def is_faculty_authorized(faculty_id, course_id):
    # All logged-in teachers are authorized (F001, T001, T002, etc.)
    # In production, this would check actual course assignments
    return faculty_id in DEMO_CREDENTIALS or faculty_id.startswith('T') or faculty_id.startswith('F')

# Simple demo authentication (for production, use proper auth library like Flask-Login)
DEMO_CREDENTIALS = {
    'F001': 'admin',   # Faculty ID: Password (Default teacher)
    'T001': 'teacher', # Teacher account
    'T002': 'teacher'  # Another teacher account
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function 

def populate_initial_data():
    # Update or create initial students
    print("Checking/updating initial data...")
    
    # Update or create S1001
    student1 = Student.query.filter_by(enroll_no='S1001').first()
    if student1:
        student1.name = 'Ananya Sharma'
        print("Updated S1001 to Ananya Sharma")
    else:
        student1 = Student(enroll_no='S1001', name='Ananya Sharma')
        db.session.add(student1)
        print("Created S1001 - Ananya Sharma")
    
    # Update or create S1002
    student2 = Student.query.filter_by(enroll_no='S1002').first()
    if student2:
        student2.name = 'Siya Singh'
        print("Updated S1002 to Siya Singh")
    else:
        student2 = Student(enroll_no='S1002', name='Siya Singh')
        db.session.add(student2)
        print("Created S1002 - Siya Singh")
    
    # Add course if not exists
    course1 = Course.query.filter_by(course_id='CS101').first()
    if not course1:
        course1 = Course(course_id='CS101', title='Computer Science Basics')
        db.session.add(course1)
        print("Added course CS101")
    
    db.session.commit()
    print("Initial data check/update complete.")

# --- 4. API Endpoints (Core Business Logic) ---

@app.route('/login', methods=['GET'])
def login():
    """Login page."""
    if session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    """Logout."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def index():
    """Serve the web interface."""
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def root():
    """Root endpoint - API information."""
    return jsonify({
        "message": "Student Attendance System API",
        "endpoints": {
            "health": "/health",
            "mark_attendance": "/api/mark_attendance (POST)",
            "view_report": "/api/report/<enroll_no> (GET)"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment status testing."""
    # Auto-initialize database on first request if not already done
    try:
        with app.app_context():
            # Test database connection first
            db.engine.connect()
            db.create_all()
            # Always update/initialize student names to ensure they're correct
            populate_initial_data()
    except Exception as e:
        error_msg = str(e)
        # Check if it's a connection issue
        if 'DATABASE_URL' in error_msg or 'connection' in error_msg.lower():
            return jsonify({
                "status": "unhealthy",
                "message": "Database connection error - check DATABASE_URL environment variable",
                "error": error_msg[:200]  # Limit error message length
            }), 503
        else:
            return jsonify({
                "status": "unhealthy",
                "message": "Database error",
                "error": error_msg[:200]
            }), 503
    
    return jsonify({
        "status": "healthy",
        "message": "Student Attendance System API is running",
        "database": "connected"
    }), 200

@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance_api():
    """Implements REQ-5: Mark Daily Attendance with UPDATE/INSERT logic (Faculty role)."""
    data = request.get_json()
    faculty_id = data.get('faculty_id')
    course_id = data.get('course_id')
    attendance_list = data.get('attendance_list', [])
    today_date = date.today() 
    
    # 1. Authorization Check
    if not is_faculty_authorized(faculty_id, course_id):
        return jsonify({"message": "Authorization failed. Faculty not assigned."}), 403

    processed_count = 0
    
    # 2. Loop through the list
    for entry in attendance_list:
        enroll_no = entry.get('enroll_no')
        status = entry.get('status')
        
        # 3. Check for existing record (UPDATE vs. INSERT logic from Sequence Diagram)
        existing_record = AttendanceRecord.query.filter_by(
            enroll_no=enroll_no,
            course_id=course_id,
            date=today_date
        ).first()

        if existing_record:
            # Alternative Flow: UPDATE (Correction)
            existing_record.status = status
            db.session.add(existing_record)
        else:
            # Normal Flow: INSERT (New Record)
            new_record = AttendanceRecord(
                enroll_no=enroll_no,
                course_id=course_id,
                status=status
            )
            db.session.add(new_record)
        
        processed_count += 1

    try:
        db.session.commit() 
        return jsonify({"message": f"Attendance marked successfully for {processed_count} students."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error during DB transaction: {str(e)}"}), 500


@app.route('/api/report/<string:enroll_no>', methods=['GET'])
def view_attendance_report(enroll_no):
    """Implements View Attendance Report (Student role), fetching history and calculating percentage."""
    
    student = Student.query.filter_by(enroll_no=enroll_no).first()
    if not student:
        return jsonify({"message": f"Error: Student {enroll_no} not found."}), 404

    # 1. Fetch all attendance records for the student
    all_records = AttendanceRecord.query.filter_by(enroll_no=enroll_no).all()
    
    if not all_records:
        return jsonify({
            "student_name": student.name,
            "message": "No attendance records found yet."
        }), 200

    # 2. Calculation Logic
    total_classes = len(all_records)
    present_count = 0
    detailed_records = []

    for record in all_records:
        if record.status.lower() == 'present':
            present_count += 1
        
        detailed_records.append({
            "date": record.date.strftime('%Y-%m-%d'),
            "course_id": record.course_id,
            "status": record.status
        })
    
    # Calculate Percentage 
    attendance_percentage = (present_count / total_classes) * 100 if total_classes > 0 else 0

    # 3. Return the structured report
    return jsonify({
        "student_name": student.name,
        "enroll_no": enroll_no,
        "summary": {
            "total_classes": total_classes,
            "present_count": present_count,
            "absent_count": total_classes - present_count,
            "percentage": f"{attendance_percentage:.2f}%" 
        },
        "detailed_history": detailed_records
    }), 200

@app.route('/api/login', methods=['POST'])
def login_api():
    """Simple demo login endpoint."""
    data = request.get_json()
    faculty_id = data.get('faculty_id')
    password = data.get('password')
    
    if faculty_id in DEMO_CREDENTIALS and DEMO_CREDENTIALS[faculty_id] == password:
        session['logged_in'] = True
        session['faculty_id'] = faculty_id
        return jsonify({
            "success": True,
            "message": "Login successful",
            "faculty_id": faculty_id
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Invalid Faculty ID or Password"
        }), 401

@app.route('/api/add_student', methods=['POST'])
@login_required
def add_student_api():
    """Add a new student to the system."""
    data = request.get_json()
    enroll_no = data.get('enroll_no')
    name = data.get('name')
    
    if not enroll_no or not name:
        return jsonify({"message": "Enrollment number and name are required"}), 400
    
    # Check if student already exists
    existing_student = Student.query.filter_by(enroll_no=enroll_no).first()
    if existing_student:
        return jsonify({"message": f"Student with enrollment number {enroll_no} already exists"}), 409
    
    try:
        new_student = Student(enroll_no=enroll_no, name=name)
        db.session.add(new_student)
        db.session.commit()
        return jsonify({
            "message": f"Student {name} ({enroll_no}) added successfully",
            "student": {
                "enroll_no": enroll_no,
                "name": name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding student: {str(e)}"}), 500

@app.route('/api/list_students', methods=['GET'])
@login_required
def list_students_api():
    """Get list of all students."""
    try:
        students = Student.query.all()
        students_list = [{"enroll_no": s.enroll_no, "name": s.name} for s in students]
        return jsonify({
            "students": students_list,
            "count": len(students_list)
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching students: {str(e)}"}), 500

@app.route('/api/list_courses', methods=['GET'])
@login_required
def list_courses_api():
    """Get list of all courses."""
    try:
        courses = Course.query.all()
        courses_list = [{"course_id": c.course_id, "title": c.title} for c in courses]
        return jsonify({
            "courses": courses_list,
            "count": len(courses_list)
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching courses: {str(e)}"}), 500

@app.route('/api/update_student', methods=['POST'])
@login_required
def update_student_api():
    """Update an existing student's information."""
    data = request.get_json()
    enroll_no = data.get('enroll_no')
    name = data.get('name')
    
    if not enroll_no:
        return jsonify({"message": "Enrollment number is required"}), 400
    
    try:
        student = Student.query.filter_by(enroll_no=enroll_no).first()
        if not student:
            return jsonify({"message": f"Student with enrollment number {enroll_no} not found"}), 404
        
        if name:
            student.name = name
        
        db.session.commit()
        return jsonify({
            "message": f"Student {enroll_no} updated successfully",
            "student": {
                "enroll_no": student.enroll_no,
                "name": student.name
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating student: {str(e)}"}), 500

@app.route('/api/fix_student_names', methods=['POST'])
@login_required
def fix_student_names_api():
    """Fix/update student names to correct ones."""
    try:
        # Update S1001 if exists
        student1 = Student.query.filter_by(enroll_no='S1001').first()
        if student1:
            student1.name = 'Ananya Sharma'
        
        # Update S1002 if exists
        student2 = Student.query.filter_by(enroll_no='S1002').first()
        if student2:
            student2.name = 'Siya Singh'
        
        db.session.commit()
        return jsonify({
            "message": "Student names updated successfully",
            "updated": {
                "S1001": "Ananya Sharma",
                "S1002": "Siya Singh"
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating names: {str(e)}"}), 500


# --- 5. Application Execution Block ---

if __name__ == '__main__':
    # Context required to interact with the Flask app
    with app.app_context():
        # Creates the database file and all tables
        db.create_all() 
        # Always update student names to ensure they're correct
        populate_initial_data() 
    
    print("Database structure and initial data prepared. Starting Flask app...")
    app.run(debug=True)
    
# Auto-update student names on app startup (for production)
@app.before_first_request
def update_student_names_on_startup():
    """Update student names when app starts."""
    with app.app_context():
        try:
            populate_initial_data()
        except Exception as e:
            print(f"Warning: Could not update student names on startup: {e}")