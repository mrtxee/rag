# Задание 4. Реализация RAG-бота с техниками промптинга

## структура проекта
morris_bot/
├── chat_with_rag.py          # ← основное приложение
├── config.py                 # ← настройки приложения
├── few_shot_examples.txt     # ← опционально: примеры для Few-shot
└── (ChromaDB, модель эмбеддингов, LLM -- из директорий прошлых уроков)

## venv
```bash
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install chromadb sentence-transformers llama-cpp-python
# ERROR: Failed building wheel for llama-cpp-python
# pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python-binaries/
winget uninstall Python
winget search Python.Python
winget install -e --id Python.Python.3.12
pip install ./llama_cpp_python-0.3.16-cp312-cp312-win_amd64.whl

pip freeze > requirements.txt
pip list --format=freeze > requirements.txt
```
