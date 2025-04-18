from abc import ABC
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from urllib.parse import urljoin

from crawler.crawler_services.shared.helper_method import helper_method


class _ebhmkoohccl45qesdbvrjqtyro2hmhkmh6vkyfyjjzfllm3ix72aqaid(leak_extractor_interface, ABC):
    _instance = None

    def __init__(self, callback=None):
        self.callback = callback
        self._card_data = []
        self._entity_data = []
        self.soup = None
        self._initialized = None
        self._redis_instance = redis_controller()

    def init_callback(self, callback=None):
        self.callback = callback

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_ebhmkoohccl45qesdbvrjqtyro2hmhkmh6vkyfyjjzfllm3ix72aqaid, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://ebhmkoohccl45qesdbvrjqtyro2hmhkmh6vkyfyjjzfllm3ix72aqaid.onion/leaks.php"

    @property
    def base_url(self) -> str:
        return "http://ebhmkoohccl45qesdbvrjqtyro2hmhkmh6vkyfyjjzfllm3ix72aqaid.onion"

    @property
    def rule_config(self) -> RuleModel:
        return RuleModel(m_fetch_proxy=FetchProxy.TOR, m_fetch_config=FetchConfig.PLAYRIGHT)

    @property
    def card_data(self) -> List[leak_model]:
        return self._card_data

    @property
    def entity_data(self) -> List[entity_model]:
        return self._entity_data

    def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
        return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

    def contact_page(self) -> str:
        return "https://mirror-h.org/contact"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    @staticmethod
    def safe_find(page, selector, attr=None):
        try:
            element = page.query_selector(selector)
            if element:
                return element.get_attribute(attr) if attr else element.inner_text().strip()
        except Exception:
            return None

    def parse_leak_data(self, page: Page):
        try:
            full_url = self.seed_url
            print("full url ")
            page.goto(full_url,timeout=30000)
            page.wait_for_load_state('load')
            print("full url load")
            page.wait_for_selector("div.advert_col",timeout=30000)
            print("full url cols added")

            today_date = datetime.today().strftime('%Y-%m-%d')

            advert_blocks = page.query_selector_all("div.advert_col")
            for block in advert_blocks:
                soup = BeautifulSoup(block.inner_html(), 'html.parser')

                # Extract title
                title = soup.select_one('div.advert_info_title').text.strip()

                # Extract content
                content = soup.select_one('div.advert_info_p').get_text(separator="\n", strip=True)

                # Extract website link
                web_url_element = soup.select_one('div.advert_info_p a')
                web_url = web_url_element['href'] if web_url_element else None

                # Extract image URLs
                image_urls = []
                for img in soup.select('div.advert_imgs_block img'):
                    img_src = img.get('src')
                    full_img_url = urljoin(self.base_url, img_src)
                    image_urls.append(full_img_url)

                card_data = leak_model(
                    m_screenshot=helper_method.get_screenshot_base64(page, title),
                    m_title=title,
                    m_weblink=[web_url] if web_url else [],
                    m_url=full_url,
                    m_base_url=self.base_url,
                    m_content=content + " " + self.base_url + " " + full_url,
                    m_websites=[],
                    m_important_content=content,
                    m_network=helper_method.get_network_type(self.base_url),
                    m_content_type=["leaks"],
                    m_leak_date=datetime.strptime(today_date, '%Y-%m-%d').date()
                )

                entity_data = entity_model(
                    m_email_addresses=[],
                    m_phone_numbers=[],
                    m_location_info=[],
                    m_name=title,
                )

                self.append_leak_data(card_data, entity_data)


        except Exception as ex:
            print(f"An error occurred: {ex}")