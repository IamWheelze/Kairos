# Kairos Voice-Activated Presentation System

## Overview
Kairos is a Voice-Activated Presentation System designed to facilitate seamless presentations through voice commands. This project integrates automatic speech recognition (ASR) and natural language processing (NLP) to interpret user commands and control presentation software effectively.

## Project Structure
The project is organized into several key directories and modules:

- **src/kairos**: Contains the main application code, including core functionalities, audio processing, ASR, NLP, and presentation control.
- **notebooks**: Jupyter notebooks for exploratory data analysis and training experimentation.
- **data**: Directories for raw and processed audio files.
- **models**: Stores model checkpoints and exported models.
- **experiments**: Configuration and notes for experiments conducted during development.
- **scripts**: Python scripts for data preparation, training, and evaluation.
- **tests**: Unit and integration tests to ensure code quality and functionality.
- **configs**: Configuration files for different environments.
- **docs**: Documentation for architecture, setup, and checkpoints.
- **ci**: Continuous integration configuration.

## Installation
To set up the Kairos project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd Kairos
pip install -r requirements.txt
```

## Usage
To run the application, use the command line interface:

```bash
python src/kairos/cli.py
```

Follow the prompts to interact with the Voice-Activated Presentation System.

### Configuration
- Default settings live in `configs/default.yaml`.
- To use an HTTP presentation backend, set `presentation.client: http` and configure `presentation.http.base_url` and `routes`. See `configs/propresenter.example.yaml`.
- You can pass a config at startup:

```bash
python src/kairos/cli.py --start --config configs/propresenter.example.yaml
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
Special thanks to the contributors and the open-source community for their support and resources.

## Requirements Docs
- Functional Requirements Document: `docs/frd.md`
- Requirements Traceability Matrix: `docs/requirements_traceability.md`
