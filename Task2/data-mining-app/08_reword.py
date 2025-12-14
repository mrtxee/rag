import json
import os
import re

def load_renaming_rules(json_path):
    """Загружает правила переименования из JSON-файла."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {item['original']: item['renamed'] for item in data}
    except FileNotFoundError:
        print(f"Ошибка: файл {json_path} не найден.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {e}")
        return {}

def replace_in_file(file_path, rules):
    """Заменяет все вхождения original на renamed в файле."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Создаем копию для модификаций
        new_content = content
        
        # Применяем все правила замены
        for original, renamed in rules.items():
            # Используем word boundaries (\b) для точной замены слов
            pattern = r'\b' + re.escape(original) + r'\b'
            new_content = re.sub(pattern, renamed, new_content)
        
        
        # Если были изменения — записываем файл
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Обновлён: {file_path}")
            
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")

def rename_file_if_needed(file_path, rules):
    """Переименовывает файл, если его имя содержит подстроку из original."""
    dir_name, file_name = os.path.split(file_path)
    base_name, ext = os.path.splitext(file_name)
    
    new_base = base_name
    
    # Проверяем все правила на совпадение с именем файла
    for original, renamed in rules.items():
        if original in base_name:
            new_base = new_base.replace(original, renamed)
    
    
    if new_base != base_name:
        new_file_name = new_base + ext
        new_file_path = os.path.join(dir_name, new_file_name)
        try:
            os.rename(file_path, new_file_path)
            print(f"Переименован: {file_name} → {new_file_name}")
            return new_file_path  # Возвращаем новое имя, если файл был переименован
        except Exception as e:
            print(f"Ошибка переименования {file_name}: {e}")
            return file_path
    return file_path

def process_directory(directory, rules):
    """Обрабатывает все .md файлы в директории."""
    if not os.path.exists(directory):
        print(f"Директория {directory} не существует.")
        return
    
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            filepath = os.path.join(directory, filename)
            # 1. Переименовываем файл (если нужно)
            new_filepath = rename_file_if_needed(filepath, rules)
            # 2. Заменяем текст внутри файла
            replace_in_file(new_filepath, rules)

def main():
    json_path = "pages/10/renaming_dictionary_1.json"
    md_directory = "pages/10"
    
    # Загружаем правила переименования
    rules = load_renaming_rules(json_path)
    
    if not rules:
        return  # Если правил нет — завершаем
    
    print("Загружены правила переименования:")
    for orig, ren in rules.items():
        print(f" {orig} → {ren}")
    
    # Обрабатываем все .md файлы
    process_directory(md_directory, rules)
    print("Обработка завершена.")

if __name__ == "__main__":
    main()