import os
from bs4 import BeautifulSoup, Comment

def process_html_files(directory):
    # Проверяем существование директории
    if not os.path.exists(directory):
        print(f"Ошибка: директория '{directory}' не найдена.")
        return

    # Перебираем все файлы в директории
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            print(f"Обрабатываю файл: {filepath}")

            try:
                # Читаем файл
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Создаём объект BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')

                # 1. Находим основной блок
                main_div = soup.find(
                    'div',
                    class_='mw-content-ltr mw-parser-output',
                    attrs={'lang': 'ru', 'dir': 'ltr'}
                )
                if not main_div:
                    print(f"Основной блок не найден в файле {filename}. Пропускаем.")
                    continue

                # 2. Удаляем все блоки div с классом mw-collapsible
                for collapsible in main_div.find_all('div', class_='mw-collapsible'):
                    collapsible.decompose()

                # 3. Удаляем атрибуты style и class у всех тегов внутри блока
                for tag in main_div.find_all(True):  # True — все теги
                    if 'style' in tag.attrs:
                        del tag['style']
                    if 'class' in tag.attrs:
                        del tag['class']

                # 4. Удаляем все таблицы (<table>)
                for table in main_div.find_all('table'):
                    table.decompose()

                # 4. Удаляем все таблицы (<span>)
                for span in main_div.find_all('span'):
                    span.unwrap()

                # 4. Удаляем все таблицы (<a>)
                for link in main_div.find_all('a'):
                    if 'href' in link.attrs:
                        del link['href']
                    if 'title' in link.attrs:
                        del link['title']
                    if 'data-tracking-label' in link.attrs:
                        del link['data-tracking-label']
                    if 'data-testid' in link.attrs:
                        del link['data-testid']
                    if 'data-action' in link.attrs:
                        del link['data-action']
                        
                for svg in main_div.find_all('svg'):
                    svg.decompose()
                
                for use in main_div.find_all('use'):
                    use.decompose()

                comments = main_div.find_all(string=lambda text: isinstance(text, Comment))
                for comment in comments:
                    comment.extract()  # Удаляем комментарий

                # 5. Удаляем блоки с id="toc"
                for toc in main_div.find_all('div', id='toc'):
                    toc.decompose()

                # Формируем новый контент: только содержимое основного блока (без самого тега div)
                new_content = ''.join(str(item) for item in main_div.contents)

                # Записываем результат обратно в файл
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)

                print(f"Файл {filename} успешно обработан.")

            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {e}")

# Запуск обработки
if __name__ == "__main__":
    target_directory = "pages/4"
    process_html_files(target_directory)
