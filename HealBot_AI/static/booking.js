// Booking.js - Handles Appointment Submission and Token Generation

// Simulated database using localStorage
class AppointmentDatabase {
    constructor() {
        this.appointments = JSON.parse(localStorage.getItem('appointments')) || [];
    }

    addAppointment(appointment) {
        this.appointments.push(appointment);
        localStorage.setItem('appointments', JSON.stringify(this.appointments));
    }

    generateToken() {
        // Generate a unique token based on current appointments
        const today = new Date().toISOString().split('T')[0];
        const todayAppointments = this.appointments.filter(
            app => app.date === today
        ).length;
        return `HB-${today.replace(/-/g, '')}-${(todayAppointments + 1).toString().padStart(3, '0')}`;
    }
}

// Initialize database
const db = new AppointmentDatabase();

// Event listener for form submission
document.getElementById('appointmentForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Collect form data
    const appointment = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        date: document.getElementById('date').value,
        doctor: document.getElementById('doctor').value,
        bookingTimestamp: new Date().toISOString()
    };

    // Generate and display token
    const token = db.generateToken();

    // Store appointment
    db.addAppointment({...appointment, token});

    // Display token to user
    const tokenDisplay = document.getElementById('tokenDisplay');
    tokenDisplay.innerHTML = `
        <p>Appointment Booked Successfully!</p>
        <p>Your Token Number: <strong>${token}</strong></p>
        <p>Please save this token for your records.</p>
    `;

    // Reset form
    this.reset();
});

// Optional: Validate date to prevent past date selection
document.getElementById('date').min = new Date().toISOString().split('T')[0];