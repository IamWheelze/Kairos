"""Setup script for Kairos Voice-Activated Presentation System."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="kairos",
    version="1.0.0",
    description="Voice-Activated Presentation Control System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kairos Team",
    python_requires=">=3.8",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "Flask==2.0.3",
        "numpy==1.21.2",
        "pandas==1.3.3",
        "scikit-learn==0.24.2",
        "torch==1.9.0",
        "transformers==4.11.3",
        "pydub==0.25.1",
        "SpeechRecognition==3.8.1",
        "PyYAML==5.4.1",
        "pytest==6.2.4",
        "jupyter==1.0.0",
        # Web UI dependencies
        "fastapi==0.103.2",
        "uvicorn[standard]==0.22.0",
        "jinja2==3.1.4",
        "python-multipart==0.0.6",
        "websockets==11.0.3",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.4",
            "black",
            "flake8",
        ],
        "ai": [
            "openai>=1.0.0",  # OpenAI GPT-3.5/GPT-4o support
            "requests>=2.28.0",  # Ollama local AI support
        ],
    },
    entry_points={
        "console_scripts": [
            "kairos-web=kairos.web.server:run_server",
        ],
    },
    include_package_data=True,
    package_data={
        "kairos.web": ["templates/*.html", "static/**/*"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
