// API base URL - use Render URL in production, localhost for development
const API_BASE_URL = window.location.origin.includes('onrender.com') 
    ? window.location.origin 
    : 'https://student-attendance-api-zv6y.onrender.com';

// Check API status on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAPIStatus();
    
    // Mark attendance form submission
    document.getElementById('attendance-form').addEventListener('submit', handleMarkAttendance);
    
    // View report form submission
    document.getElementById('report-form').addEventListener('submit', handleViewReport);
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
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Clear results
    document.getElementById('mark-result').classList.remove('show');
    document.getElementById('report-result').classList.remove('show');
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
        const response = await fetch(`${API_BASE_URL}/api/report/${enroll_no}`);
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

