async function updateDashboard() {
  try {
    const response = await fetch(
      "https://your-api.render.com/api/latest-forecast"
    );
    const data = await response.json();

    // Update the plot with new data
    Plotly.update("forecast-plot", {
      x: [[...timestamps], [...timestamps], [...timestamps]],
      y: [data.actual_load, data.entsoe_forecast, data.model_forecast],
    });

    // Update stats
    document.getElementById("last-updated").textContent = new Date(
      data.timestamp
    ).toLocaleString();
  } catch (error) {
    console.error("Error updating dashboard:", error);
  }
}

// Update every 5 minutes
setInterval(updateDashboard, 5 * 60 * 1000);
