FROM python:3.12

# Set up the working directory and dependencies
WORKDIR /app
COPY requirements.lock ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

# Copy the source code into the container
COPY src .

# Run the FastAPI server on port 80 when Docker container starts
CMD ["fastapi", "run", "dear_diary/main.py", "--port", "80"]