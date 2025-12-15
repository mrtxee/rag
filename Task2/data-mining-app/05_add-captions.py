import os

def process_files_in_directory(directory_path):
    # Проверяем, существует ли директория
    if not os.path.exists(directory_path):
        print(f"Ошибка: директория {directory_path} не существует.")
        return

    # Получаем список файлов в директории
    files = os.listdir(directory_path)
    
    if not files:
        print("В директории нет файлов.")
        return

    for filename in files:
        filepath = os.path.join(directory_path, filename)
        
        # Пропускаем поддиректории
        if not os.path.isfile(filepath):
            continue
            
        try:
            # Читаем содержимое файла
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Получаем имя файла без расширения
            name_without_ext = os.path.splitext(filename)[0]
            
            # Проверяем наличие подстрок
            if "### Биография" in content:
                # Формируем новую первую строку
                new_first_line = f"## Биография {name_without_ext}\n\n"
                
                # Записываем обновлённое содержимое
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_first_line + content)
                
                # Формируем новое имя файла
                file_ext = os.path.splitext(filename)[1]
                new_filename = f"Биография {name_without_ext}{file_ext}"
                new_filepath = os.path.join(directory_path, new_filename)
                
                # Переименовываем файл
                os.rename(filepath, new_filepath)
                print(f"Обработан файл: {filename} → {new_filename}")
                
            elif "### Сюжет" in content:
                # Формируем новую первую строку
                new_first_line = f"## Фрагмент истории: {name_without_ext}\n\n"
                
                # Записываем обновлённое содержимое
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_first_line + content)
                
                # Формируем новое имя файла
                file_ext = os.path.splitext(filename)[1]
                new_filename = f"История {name_without_ext}{file_ext}"
                new_filepath = os.path.join(directory_path, new_filename)
                
                # Переименовываем файл
                os.rename(filepath, new_filepath)
                print(f"Обработан файл: {filename} → {new_filename}")
                
            else:
                print(f"Файл не содержит ключевых подстрок: {filename}")
                
        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {e}")

# Запускаем обработку
if __name__ == "__main__":
    target_directory = "pages/6"
    process_files_in_directory(target_directory)
