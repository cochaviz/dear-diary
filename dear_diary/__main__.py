import uvicorn

# from dear_diary.main import app

if __name__ == "__main__":
    uvicorn.run("dear_diary.main:app", host="localhost", reload=True)
