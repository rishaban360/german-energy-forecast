# Energy Forecast Dashboard

<div class="dashboard-container">
    <div id="forecast-plot"></div>
    <div class="stats-panel">
        <p id="last-updated">Last updated: Loading...</p>
        <!-- Other stats -->
    </div>
</div>

<script src="assets/js/dashboard.js"></script>

## Live Energy Consumption

<div class="dashboard-container">
    <iframe
        src="https://german-energy-dashboard.onrender.com"
        width="100%"
        height="500px"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope"
    ></iframe>
</div>

## Understanding the Dashboard

- **Blue Line**: Actual Load [MW]
- **Orange Line**: ENTSO-E's Day-Ahead Forecast [MW]
- **Vertical Red Line**: Current Time

Updates every 5 minutes with latest ENTSO-E data.

<div class="dashboard-stats">
    <div id="last-updated">Loading...</div>
    <div class="stats-grid">
        <div class="stat-box">
            <h3>Current Load</h3>
            <span id="current-load">Loading...</span>
        </div>
        <div class="stat-box">
            <h3>Forecasted Load</h3>
            <span id="forecast-load">Loading...</span>
        </div>
        <div class="stat-box">
            <h3>24h Maximum Load</h3>
            <span id="max-load">Loading...</span>
        </div>
        <div class="stat-box">
            <h3>24h Minimum Load</h3>
            <span id="min-load">Loading...</span>
        </div>
    </div>
</div>

<style>
.dashboard-container {
    margin: 20px 0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dashboard-stats {
    margin: 20px 0;
    padding: 20px;
    background: #1f2630;
    border-radius: 8px;
    color: white;
}

#last-updated {
    text-align: right;
    margin-bottom: 20px;
    color: #718096;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.stat-box {
    background: #2d3748;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}

.stat-box h3 {
    margin: 0 0 10px 0;
    color: #a0aec0;
    font-size: 0.9em;
}

.stat-box span {
    font-size: 1.5em;
    font-weight: bold;
    color: #ffffff;
}
</style>

<script>
async function updateStats() {
    try {
        const response = await fetch('http://localhost:8050/api/latest-forecast');
        const data = await response.json();
        
        // Update stats
        document.getElementById('current-load').textContent = 
            `${Math.round(data.actual_load[data.actual_load.length-1]).toLocaleString()} MW`;
        document.getElementById('forecast-load').textContent = 
            `${Math.round(data.forecast_load[data.forecast_load.length-1]).toLocaleString()} MW`;
        document.getElementById('max-load').textContent = 
            `${Math.round(Math.max(...data.actual_load)).toLocaleString()} MW`;
        document.getElementById('min-load').textContent = 
            `${Math.round(Math.min(...data.actual_load)).toLocaleString()} MW`;
            
        // Update timestamp
        const now = new Date();
        document.getElementById('last-updated').textContent = 
            `Last updated: ${now.toLocaleString()}`;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update stats every 5 minutes
document.addEventListener('DOMContentLoaded', () => {
    updateStats();
    setInterval(updateStats, 5 * 60 * 1000);
});
</script>

## Technical Implementation

This dashboard is built using:

- Plotly for visualization
- ENTSO-E API for real-time data
- Python Flask for backend
- Automated updates every 5 minutes
