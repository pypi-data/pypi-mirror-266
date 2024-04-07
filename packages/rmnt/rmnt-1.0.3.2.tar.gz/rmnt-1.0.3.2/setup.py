from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-16") as fh:
    requirements = fh.read()
setup(
    name = 'rmnt',
    version = '1.0.3.2',
    author = 'Raghu Ram Jee Janapareddy',
    author_email = 'ramjeeraghu@gmail.com',
    license = 'MIT License',
    description = 'CLI Scaffolding Tool for web projects with Flask and FastAPI',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/raghuramjee7/rmnt',
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'rmnt = app:cli',
        ],
    },
)