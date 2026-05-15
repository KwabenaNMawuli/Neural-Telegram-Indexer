# Build context is the project root (set by docker-compose) so this Dockerfile
# can COPY both scraper/ and shared/ into the image.

FROM python:3.13-slim

# Logs flush to stdout immediately (so `docker compose logs -f` works in real time).
# No .pyc files in the image. No pip cache or version-check noise.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python deps FIRST, as a separate layer. Docker caches this layer
# and only re-runs it when requirements.txt changes — so editing source code
# triggers a fast rebuild, not a fresh pip install.
COPY scraper/requirements.txt /app/scraper/requirements.txt
RUN pip install -r /app/scraper/requirements.txt

# Now copy the rest of the project. .dockerignore keeps venv, __pycache__,
# .sessions, .state.json, etc. out of the image.
COPY scraper/ /app/scraper/
COPY shared/  /app/shared/

# main.py uses sibling-module imports (`from client import ...`), so the
# working directory at runtime must BE the scraper directory.
WORKDIR /app/scraper

CMD ["python", "main.py"]
