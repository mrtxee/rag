import os
import json
import re
from collections import Counter

def extract_words(directory_path):
    # Регулярное выражение для поиска:
    # - слов, начинающихся с заглавной кириллической буквы [А-Я]
    # - слов, начинающихся с заглавной латинской буквы [A-Z]
    # - слов, содержащих минимум 2 цифры подряд \d{2,}
    pattern = re.compile(
        r'\b(?:[А-Я][а-яё]*|[A-Z][a-z]*|\w*\d{2,}\w*)\b',
        re.UNICODE
    )
    
    all_words = []  # Список для сбора всех найденных слов (с повторами)

    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        
        # Проверяем, что это файл (не директория)
        if not os.path.isfile(filepath):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Находим все подходящие слова
            matches = pattern.findall(content)
            all_words.extend(matches)
                
        except Exception as e:
            print(f"Ошибка при чтении файла {filename}: {e}")
    
    return all_words

def create_renaming_dictionary(word_list):
    # Подсчитываем частоту каждого слова
    word_counts = Counter(word_list)
    
    # Создаем список словарей и сортируем по количеству вхождений (по возрастанию)
    dictionary = []
    for word, count in sorted(word_counts.items(), key=lambda x: x[1]):
        dictionary.append({
            "original": word,
            "renamed": "",
            "count": str(count)  # Преобразуем в строку согласно ТЗ
        })
    
    return dictionary

def save_to_json(data, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(
                data,
                json_file,
                ensure_ascii=False,
                indent=4  # pretty print (отступы для читаемости)
            )
        print(f"Словарь сохранён в {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении JSON: {e}")

def main():
    input_directory = "pages/8"
    output_file = os.path.join(input_directory, "renaming_dictionary.json")
    
    # Проверяем существование директории
    if not os.path.exists(input_directory):
        print(f"Ошибка: директория {input_directory} не существует.")
        return
    
    print("Начинаем обработку файлов...")
    
    # 1. Собираем все подходящие слова (с повторами)
    words = extract_words(input_directory)
    
    if not words:
        print("Не найдено ни одного подходящего слова.")
        return
    
    print(f"Найдено {len(words)} слов (с учётом повторов).")
    print(f"Уникальных слов: {len(set(words))}")
    
    # 2. Создаём словарь с подсчётом и сортировкой
    dictionary = create_renaming_dictionary(words)
    
    # 3. Сохраняем в JSON
    save_to_json(dictionary, output_file)

if __name__ == "__main__":
    main()
