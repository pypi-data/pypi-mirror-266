import textwrap

class Content:
    
    @classmethod
    def get_gitignore_content(cls, projectname: str) -> str:
        return textwrap.dedent(f"""\
            {projectname}-env/
            .ipynb_checkpoints
            __pycache__/
            .vscode/
            .idea/
            .env
            .DS_Store
            __pypackages__/
            instance/
            .webassets-cache
            .pytest_cache/
        """)
    
class Structure:

    folders = ["src", "tests", ".github"]

    github_folders = ["workflows"]

    src_files = ["__init__.py", "app.py", "config.py", "models.py", "utils.py", "exceptions.py"]
    
    test_files = ["__init__.py", "test_app.py", "test_utils.py"]

    files = ["README.md", "Dockerfile", ".env", ".gitignore", "LICENSE"]


class Commands:
    
    @classmethod
    def get_venv_command(cls, project_name: str) -> str:
        return f"python -m venv {project_name}-env"
    
    git = "git init"

    venv_install = "pip install virtualenv"

    pytest = "pip install pytest"

    requirements = "pip freeze > requirements.txt"

class PrePostCommands:

    venv_install_pre = "Installing Virtualenv package"
    venv_install_post = "Virtualenv package installed"

    venv_create = "Virtual Environment Created!"
    
    dependencies_pre = "Installing dependencies - pytest"
    dependencies_post = "Dependencies installed"

    requirements_pre = "Creating requirements.txt file"
    requirements_post = "Requirements.txt file created"

    structure_pre = "Creating project structure"
    structure_post = "Project structure created"
    
    