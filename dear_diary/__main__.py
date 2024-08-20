import uvicorn

from dear_diary.config import DEV_MODE, SERVER_PORT

if __name__ == "__main__":
    uvicorn.run(
        "dear_diary.main:app",
        host="localhost",
        reload=DEV_MODE,
        port=SERVER_PORT,  # type: ignore
    )
