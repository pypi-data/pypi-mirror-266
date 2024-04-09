import locale
from .category_page import CategoryPage
from .product_page import ProductPage
from ..filesytem import File
from ..date import Date
from ..db import DB
from .category_page import CategoryPage
from .product_page import ProductPage
from typing import Dict, List, Self, Tuple, Union
from selenium_web_browser.browser import Browser
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec


class Market:

    URL: str = ""
    IMAGES_DIR: str = ""

    browser: Union[Browser, None] = None
    driver: Union[WebDriver, None] = None
    wait: Union[WebDriverWait, None] = None
    logger = None

    # Veritabanı özellikleri
    db_path = ""
    db: Union[DB, None] = None

    category_page: Union[CategoryPage, None] = None
    product_page: Union[ProductPage, None] = None

    # SEÇİCİLER
    page_load_element = ()  # [seçici türü, seçici]
    cookie_element = ()  # [seçici türü, seçici]
    category_link_locator = ()
    category_name_locator = ()

    # JAVASCRIPTS
    remove_element_script = "arguments[0].remove()"
    scroll_to_element_script = "arguments[0].scrollIntoView({block: 'center'});"
    scroll_to_bottom_script = "window.scrollTo(0, document.body.scrollHeight);"

    def __new__(cls) -> Self:

        if not cls.browser or not cls.driver:
            cls.browser = Browser()
            cls.driver = cls.browser.disable_logging() \
                .increase_performance() \
                .set_window_size() \
                .run() \
                .maximize_window() \
                .get()
            cls.wait = WebDriverWait(cls.driver, 10)

        return super().__new__(cls)

    def __init__(self):
        # tarih bilgileri Türkçe olması için çeviri yap
        locale.setlocale(locale.LC_TIME, "tr_TR")

        # veritabanı çalıştırılır
        self.db = DB(self.db_path)

    def is_page_load(self):
        """Gelen locator bilgisine göre sayfanın yüklenmesini bekler"""
        self.wait.until(ec.visibility_of_element_located(
            self.page_load_element
        ))

    def accept_cookie(self):
        """Sitede çerezleri kabul edecek metot"""
        try:
            self.wait.until(ec.element_to_be_clickable(
                self.cookie_element
            )).click()
            self.logger.info("Çerezler kabul edildi")
        except TimeoutException:
            self.logger.info("Çerez kabul etme paneli gelmedi")

    def go(self):
        self.driver.get(self.URL)
        self.is_page_load()
        self.accept_cookie()

        self.logger.info(f"'{self.URL}' adresine gidildi.")

    def remove_elements(self, locator: Tuple[str, str], element: Union[WebElement, None] = None):
        # eğer gönderilen bir web elemanı değilse seç
        select_from = self.driver if element is None else element
        try:
            els = select_from.find_elements(*locator)
        except:
            els = []

        for el in els:
            self.driver.execute_script(self.remove_element_script, el)

    def scroll_to_element(self, el: Union[WebElement, Tuple[str, str]]):
        # eğer gönderilen bir web elemanı değilse seç
        if not isinstance(el, WebElement):
            el = self.driver.find_element(*el)

    def scroll_to_bottom(self):
        self.driver.execute_script(self.scroll_to_bottom_script)

    def get_next_date(self, excludes: List, locator: Tuple[str, str]) -> Dict:
        els = self.driver.find_elements(*locator)
        dates = Date.get_dates(els, excludes)
        return Date.next_date(dates)

    def create_date_directory(self, date: Union[Dict, None] = None):
        date = date["object"] if date else date
        date_str = Date.to_str(date)
        return File.mk_dir(self.IMAGES_DIR, date=date_str)

    def get_product_elements(self, locator: Tuple[str, str]):
        return self.driver.find_elements(*locator)

    def update_excludes(self, txt: str, key: str, excludes: List):
        excludes.append(txt)
        self.db.set(key, excludes)

    def save_last_scrape_date(self):
        today_str = Date.to_str()
        self.db.set("last_scrape_date", today_str)
        self.logger.info(f"Kontrol tarihi kaydedildi: {today_str}")

    def is_it_time_to_scrape(self, threshold_days: int = 7) -> bool:
        """Gönderilen son kazıma tarihi baz alınarak, istenen sürenin geçip
        geçmediğini kontrol ederek "kazıma zamanı geldi mi" karar verir.

        Args:
            threshold_days (int, optional): Geçmesi gereken süre. Defaults to 7.

        Returns:
            bool: "Kazıma zamanı geldi mi" sonucu
        """
        last_date = self.db.get("last_scrape_date")

        # son tarih yoksa daha önce bilgiler alınmamıştır.
        # Bu durumda bilgiler alınabilir.
        if last_date is None:
            return True

        difference = Date.day_difference(last_date)

        # Farkı gün cinsine dönüştür ve threshold_days ile karşılaştır
        if difference >= threshold_days:
            return True

        self.logger.info(
            f"Son kontrolden '{difference}' gün geçtiği için iptal edildi.")
        return False

    def get_products(self) -> Dict:
        # kontrol tarihi geldi mi
        if not self.is_it_time_to_scrape():
            return {}

        products = self.get_discount_product()

        if products:
            self.save_last_scrape_date()

        self.driver.close()
        return products

    def get_discount_product(self) -> Dict:
        self.go()

        # Önce kategoriler alınır.
        categories = self.get_categories()

        # kategorilerden indirimli ürünler alınır
        product_list = self.fetch_category_products(
            self.category_page,
            categories
        )

        self.IMAGES_DIR = self.create_date_directory()
        return self.fetch_products(self.product_page, product_list)

    def get_categories(self) -> List:
        category_elems = self.driver.find_elements(*self.category_link_locator)

        categories = []

        for el in category_elems:
            categories.append({
                "link": el.get_attribute("href"),
                "title": el.find_element(*self.category_name_locator).text.strip()
            })

        self.logger.info(f"{len(categories)} adet ürün kategorisi alındı.")
        return categories

    def merge_products(self, data: List) -> List:
        """Gelen kategori listesindeki, her kategoride bulunan ürünleri
        tek bir liste haline getirir

        Args:
            data (List): İçinde ürünlerin de bulunduğu kategorilerden oluşan liste

        Returns:
            List: Ürün listesi
        """
        new_data = []
        for category in data:
            for product in category["products"]:
                product["category"] = category["title"]
                new_data.append(product)

        return new_data

    def fetch_category_products(
        self,
        category_page: CategoryPage,
        categories: List[Dict]
    ) -> List:

        # category: {"link": "...", "title": "..."}
        data = []
        for category in categories:
            page: CategoryPage = category_page(self, **category)
            page.go()
            # ilgili kategori ürün bilgileri alınırken bir hata oluşursa geç
            try:
                page.scrape_products()
            except:
                continue
            data.append(page.data)

        return self.merge_products(data)

    def fetch_products(self, product_page: ProductPage, products: List) -> Dict:
        data = {}  # 'code': product

        # Ürünler gezilir
        # product: {
        #   'category': '...',
        #   'sub_category': '...',
        #   'name': '...',
        #   'link': '...',
        #   'code': '...'
        # }
        for product in products:
            # eğer aynı ürün varsa geç
            if product["code"] in data.keys():
                continue

            try:
                page = product_page(self, **product)
                page.go()
                result = page.get_product()
                data[result["code"]] = result
            except Exception as e:
                self.logger.error("Ürün Bilgileri alınırken hata oldu: "
                                  f"{product}")
                self.logger.error(f"--- Hata: {e}")

        return data
