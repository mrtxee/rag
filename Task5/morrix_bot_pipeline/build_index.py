# ingest, build index app
import os
import glob
import tiktoken
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
import time
import re
from config import *
import re


def strip_markdown(text):
    """
    Удаляет Markdown‑разметку из текста.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Удаляем изображения: ![alt](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # 2. Удаляем ссылки: [текст](url) → оставляем только текст
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)

    # 3. Удаляем жирный/курсив: *текст*, **текст**, _текст_, __текст__
    text = re.sub(r'(\*{1,3}|_{1,3})(.*?)\1', r'\2', text)

    # 4. Удаляем заголовки: #, ##, ### и т. д.
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # 5. Удаляем цитаты: > текст
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    #   Если цитата многострочная, удаляем > в начале каждой строки
    text = re.sub(r'\n>\s*', '\n', text)

    # 6. Удаляем код: `код`
    text = re.sub(r'`(.*?)`', r'\1', text)

    # 7. Удаляем блоки кода: ```...```
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # 8. Удаляем списки: - пункт, * пункт, + пункт, 1. пункт
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)  # маркированные
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)   # нумерованные


    # 9. Удаляем горизонтальные линии: ---, ****, ___
    text = re.sub(r'^(?:\-{3,}|\*{3,}|_{3,})\s*$', '', text, flags=re.MULTILINE)

    # 10. Удаляем HTML‑теги (если есть)
    text = re.sub(r'<[^>]+>', '', text)

    # 11. Убираем лишние пробелы и пустые строки
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # удаляем пустые строки
    text = '\n'.join(lines)

    return text


def chunk_text(text: str, source: str, chunk_size: int = 400, overlap: int = 50) -> List[Dict]:
    """
    Возвращает коллекцию чанков
    """
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        tokens = encoder.encode(text)
    except Exception:
        # Fallback: по символам (для кириллицы, если tiktoken ведёт себя нестабильно)
        tokens = list(text)
        chunk_size *= 4
        overlap *= 4

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        if 'encoder' in locals():
            chunk_text_decoded = encoder.decode(tokens[start:end])
        else:
            chunk_text_decoded = ''.join(tokens[start:end])

        # Пропускаем пустые чанки
        if chunk_text_decoded.strip():
            chunks.append({
                "text": chunk_text_decoded.strip(),
                "source": source,
                "chunk_id": f"{os.path.basename(source)}_chunk_{chunk_id}",
                "chunk_index": chunk_id,
                "start_token": start,
                "end_token": end
            })
            chunk_id += 1
        start += (chunk_size - overlap)
    return chunks

def main():
    """
    + Найти файлы базы знаний, для каждого файла
        + Убрать MD-форматирование
        + Разбить на чанки
    + Для каждого чанка сгенерировать индекс
    + Каждый индекс обогатить фрагментом знаний, метаданными и записать в ChromaDb
    """
    print(f"🔍 Загружаем Markdown-файлы из '{KNOWLEDGE_DIR}'...")
    md_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))
    if not md_files:
        print(f"❌ Папка '{KNOWLEDGE_DIR}' пустая или не существует!")
        print("Убедитесь, что файлы имеют расширение .md")
        return

    print(f"📄 Найдено {len(md_files)} Markdown-файлов.")

    # Загрузка модели
    print("🧠 Загружаем модель эмбеддингов...")
    metric_start_time = time.perf_counter()
    model = SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH)
    metric_time = time.perf_counter() - metric_start_time
    print(f"⏱️ длительность операции: {metric_time:.4f} секунд")

    # Сбор всех чанков
    all_chunks = []
    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as f:
            text = strip_markdown(f.read())
        print(f"  → Чанкинг: {os.path.basename(file_path)}")
        chunks = chunk_text(text, source=file_path, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        all_chunks.extend(chunks)
    print(f"✅ Всего чанков: {len(all_chunks)}")

    
    # Генерация эмбеддингов
    metric_start_time = time.perf_counter()
    print("🌀 Генерируем эмбеддинги...")
    texts = ["passage: " + chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, batch_size=8, show_progress_bar=True)
    metric_time = time.perf_counter() - metric_start_time
    print(f"⏱️ длительность операции: {metric_time:.4f} секунд")

    # Подготовка для Chroma
    ids = [chunk["chunk_id"] for chunk in all_chunks]
    documents = [chunk["text"] for chunk in all_chunks]
    embeddings_list = [emb.tolist() for emb in embeddings]
    metadatas = [
        {
            "source": os.path.basename(chunk["source"]),  # только имя файла, без пути
            "chunk_index": chunk["chunk_index"],
            "start_token": chunk["start_token"],
            "end_token": chunk["end_token"]
        }
        for chunk in all_chunks
    ]

    # Сохранение в ChromaDB
    print("💾 Сохраняем в ChromaDB...")
    metric_start_time = time.perf_counter()
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    collection.add(ids=ids, documents=documents, embeddings=embeddings_list, metadatas=metadatas)
    metric_time = time.perf_counter() - metric_start_time
    print(f"⏱️ длительность операции: {metric_time:.4f} секунд")
    print(f"✅ Эбмеддинги {EMBEDDING_MODEL_LOCAL_PATH} сгенерированы и записаны в базу {CHROMA_PATH}:{COLLECTION_NAME}")

if __name__ == "__main__":
    main()