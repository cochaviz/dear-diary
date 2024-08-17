# Dear Diary


A small web application to keep track of a diary! My idea was to have a place where I could write down how I felt, and make it easy to learn from my experiences. Most importantly, I wanted to
make sure that I don't forget about trails and tribulations of the past, to not forget past learnt lessons!

So while this, right now, really just a place to write down my thoughts, I would like to hook this to a locally-running LLM. The idea being that if the LLM had access to this database that is my written experience of my life,
I would be able to ask how I dealt with stuff in the past, how I've changed, etc. It sounds interesting, like an actual 'second brain', but I'm not sure whether it's actually useful... Only one way to find out! 😄

| Mobile UI | Desktop UI |
| --- | --- |
| ![image](https://github.com/user-attachments/assets/0b7a82b3-ee2d-493f-9fa9-4eda5d925e73) | ![image](https://github.com/user-attachments/assets/fc3e8176-7a1a-4385-b2b5-3020d481e494) |

## Requirements and Scope

This is not something that is supposed to be run at a large scale. The requirements are as follows:

 - Run locally (local network or local host), only to be used by a single user.
 - Be able to see if diary entries changed, and revert if necessary.
 - Use least amount of services/resources possible in front- and back-end.

For this reason, I've decided to make a FastAPI app, that uses native javascript in the front-end, and a git repostory as a database. 

## Prerequisites

I can strongly recommend [`rye`](https://rye.astral.sh/) for managing python environments, but if you decide to do it the old-fashioned way, install the 
requirements with the following command:

```bash
sed -i 's/-e file:\.//g' requirements.lock && pip install -r requirements.lock
```
The reason that `sed` is used in the beginning of the command is also explained in the Dockerfile:

> When using pip to install requirements.lock, it uses the line `-e file:.` to
> determine where to find the content when installing package. However, here we
> are only installing the dependencies, so this will give an error when we run it.
> Thus, we remove it from the file

## Running

To run the project in development mode, execute the following command:

```bash
python -m dear_diary
```

## Deployment

[![Docker](https://github.com/cochaviz/dear-diary/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/cochaviz/dear-diary/actions/workflows/docker-publish.yml)

For deployment, it is easiest to run the Docker file which is automatically kept up to date (see the badge for status). Just run it using the `docker pull` and `docker run` commands, or set up a service (recommended) using `docker-compose`:

```yaml
version: '3.6'

services:
  dear-diary:
    image: ghcr.io/cochaviz/dear-diary:main
    ports:
      - "9000:80"
    volumes:
      - ./dear_diary/entries:/app/dear_diary/entries
    command: ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "80"]
```

Make sure that the folder `/app/dear_diary/entries` does not yet exist, or exists and is a valid git repository.
