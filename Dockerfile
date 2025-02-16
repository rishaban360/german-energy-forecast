FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install the project package
RUN pip install -e .

# Expose the port
EXPOSE 8050

# Command to run the dashboard
CMD ["python", "scripts/deploy_dashboard.py"] 