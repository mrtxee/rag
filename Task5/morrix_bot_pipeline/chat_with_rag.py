# chat_with_rag.py
import argparse
import time
import re
from typing import List, Dict
from config import *

import chromadb
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# === Загрузка компонентов ===
print("🧠 Загружаем эмбеддинг-модель...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH, device="cpu")

print("💾 Подключаемся к ChromaDB...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(name=COLLECTION_NAME)

print("🤖 Загружаем LLM...")
llm = Llama(
    model_path=LLM_MODEL_LOCAL_PATH,
    n_ctx=8192,          # контекст модели
    n_threads=6,         # CPU threads <= 8 for i5-1135G7)
    verbose=False
)

def retrieve_chunks(query: str, top_k: int = CHUNKS_FOR_RESPONSE) -> List[Dict]:
    """Поиск релевантных чанков в ChromaDB"""
    query_emb = embedding_model.encode("query: " + query).tolist()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )
    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "similarity": 1 - results["distances"][0][i]
        })
    return chunks


# Компиляция для скорости
MALICIOUS_REGEX = re.compile(
    "|".join(f"({p})" for p in MALICIOUS_PATTERNS),
    re.IGNORECASE
)

def is_chunk_malicious(text: str) -> bool:
    """Проверка чанка на вредоносность"""
    return bool(MALICIOUS_REGEX.search(text))

def sanitize_chunk(text: str) -> str:
    """Очистка чанка от опасных инструкций"""
    # Удаляем подозрительные фразы
    cleaned = MALICIOUS_REGEX.sub("[УДАЛЕНО: потенциально вредоносный фрагмент]", text)
    # Удаляем длинные последовательности спецсимволов
    cleaned = re.sub(r"[!@#$%^&*()_+=\[\]{}|;:,.<>?]{10,}", "[УДАЛЕНО: подозрительная строка]", cleaned)
    return cleaned.strip()

def retrieve_and_filter_chunks(query: str, top_k: int = CHUNKS_FOR_RESPONSE) -> List[Dict]:
    """Поиск + фильтрация + санитизация"""
    query_emb = embedding_model.encode("query: " + query).tolist()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )
    
    # Фильтрация и санитизация
    valid_chunks = []
    for i in range(len(results["ids"][0])):
        text = results["documents"][0][i]
        source = results["metadatas"][0][i]["source"]
        
        if is_chunk_malicious(text):
            print(f"⚠️ Пропущен вредоносный чанк из {source}")
            continue
            
        cleaned_text = sanitize_chunk(text)
        if len(cleaned_text) < 20:  # слишком короткий после очистки
            continue
            
        valid_chunks.append({
            "text": cleaned_text,
            "source": source,
            "similarity": 1 - results["distances"][0][i]
        })
        
        if len(valid_chunks) >= top_k:
            break
            
    return valid_chunks


def build_prompt(query: str, chunks: List[Dict], use_few_shot: bool = False, use_cot: bool = False) -> str:
    """Промпт-инженеринг"""
    context = "\n\n".join(f"{c['text']}" for c in chunks)
    
    # System prompt
    instructions = SYSTEM_INSTRUCTIONS
    
    # Chain-of-Thought
    if use_cot:
        instructions += COT_INSTRUCTION

    # Few-shot
    if use_few_shot:
        instructions += FEW_SHOT_SAMPLES

    return (
        f"Контекст:\n{context}\n\n"
        f"Инструкция:\n{instructions}\n\n"
        f"Вопрос:\n{query}\n\n"
        f"Ответ (строго по правилам):\n"
    )

def post_check_response(response: str) -> str:
    """Пост-проверка ответа на утечку секретов"""
    if MALICIOUS_REGEX.search(response):
        return "❌ Ответ заблокирован системой безопасности: обнаружена потенциально вредоносная информация."
    if re.search(r"(пароль|password|secret|ключ|root):\s*\w+", response, re.IGNORECASE):
        return "❌ Ответ заблокирован: запрещено раскрывать учётные данные."
    return response

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--few-shot", action="store_true", help="Включить Few-shot prompting")
    parser.add_argument("--cot", action="store_true", help="Включить Chain-of-Thought")
    parser.add_argument("--top-k", type=int, default=3, help="Сколько чанков использовать")
    args = parser.parse_args()

    print("🛡️ RAG-бот с LLM и защитой от вредоносного контекста готов!")
    print("Введите 'exit' для выхода.\n")

    while True:
        query = input("Ваш вопрос: ").strip()
        if not query or query.lower() in ("exit", "quit"):
            break

        # 1. Retrieval
        chunks = retrieve_and_filter_chunks(query, top_k=args.top_k)
        if not chunks:
            print("ℹ️ Нет безопасных релевантных фрагментов.\n")
            continue

        # 2. Формирование промпта
        prompt = build_prompt(
            query=query,
            chunks=chunks,
            use_few_shot=args.few_shot,
            use_cot=args.cot
        )

        # 3. Генерация ответа
        metric_start_time = time.perf_counter()
        print("\n⏳ Генерация ответа...", flush=True)
        output = llm(
            prompt,
            max_tokens=512,
            stop=["\n\n", "СИСТЕМНЫЕ ИНСТРУКЦИИ", "КОНТЕКСТ:"],
            echo=False,
            temperature=LLM_TEMPERATURE
        )
        answer = post_check_response(output["choices"][0]["text"].strip())
        metric_time = time.perf_counter() - metric_start_time
        print(f"⏱️ длительность операции: {metric_time:.4f} секунд")

        # 4. Вывод
        print("\n✅ Ответ:")
        print(answer)
        print("\n" + "-" * 60)

if __name__ == "__main__":
    main()