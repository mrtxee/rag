import os
import re
import json

def extract_words_from_md(file_path):
    """Извлекает слова из MD‑файла без учёта разметки."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем Markdown-разметку:
    # 1. Заголовки (#, ##, ### и т.д.)
    content = re.sub(r'^#{1,6}.*', '', content, flags=re.MULTILINE)
    # 2. Ссылки [текст](url)
    content = re.sub(r'\[.*?\]\(.*?\)', '', content)
    # 3. Жирный/курсив (*текст*, **текст**, _текст_, __текст__)
    content = re.sub(r'[\*_]{1,2}.*?[\*_]{1,2}', '', content)
    # 4. Цитаты (> текст)
    content = re.sub(r'^>.*', '', content, flags=re.MULTILINE)
    # 5. Код (`код`, ```код```)
    content = re.sub(r'`.*?`', '', content)
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    # 6. Списки (- пункт, * пункт, 1. пункт)
    content = re.sub(r'^[\-\*\d\.]\s+.*', '', content, flags=re.MULTILINE)
    
    # Оставляем только буквы и пробелы, разбиваем на слова
    words = re.findall(r'[a-zA-Za-яА-ЯёЁ]+', content)
    return words

def main():
    input_dir = './pages/10'
    output_file = 'words_corpus.jsonl'
    
    all_words = set()
    
    # Обходим все MD-файлы в директории
    for filename in os.listdir(input_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(input_dir, filename)
            try:
                words = extract_words_from_md(filepath)
                # Фильтруем: длина ≥4, приводим к нижнему регистру
                filtered_words = {word.lower() for word in words if len(word) >= 4}
                all_words.update(filtered_words)
            except Exception as e:
                print(f"Ошибка при обработке {filename}: {e}")
    
    # Записываем в JSONL (по слову в строке)
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted(all_words):  # сортируем для удобства
            f.write(json.dumps({"word": word}, ensure_ascii=False) + '\n')
    
    # Выводим количество уникальных слов
    print(f"Найдено уникальных слов (длина ≥4): {len(all_words)}")


if __name__ == '__main__':
    main()
