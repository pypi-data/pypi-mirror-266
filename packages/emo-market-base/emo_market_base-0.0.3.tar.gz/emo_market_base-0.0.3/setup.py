from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    description = fh.read()

setup(
    name="emo_market_base",
    version="v0.0.3",
    author="Eren Mustafa Özdal",
    author_email="eren.060737@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    description="Marketlerden ürünleri kazıma işlemleri için temel pakettir",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/erenmustafaozdal/market-base",
    license='MIT',
    python_requires='>=3.11',
    install_requires=[
        "selenium_web_browser",
        "emo-cache-db",
        "emo-file-system",
        "pillow",
        "pdf2image",
    ],
)
