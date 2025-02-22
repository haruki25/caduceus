FROM python:3.12.3

# Set the working directory as current one
WORKDIR /app

COPY . .

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pathway[all]

# Expose required ports
EXPOSE 8000 8501 8502

# Define environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Start the backend and frontend services
CMD ["python", "-m", "streamlit", "run", "main.py"]
