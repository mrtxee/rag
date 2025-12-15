# Задание-5: Управление рисками RAG бота

## venv
```bash
python -m venv .venv
#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install ./../../Task4/morris_bot/llama_cpp_python-0.3.16-cp312-cp312-win_amd64.whl
pip freeze > requirements.txt
pip list --format=freeze > requirements.txt
```


