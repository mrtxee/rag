from playwright.sync_api import sync_playwright
import time

def save_html_with_playwright(url, output_file="testsave.html", timeout=30000):
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

if __name__ == "__main__":
    url = "https://rickandmorty.fandom.com/ru/wiki/Морти_Смит"
    success = save_html_with_playwright(url, "morty_playwright.html", timeout=60000)
    
    if success:
        # Читаем и показываем начало файла
        with open("morty_playwright.html", 'r', encoding='utf-8') as f:
            content = f.read(1000)
            print("\n📄 Начало сохранённого файла:")
            print("-" * 50)
            print(content)
            print("-" * 50)