# ====== Конфигурация построителя индексов модели машинного обучения ======
# ==== общие настройки ====
KNOWLEDGE_DIR = "./../../Task2/knowledge_base" # база знаний с данными для тренировки модели
CHROMA_PATH = "chroma_db" # путь до бд
COLLECTION_NAME = "stories_rag" # идентификатор коллекции
EMBEDDING_MODEL_LOCAL_PATH = "./../../models/multilingual-e5-large-instruct" # путь до эмбединга

# ==== настройки чинкинга ====
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
