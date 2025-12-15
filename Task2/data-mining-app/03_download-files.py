import pandas as pd
import os
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def save_one_html_with_playwright(url, output_file="testsave.html", timeout=30000):
    """
    Скачивает HTML через Playwright с исправленными настройками
    """
    print(f"🌐 Загружаю через Playwright: {url}")
    
    with sync_playwright() as p:
        try:
            # Запускаем браузер с дополнительными опциями
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # Создаем контекст с пользовательским агентом
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True
            )
            
            # Отключаем службы которые могут замедлять
            context.route("**/*.{png,jpg,jpeg,webp,gif,svg}", lambda route: route.abort())
            context.route("**/*.css", lambda route: route.abort())
            
            page = context.new_page()
            
            # Устанавливаем разумный timeout
            page.set_default_timeout(45000)
            
            print(f"⏳ Перехожу по ссылке (timeout: {timeout}ms)...")
            
            # Используем 'domcontentloaded' вместо 'networkidle'
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            
            # Ждем немного для загрузки динамического контента
            print("⏳ Жду загрузки динамического контента...")
            page.wait_for_timeout(5000)  # 5 секунд
            
            # Прокручиваем для загрузки ленивого контента
            print("🔄 Прокручиваю страницу...")
            page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight / 2);
                setTimeout(() => {
                    window.scrollTo(0, document.body.scrollHeight);
                }, 1000);
            """)
            page.wait_for_timeout(3000)
            
            # Проверяем, загрузился ли основной контент
            content_loaded = page.evaluate("""
                () => {
                    // Проверяем наличие основного контента
                    const mainContent = document.querySelector('#content') || 
                                       document.querySelector('main') || 
                                       document.querySelector('article') ||
                                       document.querySelector('.mw-parser-output');
                    return mainContent && mainContent.textContent.length > 1000;
                }
            """)
            
            if not content_loaded:
                print("⚠️  Контент не загрузился, жду еще...")
                page.wait_for_timeout(10000)  # Дополнительные 10 секунд
            
            # Получаем HTML
            html_content = page.content()
            
            # Сохраняем
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            print(f"✅ HTML сохранён: {output_file}")
            print(f"📏 Размер: {len(html_content):,} символов")
            
            # Проверяем результат
            if "JavaScript is disabled" in html_content or len(html_content) < 10000:
                print("⚠️  Возможно, контент не загрузился полностью")
                print(f"   Содержит 'noscript': {'noscript' in html_content}")
            else:
                print("✅ Контент загружен успешно")
            
            # Делаем скриншот для проверки
            page.screenshot(path="page_screenshot.png", full_page=True)
            print("📸 Скриншот сохранён: page_screenshot.png")
            
            # Закрываем
            browser.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка Playwright: {e}")
            return False

    return True


def save_html_with_playwright(url, output_file, timeout=30000):
    """
    Скачивает HTML через Playwright с исправленными настройками
    """
    print(f"🌐 Загружаю: {url}")
    
    return save_one_html_with_playwright(url, output_file, timeout)
    

def process_links_file(tsv_file="links.tsv", output_dir="pages", delay=2):
    """
    Обрабатывает TSV файл и скачивает все страницы
    """
    # Проверяем существование файла
    if not os.path.exists(tsv_file):
        print(f"❌ Файл не найден: {tsv_file}")
        return False
    
    # Создаем директорию для сохранения
    os.makedirs(output_dir, exist_ok=True)
    
    # Читаем TSV файл
    print(f"📖 Читаю файл: {tsv_file}")
    
    try:
        # Используем pandas для чтения TSV
        df = pd.read_csv(tsv_file, sep='\t', encoding='utf-8')
    except Exception as e:
        print(f"❌ Ошибка чтения TSV: {e}")
        print("🔄 Пробую ручное чтение...")
        
        # Альтернативный способ чтения
        try:
            with open(tsv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Пропускаем заголовок
            data = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        data.append({'URL': parts[0], 'Text': parts[1]})
            df = pd.DataFrame(data)
        except Exception as e2:
            print(f"❌ Ошибка ручного чтения: {e2}")
            return False
    
    print(f"📊 Найдено записей: {len(df)}")
    print("\nПервые 5 записей:")
    print(df.head())
    
    # Проверяем наличие нужных колонок
    if 'URL' not in df.columns or 'Text' not in df.columns:
        print("❌ Файл должен содержать колонки 'URL' и 'Text'")
        return False
    
    # Статистика
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    # Процесс скачивания
    print(f"\n{'='*60}")
    print(f"НАЧИНАЮ СКАЧИВАНИЕ СТРАНИЦ")
    print(f"{'='*60}")
    
    for index, row in df.iterrows():
        url = row['URL']
        text = row['Text']
        
        # Создаем безопасное имя файла
        safe_filename = create_safe_filename(text)
        output_file = os.path.join(output_dir, f"{safe_filename}.html")
        
        print(f"\n[{index + 1}/{len(df)}] {'-'*40}")
        print(f"📄 Текст: {text}")
        print(f"🔗 URL: {url}")
        print(f"💾 Файл: {output_file}")
        
        # Проверяем, не скачан ли уже файл
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"⚠️  Файл уже существует ({file_size:,} байт). Пропускаю...")
            skipped_count += 1
            continue
        
        # Скачиваем страницу
        success = save_html_with_playwright(url, output_file)
        
        if success:
            success_count += 1
            
            # Проверяем размер файла
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📏 Размер файла: {file_size:,} байт")
                
                # Проверяем, не пустой ли файл
                if file_size < 1000:
                    print("⚠️  Внимание: файл очень маленький, возможно ошибка загрузки")
        else:
            fail_count += 1
            print(f"❌ Не удалось скачать: {url}")
        
        # Задержка между запросами (чтобы не нагружать сервер)
        if index < len(df) - 1:  # Не ждем после последнего
            print(f"⏳ Жду {delay} секунд перед следующим запросом...")
            time.sleep(delay)
    
    # Вывод статистики
    print(f"\n{'='*60}")
    print("СТАТИСТИКА СКАЧИВАНИЯ")
    print(f"{'='*60}")
    print(f"✅ Успешно: {success_count}")
    print(f"❌ Ошибки: {fail_count}")
    print(f"⏭️  Пропущено (уже скачано): {skipped_count}")
    print(f"📊 Всего обработано: {success_count + fail_count + skipped_count} из {len(df)}")
    
    # Сохраняем статистику в файл
    stats_file = os.path.join(output_dir, "download_stats.txt")
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"Статистика скачивания от {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Исходный файл: {tsv_file}\n")
        f.write(f"Директория: {output_dir}\n")
        f.write(f"Успешно: {success_count}\n")
        f.write(f"Ошибки: {fail_count}\n")
        f.write(f"Пропущено: {skipped_count}\n")
        f.write(f"Всего в исходнике: {len(df)}\n")
    
    print(f"\n📊 Статистика сохранена в: {stats_file}")
    
    return success_count > 0 or skipped_count > 0

def create_safe_filename(text, max_length=100):
    """
    Создает безопасное имя файла из текста
    """
    import re
    
    # Заменяем недопустимые символы
    safe = re.sub(r'[<>:"/\\|?*]', '_', text)
    
    # Убираем лишние пробелы
    safe = re.sub(r'\s+', ' ', safe).strip()
    
    # Обрезаем длину
    if len(safe) > max_length:
        safe = safe[:max_length]
    
    # Если имя файла пустое, создаем случайное
    if not safe:
        import random
        import string
        safe = 'page_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    return safe

def create_batch_script(tsv_file, output_dir="pages"):
    """
    Создает батч-скрипт для скачивания в случае проблем
    """
    # Читаем TSV
    df = pd.read_csv(tsv_file, sep='\t', encoding='utf-8')
    
    # Создаем Python скрипт для ручного скачивания
    script_content = '''#!/usr/bin/env python3
# Скрипт для скачивания страниц вручную

import requests
import time
import os

# Список URL для скачивания
urls_to_download = [
'''
    
    for _, row in df.iterrows():
        script_content += f"    ('{row['URL']}', '{row['Text']}'),\n"
    
    script_content += ''']

def download_page(url, filename):
    """Простая загрузка через requests"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ {filename}")
        return True
    except Exception as e:
        print(f"❌ Ошибка {filename}: {e}")
        return False

if __name__ == "__main__":
    output_dir = "''' + output_dir + '''"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (url, text) in enumerate(urls_to_download):
        print(f"[{i+1}/{len(urls_to_download)}] {text}")
        safe_name = text.replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = os.path.join(output_dir, f"{safe_name}.html")
        
        if not os.path.exists(filename):
            download_page(url, filename)
            time.sleep(2)
        else:
            print(f"⚠️  Уже существует: {filename}")
'''

    script_file = "download_backup.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"📝 Создан резервный скрипт: {script_file}")

def main():
    """
    Основная функция
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Скачивание HTML страниц из TSV файла',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Примеры:
  python download_pages.py links.tsv
  python download_pages.py links.tsv --output my_pages
  python download_pages.py links.tsv --delay 3 --timeout 45
        '''
    )
    
    parser.add_argument('tsv_file', help='TSV файл со ссылками')
    parser.add_argument('-o', '--output', default='pages', help='Директория для сохранения (по умолчанию: pages)')
    parser.add_argument('-d', '--delay', type=float, default=2, help='Задержка между запросами в секундах')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='Таймаут для каждой страницы в секундах')
    parser.add_argument('--create-backup', action='store_true', help='Создать резервный скрипт')
    
    args = parser.parse_args()
    
    # Проверяем наличие playwright
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright не установлен!")
        print("📦 Установите: pip install playwright")
        print("🔧 Затем установите браузер: playwright install chromium")
        sys.exit(1)
    
    # Проверяем наличие браузера
    try:
        with sync_playwright() as p:
            p.chromium.launch(headless=True).close()
    except Exception as e:
        print(f"❌ Ошибка инициализации Playwright: {e}")
        print("🔧 Установите браузер: playwright install chromium")
        sys.exit(1)
    
    # Создаем резервный скрипт если нужно
    if args.create_backup:
        create_batch_script(args.tsv_file, args.output)
    
    # Запускаем обработку
    print(f"{'='*60}")
    print(f"ЗАПУСК СКАЧИВАНИЯ СТРАНИЦ")
    print(f"{'='*60}")
    print(f"Файл: {args.tsv_file}")
    print(f"Директория: {args.output}")
    print(f"Задержка: {args.delay} сек")
    print(f"Таймаут: {args.timeout} сек")
    print(f"{'='*60}")
    
    # Запускаем скачивание
    success = process_links_file(
        tsv_file=args.tsv_file,
        output_dir=args.output,
        delay=args.delay
    )
    
    if success:
        print(f"\n🎉 Скачивание завершено!")
    else:
        print(f"\n⚠️  Скачивание завершено с ошибками!")
        sys.exit(1)

if __name__ == "__main__":
    # Проверяем наличие зависимостей
    try:
        import pandas as pd
    except ImportError:
        print("❌ Pandas не установлен!")
        print("📦 Установите: pip install pandas")
        sys.exit(1)
    
    main()