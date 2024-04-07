# rmnt

CLI Scaffolding Tool for web applications with python

## Installation

### Using pip
To install this package, run - `pip install rmnt`

### Using source
1. Clone this repository
2. Create a virtual environment and install all the required packages using - `pip install -r requirements.txt`
3. Run the following command - `pip install -e .`

## Project Structure
```
project/
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── utils.py
│   ├── models.py
│   └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── test_utils.py
│   ├── test_app.py
├── .github/
│   └── workflows/
├── README.md
├── Dockerfile
├── LICENSE
├── .gitignore
└── .env
```

## Commands
1. `rmnt make <project-name>` - Initialize a new project
2. `rmnt --help` - Show help message
3. `rmnt --version` - Show version

## Features
1. Builds project structure for FastAPI and Flask projects
3. Creates a virtual environment
4. Initializes a git repository
