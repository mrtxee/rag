# chat_cli.py (без изменений)
import chromadb
from sentence_transformers import SentenceTransformer
from config import *


def main():
    print("💬 RAG-бот для поиска ближайших чанков по сходству")
    print("Введите 'exit', чтобы выйти.\n")

    model = SentenceTransformer(EMBEDDING_MODEL_LOCAL_PATH)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    while True:
        query = input("Ваш запрос: ").strip()
        if not query or query.lower() in ("exit", "quit"):
            break

        query_emb = model.encode("query: " + query).tolist()
        results = collection.query(query_embeddings=[query_emb], n_results=2)

        print("\n🔍 Найдено:")
        for i in range(len(results['ids'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            similarity = 1 - results['distances'][0][i]

            print(f"\n📚 Источник: {meta['source']}, чанк #{meta['chunk_index']}")
            print(f"🎯 Сходство: {similarity:.3f}")
            print(f"📝 Цитата: {doc[:250]}{'...' if len(doc) > 250 else ''}")

        print("\n" + "="*60)

if __name__ == "__main__":
    main()