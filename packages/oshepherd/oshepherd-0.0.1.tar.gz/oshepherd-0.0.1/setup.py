from setuptools import setup, find_packages

setup(
    name="oshepherd",
    version="0.0.1",
    description="The Oshepherd guiding the Ollama(s) inference orchestration.",
    packages=find_packages(),
    install_requires=[
        "flask",
        "celery",
        "click",
        "ollama",
        "amqp",
        "redis",
        "pydantic",
        "pytest",
        "python-dotenv",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "oshepherd=oshepherd.cli:main",
        ]
    },
    author="mnemonica.ai",
    author_email="info@mnemonica.ai",
)
