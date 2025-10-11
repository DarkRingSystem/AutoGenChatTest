@echo off
cd backend
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install autogen-agentchat==0.7.5
pip install autogen-ext[openai]==0.7.5
pip install "openai>=1.93"
pip install "fastapi>=0.115.0"
pip install "uvicorn[standard]>=0.32.0"
pip install "pydantic>=2.10.0"
pip install "pydantic-settings>=2.0.0"
pip install "python-dotenv>=1.0.1"
pip install "tiktoken>=0.5.0"
pip install "marker-pdf>=1.0.0"
pip install "weasyprint>=66.0"
pip install "mammoth>=1.11.0"
pip install "python-multipart>=0.0.6"
echo.
echo Installation complete!
echo.
cmd /k

