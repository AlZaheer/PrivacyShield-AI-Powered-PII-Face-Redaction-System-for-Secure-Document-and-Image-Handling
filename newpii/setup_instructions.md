# VS Code Setup Instructions for PII De-identification App

## Prerequisites
- VS Code installed
- Python 3.8+ installed on your system
- Git (optional, for version control)

## Step-by-Step Setup

### 1. Create Project Folder
```bash
# Create a new folder for your project
mkdir pii-deidentifier-app
cd pii-deidentifier-app
```

### 2. Open in VS Code
```bash
# Open the folder in VS Code
code .
```

### 3. Set Up Python Virtual Environment

**Option A: Using VS Code Command Palette**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Python: Create Environment"
3. Select "Venv"
4. Choose your Python interpreter
5. Select `requirements.txt` when prompted

**Option B: Using Terminal in VS Code**
```bash
# Open terminal in VS Code (Ctrl+` or View > Terminal)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
# Make sure your virtual environment is activated
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### 5. Install System Dependencies

**Windows:**
- Download and install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- Add Poppler bin folder to your PATH
- Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

**macOS:**
```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install poppler tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr
```

### 6. Install Recommended VS Code Extensions

The `.vscode/extensions.json` file will prompt you to install:
- Python (Microsoft)
- Pylance (Microsoft)
- Black Formatter (Microsoft)
- Jupyter (Microsoft)
- Ruff (Charlie Marsh)

### 7. Run the Application

**Method 1: Using VS Code Debugger**
1. Press `F5` or go to Run > Start Debugging
2. Select "Run Streamlit App" configuration
3. Your app will open in the browser at `http://localhost:8501`

**Method 2: Using Terminal**
```bash
# In VS Code terminal with venv activated
streamlit run app.py
```

**Method 3: Using VS Code Tasks**
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Run Streamlit App"

## VS Code Features You'll Love

### 1. Integrated Debugging
- Set breakpoints in your Python code
- Step through PII detection logic
- Inspect variables during face detection

### 2. IntelliSense & Auto-completion
- Smart code completion for Streamlit, OpenCV, and Presidio
- Type hints and documentation on hover
- Import suggestions

### 3. Integrated Terminal
- Run commands without leaving VS Code
- Multiple terminal instances
- Virtual environment integration

### 4. Git Integration
- Built-in version control
- Visual diff viewer
- Commit and push directly from VS Code

### 5. Extensions for Enhanced Development
- **Python**: Full Python language support
- **Pylance**: Advanced Python language server
- **Black Formatter**: Automatic code formatting
- **Jupyter**: For data analysis notebooks

## Useful VS Code Shortcuts

- `Ctrl+Shift+P`: Command Palette
- `Ctrl+``: Toggle Terminal
- `F5`: Start Debugging
- `Ctrl+Shift+F`: Search across files
- `Ctrl+P`: Quick file open
- `Ctrl+Shift+E`: Explorer panel
- `Ctrl+J`: Toggle panel (terminal, problems, etc.)

## Troubleshooting

### Virtual Environment Issues
```bash
# If VS Code doesn't detect your virtual environment
# Press Ctrl+Shift+P and type "Python: Select Interpreter"
# Choose the interpreter from your venv folder
```

### Import Errors
```bash
# Make sure all dependencies are installed
pip list
pip install -r requirements.txt --upgrade
```

### Streamlit Not Found
```bash
# Ensure virtual environment is activated
# Check if streamlit is installed
pip show streamlit
```

### System Dependencies Missing
- Windows: Ensure Poppler and Tesseract are in your PATH
- macOS/Linux: Verify installation with `which poppler` and `which tesseract`

## Development Workflow

1. **Code**: Write your Python code with full IntelliSense support
2. **Debug**: Use breakpoints to debug complex PII detection logic
3. **Test**: Run the Streamlit app and test with sample files
4. **Format**: Use Black formatter (Ctrl+Shift+I) to format code
5. **Commit**: Use built-in Git integration for version control

## Performance Tips

- Use VS Code's Python profiler to identify bottlenecks
- Monitor memory usage during PDF processing
- Use the integrated terminal to run performance tests

Your VS Code environment is now perfectly configured for developing and running the PII de-identification Streamlit application!