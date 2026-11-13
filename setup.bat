@echo off
echo =============================================
echo  AI Research Assistant - Setup Script
echo =============================================
echo.

cd /d "%~dp0backend"

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo [3/5] Installing numpy and spacy as pre-built wheels...
pip install numpy spacy --only-binary=:all:

echo.
echo [4/5] Installing remaining dependencies...
pip install -r requirements.txt

echo.
echo [5/5] Downloading spaCy model and NLTK data...
python -m spacy download en_core_web_sm
python -c "import nltk; [nltk.download(p, quiet=True) for p in ['punkt','stopwords','wordnet','averaged_perceptron_tagger','punkt_tab']]"

echo.
echo =============================================
echo  Setup Complete!
echo.
echo  Next: Edit backend\.env and add your API keys:
echo    TAVILY_API_KEY=...
echo    OPENROUTER_API_KEY=...
echo.
echo  Then run: start.bat
echo =============================================
pause

