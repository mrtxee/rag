import re
from html import unescape
import sys
import os

def extract_links_from_html(html_content, base_url=None):
    """
    Находит все фрагменты вида:
    <a href="https://rickandmorty.fandom.com/ru/wiki/<любой_текст_1>"
                   data-tracking="custom-level-3"
                                    >
                                        <span><любой_текст_2></span>
                </a>
    
    Возвращает список кортежей (url, текст)
    """
    # Убираем лишние пробелы и переносы для упрощения поиска
    html_content = re.sub(r'\s+', ' ', html_content)
    
    # Регулярное выражение для поиска нужных фрагментов
    pattern = r'''
        <a\s+
        href="(https://rickandmorty\.fandom\.com/ru/wiki/[^"]*)"  # Полный URL
        [^>]*\s+                                                  # Любые другие атрибуты
        data-tracking="custom-level-3"                            # Обязательный атрибут
        [^>]*>                                                    # Остальная часть тега
        \s*<span>\s*(.*?)\s*</span>\s*                           # Текст внутри span
        </a>
    '''
    
    matches = re.findall(pattern, html_content, re.IGNORECASE | re.VERBOSE | re.DOTALL)
    
    # Обрабатываем найденные совпадения
    results = []
    for url, text in matches:
        # Декодируем HTML-сущности
        text = unescape(text).strip()
        # Убираем HTML-теги внутри текста, если они есть
        text = re.sub(r'<[^>]+>', '', text)
        results.append((url, text))
    
    return results

def read_html_file(filename, encoding='utf-8'):
    """
    Читает HTML-файл с указанной кодировкой
    """
    try:
        with open(filename, 'r', encoding=encoding) as file:
            return file.read()
    except UnicodeDecodeError:
        # Пробуем другие кодировки
        encodings = ['utf-8-sig', 'cp1251', 'windows-1251', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(filename, 'r', encoding=enc) as file:
                    print(f"Файл прочитан с кодировкой: {enc}")
                    return file.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Не удалось определить кодировку файла {filename}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {filename} не найден")
    except Exception as e:
        raise Exception(f"Ошибка при чтении файла {filename}: {e}")

def main():
    # Имя файла по умолчанию
    filename = "1.htm"
    
    # Проверяем, передан ли файл как аргумент командной строки
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    # Проверяем существование файла
    if not os.path.exists(filename):
        print(f"Ошибка: Файл '{filename}' не найден.")
        print(f"Текущая директория: {os.getcwd()}")
        print(f"Содержимое директории: {os.listdir('.')}")
        return
    
    print(f"Читаем файл: {filename}")
    print(f"Размер файла: {os.path.getsize(filename)} байт")
    
    try:
        # Читаем HTML из файла
        html_content = read_html_file(filename)
        print(f"Прочитано символов: {len(html_content)}")
        
        # Извлекаем ссылки
        links = extract_links_from_html(html_content)

        save_to_tsv(links, output_file="links.tsv")
        
        # Выводим результаты в TSV формате
        if links:
            print("\nURL\tText")
            print("-" * 80)
            for url, text in links:
                # Экранируем табуляции и переносы строк в тексте
                text_escaped = text.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
                print(f"{url}\t{text_escaped}")
            
            print(f"\nНайдено ссылок: {len(links)}")
        else:
            print("Ссылки с data-tracking='custom-level-3' не найдены.")
            
    except Exception as e:
        print(f"Ошибка: {e}")

def save_to_tsv(links, output_file="links.tsv"):
    """
    Сохраняет результаты в TSV файл
    """
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write("URL\tText\n")
            for url, text in links:
                text_escaped = text.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
                f.write(f"{url}\t{text_escaped}\n")
        print(f"Результаты сохранены в файл: {output_file}")
    except Exception as e:
        print(f"Ошибка при сохранении в файл: {e}")

if __name__ == "__main__":
    main()
    
    # Если нужно автоматически сохранить в файл, раскомментируйте:
    # try:
    #     html_content = read_html_file("1.htm")
    #     links = extract_links_from_html(html_content)
    #     if links:
    #         save_to_tsv(links, "extracted_links.tsv")
    # except Exception as e:
    #     print(f"Ошибка: {e}")