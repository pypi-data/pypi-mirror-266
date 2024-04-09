import logging
import requests
from typing import List, Union
from pdf2image import convert_from_path
from file_system.file import File as FileCore


logger = logging.getLogger("MarketBaseFile")


class File:

    @staticmethod
    def mk_dir(base_path: str, **kwargs) -> str:
        path = base_path.format(**kwargs)
        if not FileCore.exists(path):
            FileCore.create_directory(path)
            logger.info(f"'{path}' dizini oluşturuldu.")

        return path

    @staticmethod
    def clean_filename(filename: str):
        # İstenmeyen karakterlerin bulunduğu bir karakter kümesi oluşturun
        invalid_chars = '<>:"/\\|?*'

        # İstenmeyen karakterleri temizleyin
        chars = [c for c in filename if c not in invalid_chars]
        cleaned_filename = ''.join(chars)
        logger.info("Dosya adı temizlendi. "
                    f"'{filename}' -> '{cleaned_filename}'")

        return cleaned_filename

    @staticmethod
    def download(src: str, dest: str) -> Union[str, None]:
        """
        İnternetten bir kaynağın indirilmesini ve hedefe kaydedilmesini sağlar

        Args:
            src (str): kaynak adresi
            dest (str): yerel hedef yolu

        Returns:
            str: _description_
        """
        # dosya adı belirlenir
        filename = FileCore.get_filename(src)

        try:
            response = requests.get(src)
            if response.status_code == 200:
                file_path = f"{dest}/{filename}"
                with open(f"{dest}/{filename}", "wb") as file:
                    file.write(response.content)

                return file_path
            else:
                logger.error(f"----- {src} adresinden dosya indirilemedi.")
                return None
        except Exception as e:
            logger.error(f"----- Dosya indirilirken hata oluştu: {e}")
            return None

    @staticmethod
    def pdf_to_images(pdf_path: str, dest: str) -> List:
        image_paths = []

        # PDF dosyasını görüntü dosyalarına dönüştür
        images = convert_from_path(pdf_path)

        # dosya adını al
        filename = FileCore.get_filename(pdf_path, without_extentsion=True)

        for i, image in enumerate(images, start=1):
            # görüntü dosyasının adını oluştur
            image_path = f"{dest}/{filename}_page_{i}.jpg"
            image.save(image_path)
            image_paths.append(image_path)
            logger.info(f"'{image_path}' görseli oluşturuldu.")

        return image_paths
