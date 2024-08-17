FROM python:slim

# git is needed for database
RUN apt-get update && apt-get install -y git

# Set up the working directory and dependencies
WORKDIR /app
COPY requirements.lock ./

# When using pip to install requirements.lock, it uses the line `-e file:.` to
# determine where to find the content when installing package. However, here we
# are only installing the dependencies, so this will give an error when we run it.
# Thus, we remove it from the file
RUN sed -i 's/-e file:\.//g' requirements.lock
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

# Copy the source code into the container
# and update the working directory
COPY dear_diary /app/dear_diary
WORKDIR /app/dear_diary

# Run the FastAPI server on port 80 when Docker container starts
CMD ["fastapi", "run", "main.py", "--port", "80"]