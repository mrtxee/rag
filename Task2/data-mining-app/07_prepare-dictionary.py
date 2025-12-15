import json
import os

def update_renaming_dictionary(input_path, output_path):
    # Проверяем существование входного файла
    if not os.path.exists(input_path):
        print(f"Ошибка: файл {input_path} не найден.")
        return
    
    
    try:
        # Читаем исходный JSON-файл
        with open(input_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        
        # Обновляем каждое слово: копируем original в renamed
        for item in data:
            item['renamed'] = item['original']
        
        
        # Записываем обновлённый словарь в новый файл
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4  # Форматирование с отступами (pretty print)
            )
        
        print(f"Файл успешно обновлён и сохранён как {output_path}")
        
    except json.JSONDecodeError as e:
        print(f"Ошибка при чтении JSON-файла: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def main():
    input_file = "pages/9/renaming_dictionary_0.json"
    output_file = "pages/9/renaming_dictionary_1.json"
    
    update_renaming_dictionary(input_file, output_file)

if __name__ == "__main__":
    main()
