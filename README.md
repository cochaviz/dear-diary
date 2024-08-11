# dear-diary


## Running

To run the project in development mode, execute the following command:

```bash
cd src/dear_diary && fastapi dev main.py
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
    environment:
      - PYTHONDONTWRITEBYTECODE=1
    command: ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "80"]
```
