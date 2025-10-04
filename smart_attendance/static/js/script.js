// Update attendance statistics
async function updateStats() {
    try {
        const response = await fetch('/api/attendance');
        const data = await response.json();
        
        // Calculate today's attendance
        const today = new Date().toISOString().split('T')[0];
        const todayCount = data.filter(record => record.Date === today).length;
        
        document.getElementById('today-count').textContent = todayCount;
        
        // Calculate unique students (simplified)
        const uniqueStudents = new Set(data.map(record => record.Name)).size;
        document.getElementById('total-students').textContent = uniqueStudents;
        
    } catch (error) {
        console.error('Error fetching attendance data:', error);
    }
}

// Load attendance records
async function loadAttendance() {
    try {
        const response = await fetch('/api/attendance');
        const data = await response.json();
        
        const tbody = document.getElementById('attendance-body');
        tbody.innerHTML = '';
        
        data.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.Name}</td>
                <td>${record.Date}</td>
                <td>${record.Time}</td>
                <td class="status-${record.Status.toLowerCase()}">${record.Status}</td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error loading attendance:', error);
    }
}

// Export attendance to CSV
function exportAttendance() {
    // This would typically make a request to generate and download a CSV file
    alert('Export feature would be implemented here');
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Update stats every 30 seconds
    updateStats();
    setInterval(updateStats, 30000);
    
    // Load attendance if on attendance page
    if (document.getElementById('attendance-body')) {
        loadAttendance();
    }
});