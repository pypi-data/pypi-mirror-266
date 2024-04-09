from typing import Dict, Union
from .product import Product
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class ProductPage:

    driver: Union[WebDriver, None] = None
    wait: Union[WebDriverWait, None] = None
    _logger = None
    product: Union[Product, None] = None

    product_locator = ()

    def __init__(self, main, **kwargs) -> None:
        self.main = main
        self.driver = self.main.driver
        self.wait = WebDriverWait(self.driver, 10)
        self.kwargs = kwargs

    def go(self):
        self.driver.get(self.kwargs["link"])
        self.main.is_page_load()
        info = self.kwargs.get("name", self.kwargs.get("link"))
        self._logger.info(f"'{info}' ürünü işlemleri başladı.")

    def pre_process(self, el: WebElement):
        """
        Bu metot extend edilen sınıflarda genişletilebilir. Belirli 
        script'lerle sayfadaki bazı değişiklikler yapılabilir. Örneğin; 
        bazı elemanlar silinebilir, eleman boyutları düzeltilebilir.
        """
        pass

    def get_product(self) -> Dict:
        by_type, selector = self.product_locator
        selector = selector.format(**self.kwargs)
        el = self.driver.find_element(by_type, selector)

        self.pre_process(el)

        product = self.product(el, self.main.IMAGES_DIR, **self.kwargs)

        return product.get_data()
