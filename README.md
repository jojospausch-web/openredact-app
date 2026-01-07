<img src="docs/logo.png" width="125" align="right" />

# OpenRedact

**Semi-automatic data anonymization for German documents.**

---

<!---[!Tests](https://github.com/openredact/openredact-app/workflows/Tests/badge.svg?branch=master)-->

[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
![Frontend Tests](https://github.com/openredact/openredact-app/workflows/Frontend%20Tests/badge.svg?branch=master)
![Backend Tests](https://github.com/openredact/openredact-app/workflows/Backend%20Tests/badge.svg?branch=master)
![Black & Flake8](https://github.com/openredact/openredact-app/workflows/Black%20&%20Flake8/badge.svg?branch=master)

_**:warning: Disclaimer :warning::**_ This is a prototype. Do not use for anything critical.

_**:warning: Note :warning::**_ This tool focuses on the text content. Metadata will not be anonymized.

## Description

This repository is the home to the OpenRedact app, a webapp for semi-automatic anonymization of German language documents.
[OpenRedact](https://openredact.org) is a [Prototype Fund](https://prototypefund.de) project, funded by the [Federal Ministry of Education and Research](https://www.bmbf.de).
A detailed description of the project and prototype can be seen [here](https://openredact.org/prototypefund).

<img src="docs/approach.png" alt="Using OpenRedact to anonymize documents" width="80%">

## CLI

You can use the CLI script `backend/cli/redact.py` to anonymize a directory of documents in an unsupervised manner.

```shell script
./redact.py --input_dir "path/to/documents/" --output_dir "out/directory/"
```

Call `./redact.py --help` for usage instructions and important notes.

## Webapp

### OpenRedact works with document file formats

This screencast walks you through the anonymization of a document, from upload to download of the anonymized file.

![](docs/end-to-end.gif "Upload a document for anonymization")

### OpenRedact supports different anonymization methods

This screencast demonstrates the different anonymization methods that OpenRedact supports.
The modifications on the left are immediately previewed on the right.

![](docs/anonymization.gif "OpenRedact supports different anonymization methods")

### OpenRedact comes with an annotation tool

The automatically detected and proposed personal data can be corrected and extended by the user using our annotation tool.

<img src="docs/annotation.png" alt="Annotate personal data inside a text" width="60%">

### OpenRedact tells you how good its automatic personal data detection is

Based on the manual corrections and extensions, we can assess the mechanism for automatic detection of personal data.

<img src="docs/scores.png" alt="Show scores and metrics for the automatic detection of personal data" width="80%">

## New Features

### Whitelist Management

OpenRedact now includes a whitelist feature that allows you to exclude specific terms from anonymization. This is particularly useful for:
- Common medical terms that should not be redacted
- Institution names that are safe to keep
- Technical terms specific to your use case

Access the whitelist manager through the filter icon in the navigation bar. You can:
- Add new entries to the whitelist
- Remove existing entries
- View all whitelisted terms

Whitelisted terms are persisted across sessions and are automatically excluded during the PII detection process.

### Template System

The template system allows you to save, load, and share anonymization configurations. This is especially useful for:
- Medical discharge letters (Entlassbriefe) with standardized anonymization requirements
- Different privacy levels (standard, high privacy, research)
- Reusing configurations across multiple documents

Access the template manager through the document icon in the navigation bar. You can:
- **Save Current Configuration**: Save your current anonymization settings as a reusable template
- **Load Medical Templates**: Quick access to predefined templates optimized for medical documents:
  - **Medical Standard**: Pseudonymization for persons, suppression for locations/organizations
  - **High Privacy**: Maximum privacy with all PIIs suppressed
  - **Research**: Optimized for research with pseudonymization and generalization
- **Import/Export**: Share templates with colleagues or backup your configurations
- **Edit Templates**: Modify template names and descriptions
- **Delete Templates**: Remove templates you no longer need

All templates are persisted in a Docker volume and remain available across container restarts.

## Deployment

The app is best deployed using Docker.

### Run the full stack using Docker-Compose

We have pre-built Docker images available at https://hub.docker.com/u/openredact.

Pull and start the containers by running:

```bash
# Clone the repo
git clone https://github.com/openredact/openredact-app.git
cd openredact-app

# Pull images & start containers
docker-compose pull
docker-compose up
```

This will host the backend at port 8000 (and http://localhost/api) and the frontend at port 80.
Once started, you can access the webapp at http://localhost/.

### Run the frontend using Docker

```bash
cd frontend
docker build -t openredact/frontend .
docker run -p 80:80 openredact/frontend
```

This will build the frontend inside a node Docker container and deploy the result in an nginx container.
For more details about this procedure see [React in Docker with Nginx, built with multi-stage Docker builds, including testing](https://medium.com/@tiangolo/react-in-docker-with-nginx-built-with-multi-stage-docker-builds-including-testing-8cc49d6ec305).

### Run the backend using Docker

```bash
cd backend
docker build -t openredact/backend .
docker run -p 8000:8000 openredact/backend
```

## API Documentation

Documentation of the API is available at the endpoints `/docs` ([Swagger UI](https://swagger.io/tools/swagger-ui/))
and `/redocs` ([ReDoc](https://redocly.github.io/redoc/)), e.g. http://127.0.0.1:8000/redoc.
The OpenAPI specification can be found [here](http://127.0.0.1:8000/openapi.json).

## Development

First, follow the instructions in the [backend](backend/README.md) or [frontend](frontend/README.md) readme.
Then, continue with the instructions below.

### Developing using Docker

If you want to use our Docker setup for development, run:

```bash
docker-compose -f docker-compose.dev.yml up
```

Don't forget to add the project's directory to the list of allowed file sharing resources in the Docker Desktop preferences.

### Install the pre-commit hooks

`pre-commit` is a Python tool to manage git pre-commit hooks.
Running the following code requires the backend dev requirements to be set up as explained [here](backend/README.md).
We have pre-commit hooks for formatting and linting Python and JavaScript code (black, flake8, prettier and eslint).
Note that the tests, being slower than formatters and linters, are run by CI.
So don't forget to run them manually before committing.

```bash
pre-commit install
git config --bool flake8.strict true  # Makes the commit fail if flake8 reports an error
```

To run the hooks:

```bash
pre-commit run --all-files
```

## How to contact us

For usage questions, bugs, or suggestions please file a Github issue.
If you would like to contribute or have other questions please email hello@openredact.org.

## License

[MIT License](https://github.com/openredact/openredact-app/blob/master/LICENSE)
