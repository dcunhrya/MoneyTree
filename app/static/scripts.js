// Function to simulate sensor readings
function generateSensorData() {
    return {
        temperature: 20 + Math.random() * 8,  // 20-28°C
        humidity: 40 + Math.random() * 20,    // 40-60%
        light: 500 + Math.random() * 500      // 500-1000 lux
    };
}

// Function to update the UI
function updateUI(data) {
    // Update sensor values and colors
    const sensors = ['temperature', 'humidity', 'light'];
    sensors.forEach(sensor => {
        // Update value
        document.getElementById(`${sensor}-value`).textContent = 
            data.sensor_data[sensor].toFixed(1);
        
        // Update status color
        const box = document.getElementById(`${sensor}-box`);
        box.classList.remove('status-good', 'status-ok', 'status-bad');
        box.classList.add(`status-${data.status[sensor]}`);
    });

    // Update personality if new one is provided
    if (data.personality) {
        document.getElementById('personality-text').textContent = data.personality;
        document.getElementById('update-time').textContent = 
            `Last updated: ${new Date().toLocaleTimeString()}`;
    }
}

// Function to send sensor data to server
function sendSensorData() {
    const sensorData = generateSensorData();
    
    fetch('/api/sensor-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(sensorData)
    })
    .then(response => response.json())
    .then(data => updateUI(data))
    .catch(error => console.error('Error:', error));
}

// Start sending sensor data every second
// setInterval(sendSensorData, 1000);