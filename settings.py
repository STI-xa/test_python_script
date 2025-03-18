import undetected_chromedriver as uc
from typing import Dict


def get_chrome_driver() -> uc.Chrome:
    """
    Инициализирует и настраивает Chrome драйвер с необходимыми параметрами.

    Returns:
        uc.Chrome: Настроенный экземпляр Chrome драйвера
    """
    options = uc.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    # Базовые настройки браузера
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')

    return uc.Chrome(options=options)


# Настройки загрузки
DOWNLOAD_FOLDER: str = 'wb_videos'
PRODUCT_URL = (
    'https://www.wildberries.ru/catalog/'
    '192186031/feedbacks'
    '?imtId=183532775&size=31'
)

# Заголовки для запросов
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/122.0.0.0 Safari/537.36'
)

REQUEST_HEADERS: Dict[str, str] = {
    'User-Agent': USER_AGENT,
    'Referer': 'https://www.wildberries.ru/',
}

# Задержки
PAGE_LOAD_DELAY: int = 5  # секунд
VIDEO_LOAD_DELAY: int = 2  # секунд