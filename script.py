from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import keyboard
import json
import requests
import time
import os
from datetime import datetime
from typing import Optional, Any
import logging
from settings import (
    get_chrome_driver,
    DOWNLOAD_FOLDER,
    PRODUCT_URL,
    REQUEST_HEADERS,
    PAGE_LOAD_DELAY,
    VIDEO_LOAD_DELAY,
)


# Настройка логирования
file_handler = logging.FileHandler('wb_downloader.log')
file_handler.setLevel(logging.CRITICAL)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler],
)


class WildberriesVideoDownloader:
    """
    Класс для скачивания видео-отзывов с Wildberries.

    Attributes:
        driver (WebDriver): Экземпляр веб-драйвера
        download_folder (str): Путь к папке для сохранения видео
        product_url (str): URL страницы с отзывами
    """

    def __init__(self) -> None:
        """
        Инициализирует экземпляр класса WildberriesVideoDownloader.
        """
        self.driver: WebDriver = get_chrome_driver()
        self.download_folder: str = DOWNLOAD_FOLDER
        self.product_url: str = PRODUCT_URL

        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def open_product_page(self) -> None:
        """
        Открывает страницу с отзывами и ждет загрузки контента.

        Raises:
            Exception: Если произошла ошибка при загрузке страницы
        """
        try:
            self.driver.get(self.product_url)
            time.sleep(PAGE_LOAD_DELAY)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'feedback__content'))
            )
            logging.info('Страница с товаром успешно загружена')
        except Exception as e:
            logging.critical(f'Ошибка при загрузке страницы: {str(e)}')

    def get_network_requests(self) -> Optional[str]:
        """
        Анализирует сетевые запросы и ищет URL видео.

        Returns:
            Optional[str]: URL видео или None, если не найден
        """
        logs = self.driver.get_log('performance')
        ts_url = None

        for entry in logs:
            log = json.loads(entry['message'])['message']
            if (
                'Network.responseReceived' in log['method']
                and 'params' in log
                and 'response' in log['params']
            ):
                response = log['params']['response']
                if 'url' in response and 'video' in response['url']:
                    video_url = response['url']
                    if '/1.ts' in video_url:
                        ts_url = video_url
                        logging.info('Найдена ссылка на основное видео')
                        break

        return ts_url

    def start_monitoring(self) -> None:
        """
        Запускает мониторинг нажатий клавиш для скачивания видео.
        """
        try:
            self.open_product_page()
            logging.info(
                'Мониторинг начат. Нажмите F4 для скачивания'
                'открытого видео. Esc для выхода.'
            )
            keyboard.on_press_key('F4', self.download_current_video)
            keyboard.wait('esc')
        finally:
            self.driver.quit()
            logging.info('Программа завершена')

    def download_current_video(self, _: Any) -> None:
        """
        Скачивает текущее открытое видео.

        Args:
            _: Неиспользуемый параметр для callback-функции клавиатуры
        """
        try:
            time.sleep(VIDEO_LOAD_DELAY)
            video_url = self.get_network_requests()

            if video_url and '/1.ts' in video_url:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'{self.download_folder}/video_{timestamp}.mp4'

                response = requests.get(video_url,
                                        headers=REQUEST_HEADERS,
                                        stream=True)
                logging.info(f'Скачивание видео по ссылке: {video_url}')

                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    logging.info(f'Видео успешно сохранено: {filename}')
                else:
                    logging.critical(
                        f'Ошибка при скачивании видео. '
                        f'Код ответа: {response.status_code}'
                    )
            else:
                logging.info('Ссылка на основное видео не найдена')

        except Exception as e:
            logging.critical(f'Произошла ошибка: {str(e)}')


if __name__ == '__main__':
    downloader = WildberriesVideoDownloader()
    downloader.start_monitoring()
