from abc import ABC
from typing import List

from playwright.sync_api import Page

from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method

import re

class _nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd(leak_extractor_interface, ABC):
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
            cls._instance = super(_nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @property
    def seed_url(self) -> str:
        return "http://nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd.onion"

    @property
    def base_url(self) -> str:
        return "http://nsalewdnfclsowcal6kn5csm4ryqmfpijznxwictukhrgvz2vbmjjjyd.onion"

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
        return "https://t.me/fresh_leaks_today"

    def append_leak_data(self, leak: leak_model, entity: entity_model):
        self._card_data.append(leak)
        self._entity_data.append(entity)
        if self.callback:
            if self.callback():
                self._card_data.clear()
                self._entity_data.clear()

    def parse_leak_data(self, page: Page):
        self._card_data = []

        try:
            page.wait_for_selector("div.elem_ibody", timeout=30000)
            cards = page.query_selector_all("div.elem_ibody")

            if not cards:
                return

            for index, card in enumerate(cards):
                try:
                    cards = page.query_selector_all("div.elem_ibody")
                    card = cards[index]

                    title_element = card.query_selector("div.ibody_title")
                    company_name = title_element.inner_text().strip() if title_element else "Unknown"

                    date_element = card.query_selector("div.ibody_ft_left p:nth-child(1)")
                    leak_date = date_element.inner_text().replace("Date:", "").strip() if date_element else "Unknown"

                    status_element = card.query_selector("div.ibody_ft_left p:nth-child(2)")
                    status = status_element.inner_text().replace("Status:", "").strip() if status_element else "Unknown"

                    views_element = card.query_selector("div.counter_include")
                    views = views_element.inner_text().strip() if views_element else "Unknown"

                    image_element = card.query_selector("div.ibody_logo picture img")
                    image_url = image_element.get_attribute("src") if image_element else None

                    if not image_url:
                        continue

                    with page.expect_navigation(wait_until="domcontentloaded"):
                        image_element.click()

                    page.wait_for_load_state("domcontentloaded")

                    website_elements = page.query_selector_all("main section .custom-container")
                    websites = [w.get_attribute("href").strip() for w in website_elements if w.get_attribute("href")]

                    p_elements = page.query_selector_all("main section .custom-container")
                    for p in p_elements:
                        p_text = p.inner_text().strip()
                        links_in_p = re.findall(r"https?://[^\s,<>]+", p_text)
                        websites.extend(links_in_p)

                    websites = list(set(websites))

                    content_element = page.query_selector("main section .custom-container")
                    if content_element:
                        content_text = content_element.inner_text().strip()
                        for website in websites:
                            content_text = re.sub(re.escape(website), '', content_text, flags=re.IGNORECASE).strip()
                        content_text = "\n".join([line for line in content_text.split("\n") if line.strip()])
                    else:
                        content_text = "No content available"

                    content_text += f"\nStatus: {status}, Views: {views}"

                    slick_images = []
                    slick_elements = page.query_selector_all("div.slick-track img")
                    for img in slick_elements:
                        img_src = img.get_attribute("src")
                        if img_src:
                            slick_images.append(img_src.strip())

                    download_element = page.query_selector('li.download__list-item a.counter_link')
                    dumplinks = download_element.get_attribute("href") if download_element else ""

                    with page.expect_navigation(wait_until="domcontentloaded"):
                        page.go_back()
                    page.wait_for_selector("div.elem_ibody", timeout=10000)

                    card_data = leak_model(
                        m_screenshot=helper_method.get_screenshot_base64(page, company_name),
                        m_title=company_name,
                        m_url=page.url,
                        m_content=content_text + " " + self.base_url + " " + page.url,
                        m_websites=websites,
                        m_base_url=self.base_url,
                        m_network=helper_method.get_network_type(self.base_url),
                        m_important_content=content_text[:500],
                        m_content_type=["leaks"],
                        m_leak_date=helper_method.extract_and_convert_date(leak_date),
                        m_logo_or_images=slick_images,
                        m_dumplink=[dumplinks],
                    )

                    entity_data = entity_model(
                        m_email_addresses=helper_method.extract_emails(content_text),
                        m_phone_numbers=helper_method.extract_phone_numbers(content_text),
                        m_company_name=company_name,
                    )

                    self.append_leak_data(card_data, entity_data)

                except Exception as e:
                    print(f"Error processing card: {e}")

        except Exception as e:
            print(f"Error in parsing: {e}")










