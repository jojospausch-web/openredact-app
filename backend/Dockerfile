FROM python:3.9-bullseye

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

# Five-stage installation to work around nerwhal's outdated torch requirement, pydantic v2 incompatibility, and numpy binary compatibility

# STAGE 1: Install numpy first (pin to v1 for spacy 3.0-3.4 binary compatibility)
RUN pip install --no-cache-dir "numpy>=1.19,<2.0"

# STAGE 2: Install PyTorch (compatible version)
RUN pip install --no-cache-dir torch==1.8.1

# STAGE 3: Install standard packages with full dependency checking
# Pin pydantic <2.0 for FastAPI 0.65.2 compatibility
RUN pip install --no-cache-dir \
    "pydantic>=1.8,<2.0" \
    fastapi==0.65.2 \
    uvicorn==0.11.7 \
    python-multipart==0.0.5 \
    click==7.1.1

# STAGE 4: Install openredact packages WITHOUT dependency checking
RUN pip install --no-cache-dir --no-deps \
    git+https://github.com/openredact/expose-text.git#egg=expose-text \
    git+https://github.com/openredact/nerwhal.git#egg=nerwhal \
    git+https://github.com/openredact/anonymizer.git#egg=or-anonymizer

# STAGE 5: Install openredact dependencies (Pydantic v1 and numpy 1.x compatible)
RUN pip install --no-cache-dir \
    "spacy>=3.0,<3.5" \
    "stanza>=1.2,<1.5" \
    flashtext

# Install optional packages and expose-text dependencies
RUN pip install --no-cache-dir \
    chardet \
    beautifulsoup4

# Environment
ENV STANZA_TEST_HOME=/app/stanza_test

# Models
RUN python -m spacy download de
RUN python -c "import stanza; stanza.download('de')"

COPY ./ /app/

RUN pip install --no-cache-dir gunicorn==20.1.0


CMD ["gunicorn", "-b", "0.0.0.0:8000", "-t", "600", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]

EXPOSE 8000
