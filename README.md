#  ShrutiLaya

ShrutiLaya is a Python-based application for audio analysis and visualization.


# Requirements

 Python 3.13+ or 3.14+
 Recommended IDE: VS Code

# Installation

Install the required dependencies using pip:

```bash
pip install numpy plotly pyttsx3 sniffio pydub scipy streamlit google-generativeai google-genai
```

# Setup

1. Create a project folder.

2. Clone or download this repository:

   ```bash
   git clone https://github.com/patilpranjal8722/shabda_vani.git
   ```

3. Move into the project directory:

   ```bash
   cd shabda_vani
   ```

4. Ensure the following files are present:

   * `analyzer.py`
   * `app.py`

# Configuration

Create a file named `config.py` in the project folder and add your API keys:

```python
API_KEY = "your_api_key_here"
```

# Running the Application

Run the analyzer:

```bash
python analyzer.py
```

Then start the Streamlit app:

```bash
python -m streamlit run app.py
```

# Output

* A web page will automatically open in your browser.
* Interact with the app and explore the features.


# Notes

* Make sure you are inside the project directory before running commands.
* Use a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
```

# Enjoy!

Explore ShrutiLaya and experience audio analysis in action 🎶

