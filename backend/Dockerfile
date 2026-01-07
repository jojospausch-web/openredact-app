FROM python:3.8

WORKDIR /app

# Install PDF dependencies using package manager
RUN apt-get update && apt-get install -y \
    cmake \
    autoconf \
    poppler-utils \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Disable pip cache
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Dev dependencies (for testing)
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install optional packages
RUN pip install chardet

# Environment
ENV STANZA_TEST_HOME=/app/stanza_test

# Models
RUN python -m spacy download de
RUN python -c "import stanza; stanza.download('de')"

COPY ./ /app/

RUN pip install gunicorn


CMD ["gunicorn", "-b", "0.0.0.0:8000", "-t", "600", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]

EXPOSE 8000
