from abc import ABC
from datetime import datetime

from typing import List

from playwright.sync_api import Page
from urllib.parse import urljoin
from crawler.crawler_instance.local_interface_model.leak.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.data_model.entity_model import entity_model
from crawler.crawler_instance.local_shared_model.data_model.leak_model import leak_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchProxy, FetchConfig
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS
from crawler.crawler_services.shared.helper_method import helper_method


class _b1nd(leak_extractor_interface, ABC):
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
      cls._instance = super(_b1nd, cls).__new__(cls)
    return cls._instance

  @property
  def seed_url(self) -> str:
    return "http://b1nd.net"

  @property
  def base_url(self) -> str:
    return "http://b1nd.net"

  @property
  def rule_config(self) -> RuleModel:
    return RuleModel(m_fetch_proxy=FetchProxy.NONE, m_fetch_config=FetchConfig.PLAYRIGHT)

  @property
  def card_data(self) -> List[leak_model]:
    return self._card_data

  @property
  def entity_data(self) -> List[entity_model]:
    return self._entity_data

  def invoke_db(self, command: REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, default_value):
    return self._redis_instance.invoke_trigger(command, [key.value + self.__class__.__name__, default_value])

  def contact_page(self) -> str:
    return self.seed_url

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
      element = page.locator(selector).first
      if element.count() > 0:
        return element.get_attribute(attr) if attr else element.inner_text().strip()
    except Exception:
      return None

  def parse_leak_data(self, page: Page):
    try:
      outer_list = []
      page.goto(self.seed_url)
      page.wait_for_load_state("load")

      outer_elements = page.query_selector_all("h3.node-title a")
      for element in outer_elements:
        href = element.get_attribute("href")
        if href:
          outer_list.append(urljoin(self.base_url, href))

      for outer_link in outer_list:

        page.goto(outer_link)
        page.wait_for_load_state("load")

        while True:
          inner_list = []
          inner_elements = page.query_selector_all("div.structItem-title a")

          for element in inner_elements:
            href = element.get_attribute("href")
            if href:
              inner_list.append(urljoin(self.base_url, href))

          for inner_link in inner_list:
            try:

              page.goto(inner_link)
              page.wait_for_load_state("load")

              m_description = self.safe_find(page, ".p-description")
              m_leak_date = self.safe_find(page, "time.u-dt")
              m_content = self.safe_find(page, "div.bbWrapper")
              title = self.safe_find(page, "h1.p-title-value")

              if m_content:
                words = m_content.split()
                if len(words) > 500:
                  m_important_content = " ".join(words[:500])
                else:
                  m_important_content = m_content
              else:
                m_important_content = ""
              m_leak_date = datetime.strptime(m_description.split("\n")[3], '%b %d, %Y').date()

              card_data = leak_model(
                m_screenshot=helper_method.get_screenshot_base64(page, title),
                m_title=title,
                m_weblink=[inner_link],
                m_url=inner_link,
                m_base_url=self.base_url,
                m_content=m_content if m_content else "" + " " + self.base_url + " " + inner_link,
                m_network=helper_method.get_network_type(self.base_url),
                m_important_content=m_important_content,
                m_content_type=["leaks"],
                m_leak_date=m_leak_date
              )

              entity_data = entity_model()
              self.append_leak_data(card_data, entity_data)

            except Exception as _:
              continue

          next_button = page.query_selector(".block-router-main .pageNav-jump--next")
          if next_button:
            next_url = next_button.get_attribute("href")
            if next_url:

              page.goto(urljoin(self.base_url, next_url))
              page.wait_for_load_state("load")
              continue
            else:
              break
          else:
            break

    except Exception as e:
      print(f"An error occurred: {e}")
    finally:
      self.invoke_db(REDIS_COMMANDS.S_SET_BOOL, CUSTOM_SCRIPT_REDIS_KEYS.URL_PARSED, True)
