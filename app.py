from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date

# --- 1. Initialization and Configuration ---
app = Flask(__name__)
# Configure Database (SQLite for local development)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    # For a simple demo, we assume faculty F001 is authorized for all courses
    return faculty_id == 'F001' 

def populate_initial_data():
    if not Student.query.first():
        print("Inserting initial data...")
        
        # Add two test students and one course
        student1 = Student(enroll_no='S1001', name='Alice Smith')
        student2 = Student(enroll_no='S1002', name='Bob Johnson')
        course1 = Course(course_id='CS101', title='Computer Science Basics')
        
        db.session.add_all([student1, student2, course1])
        db.session.commit()
        print("Initial students and course added.")
    else:
        print("Initial data already present.")

# --- 4. API Endpoints (Core Business Logic) ---

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


# --- 5. Application Execution Block ---

if __name__ == '__main__':
    # Context required to interact with the Flask app
    with app.app_context():
        # Creates the database file and all tables
        db.create_all() 
        # Populates initial student/course data
        populate_initial_data() 
    
    print("Database structure and initial data prepared. Starting Flask app...")
    app.run(debug=True)