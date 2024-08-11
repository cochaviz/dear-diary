FROM python:slim

# git is needed for database
RUN apt-get update && apt-get install -y git

# Set up the working directory and dependencies
WORKDIR /app
COPY requirements.lock ./
RUN sed -i 's/-e file:\.//g' requirements.lock
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

# Copy the source code into the container
# and update the working directory
COPY src/ .
WORKDIR /app/dear_diary

# Run the FastAPI server on port 80 when Docker container starts
CMD ["fastapi", "run", "main.py", "--port", "80"]