from typing import Dict, Tuple, Union
from ..date import Date
from ..filesytem import File
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


class Product:

    _logger = None

    brand_locator = ()
    name_locator = ()
    description_locator = ()
    old_price_locator = ()
    price_locator = ()
    discount_rate_locator = ()
    has_image = True
    image_locator = ()
    image_is_download = False

    def __init__(
        self,
        element: WebElement,
        image_path: Union[str, None] = None,
        **kwargs
    ) -> None:
        """Web sitesindeki ürün elemanı üzerinde işlemler yapar.
        Bilgiler toplar ve görseli kaydeder.

        Args:
            element (WebElement): Selenium Web Element nesnesi
            image_path (Union[str, None], optional): Görselin kaydedileceği dizin. Defaults to None.
        """
        self._element = element
        self._image_path = image_path

        for key in kwargs.keys():
            setattr(self, key, kwargs.get(key))

        if self.brand_locator and not hasattr(self, "brand"):
            self.brand = self.get_brand()

        if self.name_locator and not hasattr(self, "name"):
            self.name = self.get_name()

        if self.description_locator and not hasattr(self, "description"):
            self.description = self.get_description()

        if self.old_price_locator and not hasattr(self, "old_price"):
            self.old_price = self.get_old_price()

        if self.price_locator and not hasattr(self, "price"):
            self.price = self.get_price()

        if self.discount_rate_locator and not hasattr(self, "discount_rate"):
            self.discount_rate = self.get_discount_rate()

        if self.has_image and not hasattr(self, "image"):
            self.image = self.get_image()

    def get_brand(self) -> Union[str, None]:
        try:
            el = self._element.find_element(*self.brand_locator)
            text = el.text.strip()
            self._logger.info(f"--- Marka: {text}")
            return text
        except NoSuchElementException:
            return None

    def get_name(self) -> Union[str, None]:
        try:
            el = self._element.find_element(*self.name_locator)
            text = el.text.strip()
            self._logger.info(f"--- Ürün Adı: {text}")
            return text
        except NoSuchElementException:
            return None

    def get_description(self) -> Union[str, None]:
        try:
            el = self._element.find_element(*self.description_locator)
            text = el.text.strip()
            self._logger.info(f"--- Açıklama: {text}")
            return text
        except NoSuchElementException:
            return None

    def get_old_price(self) -> Union[str, None]:
        try:
            el = self._element.find_element(*self.old_price_locator)
            text = el.text.strip()
            self._logger.info(f"--- Eski Fiyat: {text}")
            return text
        except NoSuchElementException:
            return None

    def get_price(self) -> Union[str, None]:
        try:
            el = self._element.find_element(*self.price_locator)
            text = el.text.strip()
            self._logger.info(f"--- Fiyat: {text}")
            return text
        except NoSuchElementException:
            return None

    def get_discount_rate(self) -> Union[str, None]:
        try:
            el = self._element.find_element(*self.discount_rate_locator)
            text = el.text.strip()
            self._logger.info(f"--- İndirim Oranı: {text}")
            return text
        except NoSuchElementException:
            return None

    def _image_name(self) -> str:
        timestamp = Date.timestamp()
        filename = f"{self.name}-{timestamp}"
        filename = File.clean_filename(filename)
        return f"{self._image_path}/{filename}.png"

    def get_image(self) -> str:
        # görsel seçici varsa yeni eleman belirle
        el = self._element
        if self.image_locator:
            el = self._element.find_element(*self.image_locator)

        # eğer indirme ise indir
        if self.image_is_download:
            src = el.get_attribute("src")
            image = File.download(src, self._image_path)
            self._logger.info(f"--- Görsel: {image}")
            return image

        image = self._image_name()
        el.screenshot(image)
        self._logger.info(f"--- Görsel: {image}")
        return image

    def has_attribute(self, locator: Tuple[str, str]) -> bool:
        try:
            el = self._element.find_element(*locator)
            if el:
                return True
        except NoSuchElementException:
            pass

        return False

    def get_price_text(self, html_text: str) -> str:
        return html_text.replace("₺", "").replace("\n", "")

    def price_to_float(self, price_text: str) -> float:
        price_text = price_text.replace(".", "").replace(",", ".")
        return float(price_text)

    def get_data(self) -> Dict:
        data = {}

        for attr, value in vars(self).items():
            if attr.startswith('_') or attr.startswith('__'):
                continue
            data[attr] = value

        return data
