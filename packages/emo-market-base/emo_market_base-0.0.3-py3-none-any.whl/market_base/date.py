import logging
from datetime import datetime
from typing import Dict, List, Union
from selenium.webdriver.remote.webelement import WebElement


logger = logging.getLogger("MarketBaseDate")


class Date:

    @staticmethod
    def to_str(
        date: Union[datetime, None] = None,
        date_format: str = "%Y-%m-%d"
    ) -> str:
        if date is None:
            date = datetime.today()

        return date.strftime(date_format)

    @staticmethod
    def timestamp(date: Union[datetime, None] = None) -> int:
        if date:
            return date.timestamp()

        return datetime.now().timestamp()

    @classmethod
    def parse(cls, txt: str, _format: str = "%d %B %A") -> datetime:
        """Gelen tarih string verisini datetime nesnesine döndürür.
        Yılı hesaplar.

        Args:
            txt (str): tarih metin değeri
            _format (str): metinden çıkarılacak tarih formatı

        Returns:
            datetime: oluşturulan tarih nesnesi
        """
        if "-" in txt:
            return cls._parse_range(txt)

        return cls._parse_single(txt, _format)

    @classmethod
    def _parse_range(cls, txt: str, _format: str = "%d %B"):
        finish = txt.split('-')[1].strip()
        return cls._parse_single(finish, _format)

    @classmethod
    def _parse_single(cls, txt: str, _format: str) -> datetime:
        # Ay adı alınır
        month_name = cls.get_month_name(txt, _format)

        # Bulunduğumuz yıl alınır
        year = datetime.today().year

        # Bulunduğumuz ay Aralık ise ve
        # gelen tarih Ocak ayı ise yılı 1 arttır
        if datetime.today().month == 12 and month_name == "Ocak":
            year += 1

        # Belirlenen yıla göre tarih nesnesi oluştur
        _format += " %Y"
        return datetime.strptime(f"{txt} {year}", _format)

    @staticmethod
    def get_month_name(txt: str, _format: str):
        """Gelen tarih metni ve formatına göre ayın adını alır.
        Bunun için formattaki %B ile ay adının konumunu bulur 
        ve metinden döndürür.

        Args:
            txt (str): Tarih metni
            _format (str): Tarih formatı

        Returns:
            str: ay adı
        """
        format_parts = _format.split()
        i = format_parts.index("%B")
        return txt.split()[i]

    @classmethod
    def get_dates(
        cls,
        els: List[WebElement],
        excludes: Union[List, None]
    ) -> List:
        dates = []

        for el in els:
            # eğer tarih alınamadı ise geç
            try:
                date = cls.get_date(el, excludes)
                if date:
                    dates.append(date)
            except:
                continue

        logger.info(f"{len(dates)} adet tarih bilgisi alındı")

        return dates

    @classmethod
    def get_date(
        cls,
        el: WebElement,
        excludes: Union[List, None]
    ) -> Union[Dict, None]:
        if excludes and el.text in excludes:
            return

        return cls.date_dict(el)

    @classmethod
    def date_dict(cls, el: WebElement) -> Dict:
        return {
            "element": el,
            "text": el.text,
            "object": cls.parse(el.text)
        }

    @staticmethod
    def next_date(dates: List[Dict]) -> Dict:
        # Bugünün tarih ve saat bilgisini al
        today = datetime.today()

        # Saat ve dakikayı sıfırla
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        return next((d for d in dates if d["object"] >= today), None)

    @staticmethod
    def day_difference(
        start_date: Union[str, datetime],
        finish_date: Union[str, datetime, None] = None
    ) -> int:
        """İki tarih arasındaki gün farkını bulur

        Args:
            start_date (str): son kazıma tarihi. Format: "%Y-%m-%d"
            threshold_days (int, optional): Geçmesi gereken süre. Defaults to 7.

        Returns:
            bool: "Kazıma zamanı geldi mi" sonucu
        """

        # String tarihini datetime nesnesine dönüştür
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if finish_date is None:
            finish_date = datetime.today()
        elif isinstance(finish_date, str):
            finish_date = datetime.strptime(finish_date, "%Y-%m-%d")

        # Tarih farkını hesapla
        difference = finish_date - start_date

        # Farkı gün cinsine dönüştür ve threshold_days ile karşılaştır
        return difference.days
