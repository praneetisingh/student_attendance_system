// API base URL - use Render URL in production, localhost for development
const API_BASE_URL = window.location.origin.includes('onrender.com') 
    ? window.location.origin 
    : 'https://student-attendance-api-zv6y.onrender.com';

// Check API status on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if logged in
    if (!sessionStorage.getItem('logged_in')) {
        window.location.href = '/login';
        return;
    }
    
    // Set current faculty ID
    const facultyId = sessionStorage.getItem('faculty_id') || 'F001';
    document.getElementById('current-faculty').textContent = facultyId;
    document.getElementById('faculty_id').value = facultyId;
    
    checkAPIStatus();
    
    // Mark attendance form submission
    document.getElementById('attendance-form').addEventListener('submit', handleMarkAttendance);
    
    // View report form submission
    document.getElementById('report-form').addEventListener('submit', handleViewReport);
    
    // Add student form submission
    document.getElementById('add-student-form').addEventListener('submit', handleAddStudent);
    
    // Load students list
    refreshStudentsList();
});

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tabElement = document.getElementById(`${tabName}-tab`);
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    // Add active class to clicked button
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Clear results
    const markResult = document.getElementById('mark-result');
    const reportResult = document.getElementById('report-result');
    if (markResult) markResult.classList.remove('show');
    if (reportResult) reportResult.classList.remove('show');
    
    // Refresh students list if manage tab
    if (tabName === 'manage') {
        refreshStudentsList();
    }
}

// Check API status
async function checkAPIStatus() {
    const statusDot = document.getElementById('api-status');
    const statusText = document.getElementById('api-status-text');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'API Connected';
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'API Disconnected';
    }
}

// Handle mark attendance form submission
async function handleMarkAttendance(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultDiv = document.getElementById('mark-result');
    
    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    resultDiv.classList.remove('show');
    
    // Collect form data
    const faculty_id = document.getElementById('faculty_id').value;
    const course_id = document.getElementById('course_id').value;
    
    // Collect student attendance
    const attendance_list = [];
    document.querySelectorAll('.student-row').forEach(row => {
        const select = row.querySelector('.status-select');
        const enroll_no = select.name.replace('status_', '');
        const status = select.value;
        attendance_list.push({ enroll_no, status });
    });
    
    // Prepare request
    const requestData = {
        faculty_id,
        course_id,
        attendance_list
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/mark_attendance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',  // Include cookies for session
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.className = 'result-message success show';
            resultDiv.textContent = `✅ ${data.message || 'Attendance marked successfully!'}`;
        } else {
            resultDiv.className = 'result-message error show';
            resultDiv.textContent = `❌ Error: ${data.message || 'Failed to mark attendance'}`;
        }
    } catch (error) {
        resultDiv.className = 'result-message error show';
        resultDiv.textContent = `❌ Network Error: ${error.message}`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Attendance';
    }
}

// Handle view report form submission
async function handleViewReport(event) {
    event.preventDefault();
    
    const form = event.target;
    const enroll_no = document.getElementById('enroll_no').value.trim();
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultDiv = document.getElementById('report-result');
    
    if (!enroll_no) {
        resultDiv.className = 'result-message error show';
        resultDiv.textContent = '❌ Please enter a student enrollment number';
        return;
    }
    
    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Loading...';
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Fetching report...</div>';
    resultDiv.classList.add('show');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/report/${enroll_no}`, {
            credentials: 'include'  // Include cookies for session
        });
        const data = await response.json();
        
        if (response.ok) {
            if (data.message && data.message.includes('No attendance records')) {
                resultDiv.className = 'result-message info show';
                resultDiv.innerHTML = `
                    <strong>${data.student_name}</strong><br>
                    ${data.message}
                `;
            } else {
                // Display full report
                resultDiv.className = 'result-message success show';
                resultDiv.innerHTML = generateReportHTML(data);
            }
        } else {
            resultDiv.className = 'result-message error show';
            resultDiv.textContent = `❌ Error: ${data.message || 'Failed to fetch report'}`;
        }
    } catch (error) {
        resultDiv.className = 'result-message error show';
        resultDiv.textContent = `❌ Network Error: ${error.message}`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get Report';
    }
}

// Generate HTML for attendance report
function generateReportHTML(data) {
    const { student_name, enroll_no, summary, detailed_history } = data;
    
    let historyRows = '';
    if (detailed_history && detailed_history.length > 0) {
        detailed_history.forEach(record => {
            const date = new Date(record.date).toLocaleDateString();
            historyRows += `
                <tr>
                    <td>${date}</td>
                    <td>${record.course_id}</td>
                    <td><span class="status-badge ${record.status.toLowerCase()}">${record.status}</span></td>
                </tr>
            `;
        });
    } else {
        historyRows = '<tr><td colspan="3" style="text-align: center; color: #666;">No attendance records yet</td></tr>';
    }
    
    return `
        <div class="report-container">
            <div class="report-header">
                <div>
                    <div class="report-student-name">${student_name}</div>
                    <div class="report-enroll-no">Enrollment: ${enroll_no}</div>
                </div>
            </div>
            
            <div class="report-summary">
                <div class="summary-card">
                    <div class="summary-label">Total Classes</div>
                    <div class="summary-value">${summary.total_classes}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Present</div>
                    <div class="summary-value" style="color: #28a745;">${summary.present_count}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Absent</div>
                    <div class="summary-value" style="color: #dc3545;">${summary.absent_count}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Attendance %</div>
                    <div class="summary-value">${summary.percentage}</div>
                </div>
            </div>
            
            <h3 style="margin-bottom: 15px; color: #333;">Attendance History</h3>
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Course</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${historyRows}
                </tbody>
            </table>
        </div>
    `;
}

// Handle add student form submission
async function handleAddStudent(event) {
    event.preventDefault();
    
    const form = event.target;
    const enroll_no = document.getElementById('new_enroll_no').value.trim();
    const name = document.getElementById('new_student_name').value.trim();
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultDiv = document.getElementById('add-student-result');
    
    if (!enroll_no || !name) {
        resultDiv.className = 'result-message error show';
        resultDiv.textContent = '❌ Please fill in all fields';
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Adding...';
    resultDiv.classList.remove('show');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/add_student`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',  // Include cookies for session
            body: JSON.stringify({ enroll_no, name })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.className = 'result-message success show';
            resultDiv.textContent = `✅ ${data.message}`;
            form.reset();
            // Refresh students list
            refreshStudentsList();
            // Refresh attendance form student list
            refreshAttendanceForm();
        } else {
            resultDiv.className = 'result-message error show';
            resultDiv.textContent = `❌ ${data.message || 'Failed to add student'}`;
        }
    } catch (error) {
        resultDiv.className = 'result-message error show';
        resultDiv.textContent = `❌ Network Error: ${error.message}`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Add Student';
    }
}

// Refresh students list
async function refreshStudentsList() {
    const container = document.getElementById('students-list-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/list_students`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (response.ok && data.students) {
            if (data.students.length === 0) {
                container.innerHTML = '<div class="result-message info">No students found. Add a student to get started.</div>';
            } else {
                let html = '<table class="history-table"><thead><tr><th>Enrollment Number</th><th>Name</th></tr></thead><tbody>';
                data.students.forEach(student => {
                    html += `<tr><td><strong>${student.enroll_no}</strong></td><td>${student.name}</td></tr>`;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            }
        } else {
            container.innerHTML = '<div class="result-message error">Failed to load students</div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="result-message error">Error loading students: ' + error.message + '</div>';
    }
}

// Refresh attendance form with current students
async function refreshAttendanceForm() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/list_students`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (response.ok && data.students) {
            const studentsList = document.getElementById('students-list');
            if (studentsList) {
                studentsList.innerHTML = '';
                data.students.forEach(student => {
                    const row = document.createElement('div');
                    row.className = 'student-row';
                    row.innerHTML = `
                        <span class="student-name">${student.enroll_no} - ${student.name}</span>
                        <select name="status_${student.enroll_no}" class="status-select">
                            <option value="Present">Present</option>
                            <option value="Absent">Absent</option>
                        </select>
                    `;
                    studentsList.appendChild(row);
                });
            }
        }
    } catch (error) {
        console.error('Error refreshing attendance form:', error);
    }
}

// Fix student names function
async function fixStudentNames() {
    const resultDiv = document.getElementById('fix-names-result');
    if (!resultDiv) return;
    
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Fixing names...</div>';
    resultDiv.classList.add('show');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/fix_student_names`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.className = 'result-message success show';
            resultDiv.innerHTML = `✅ ${data.message}<br>S1001: ${data.updated.S1001}<br>S1002: ${data.updated.S1002}`;
            // Refresh both lists
            refreshStudentsList();
            refreshAttendanceForm();
        } else {
            resultDiv.className = 'result-message error show';
            resultDiv.textContent = `❌ ${data.message || 'Failed to fix names'}`;
        }
    } catch (error) {
        resultDiv.className = 'result-message error show';
        resultDiv.textContent = `❌ Network Error: ${error.message}`;
    }
}

