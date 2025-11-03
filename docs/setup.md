# Kairos Voice-Activated Presentation System Setup Instructions

## Prerequisites

Before setting up the Kairos project, ensure you have the following installed:

- Python 3.7 or higher
- pip (Python package installer)
- Git (for version control)

## Installation Steps

1. **Clone the Repository**

   Start by cloning the Kairos repository from GitHub:

   ```bash
   git clone https://github.com/yourusername/kairos.git
   cd kairos
   ```

2. **Create a Virtual Environment**

   It is recommended to create a virtual environment to manage dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   Install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Configuration Files**

   Copy the default configuration file to create your own:

   ```bash
   cp configs/default.yaml configs/my_config.yaml
   ```

   Modify `my_config.yaml` as needed for your environment.

5. **Prepare Data**

   Place your raw audio files in the `data/raw` directory. Use the `prepare_data.py` script to preprocess the data:

   ```bash
   python scripts/prepare_data.py
   ```

6. **Run the Application**

   You can start the application using the command line interface:

   ```bash
   python src/kairos/cli.py
   ```

## Additional Information

- For detailed usage instructions, refer to the `README.md` file.
- Explore the Jupyter notebooks in the `notebooks` directory for data analysis and model training experiments.
- Check the `docs` directory for architectural details and other documentation.

## Troubleshooting

If you encounter issues during setup, please check the following:

- Ensure all dependencies are correctly installed.
- Verify that your Python version is compatible.
- Consult the `issues` section of the GitHub repository for known problems and solutions.