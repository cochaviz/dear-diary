# Run the FastAPI server on port 80 when Docker container starts
FROM python:slim
RUN --mount=source=dist,target=/dist PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir /dist/*.whl
CMD python -m dear_diary.server