from time import sleep
from typing import Dict, List, Union
from .list_product import ListProduct
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec


class CategoryPage:

    driver: Union[WebDriver, None] = None
    wait: Union[WebDriverWait, None] = None
    logger = None
    list_product: Union[ListProduct, None] = None

    with_loader: bool = False
    product_locator = ()

    def __init__(self, main, **kwargs) -> None:
        self.main = main
        self.driver = self.main.driver
        self.wait = WebDriverWait(self.driver, 10)

        self.link = kwargs.get("link")
        self.title = kwargs.get("title")
        self.data = {
            "link": self.link,
            "title": self.title,
            "products": []
        }

    def go(self):
        self.driver.get(self.link)
        self.main.is_page_load()
        self.logger.info(f"'{self.title}' kategorisi işlemleri başladı.")

    def scrape_products(self):
        self.data["products"] += self.fetch_products()

        self.logger.info(f"'{self.title}' kategorisi tamamlandı.")
        self.logger.info("--- İndirimli ürün sayısı: "
                         f"{len(self.data['products'])}")

    def get_products(self, el: Union[WebElement, None] = None) -> List:
        # eğer loader varsa tüm ürünlerin sayfaya
        # yüklenmesi için load işlemi yapılır
        product_count = 0
        while True:
            # sayfadaki ürünler alınır
            products = self.wait.until(ec.visibility_of_all_elements_located(
                self.product_locator
            ))

            # eğer loader yoksa döngüden çık
            if not self.with_loader:
                break

            # eğer sayfadaki ürün sayısı bir eki
            # döngüdeki ürün sayısı ile aynı ise
            # bu yeni ürün gelmedi demektir: çık
            if len(products) == product_count:
                break

            product_count = len(products)

            # sayfaya yeni eleman yükleme işlemi: kaydırm, button vs.
            self.load()
            sleep(0.5)

        return products

    def load(self):
        self.main.scroll_to_bottom()

    def fetch_products(self) -> List:
        els = self.get_products()

        data = []
        for el in els:
            result = self.fetch_product(el)
            if result:
                data.append(result)

        return data

    def fetch_product(self, el: WebElement) -> Union[Dict, None]:
        p_list = self.list_product(el)

        if p_list.is_discount():
            return {
                "name": p_list.name,
                "link": p_list.link,
                "code": p_list.code,
            }
