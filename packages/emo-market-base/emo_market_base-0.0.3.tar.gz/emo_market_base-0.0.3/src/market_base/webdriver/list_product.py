from typing import Union
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


class ListProduct:

    # Nesne içindeki ad elemanı seçicisi
    name_locator = ()
    # Nesne içindeki link elemanı seçicisi
    link_locator = ()
    # Nesne içindeki ürün kodu elemanı seçicisi
    code_locator = ()
    # Nesne içindeki indirim beliteci elemanları seçicileri
    # İndirimli fiyat (üstü çizili) veya çok al az öde gibi
    # elemanların seçicileri "tuple" şeklinde eklenir
    discount_locators = []

    def __init__(self, element: WebElement) -> None:
        self.element = element
        self.name = None
        self.link = None
        self.code = None

        if self.name_locator:
            self.name = self.get_name()

        if self.link_locator:
            self.link = self.get_link()

        if self.code_locator:
            self.code = self.get_code()

    def get_name(self) -> Union[str, None]:
        try:
            el = self.element.find_element(*self.name_locator)
            return el.text.strip()
        except NoSuchElementException:
            return None

    def get_link(self) -> Union[str, None]:
        try:
            el = self.element.find_element(*self.link_locator)
            return el.get_attribute("href")
        except NoSuchElementException:
            return None

    def get_code(self) -> Union[str, None]:
        try:
            el = self.element.find_element(*self.code_locator)
            return el.text.strip()
        except NoSuchElementException:
            return None

    def is_discount(self) -> bool:
        for locator in self.discount_locators:
            try:
                el = self.element.find_element(*locator)
                if el:
                    return True
            except NoSuchElementException:
                pass

        return False
