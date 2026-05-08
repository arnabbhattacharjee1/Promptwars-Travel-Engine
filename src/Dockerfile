# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
# We use /app as the root of our project
WORKDIR /app

# Copy the requirements file from the backend directory
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend, frontend, and docs directories
# This ensures the relative paths in the code (e.g. static files and docs) remain valid
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY docs/ ./docs/

# Expose the port FastAPI is running on
EXPOSE 8000

# Set Environment Variables
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ID=promptwars-gurgaon

# Command to run the application
# We use -m backend.main to ensure proper module resolution
CMD ["python", "-m", "backend.main"]
