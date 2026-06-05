FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies first so this layer is cached across code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app, the roster spreadsheet, and the logo
COPY . .

EXPOSE 8501

# Streamlit must bind 0.0.0.0 to be reachable from outside the container,
# and run headless so it doesn't try to open a browser inside it.
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
