import uvicorn

from dear_diary.main import app

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
