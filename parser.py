import requests
from bs4 import BeautifulSoup
import re

URL_1 = "https://www.chitai-gorod.ru/catalog/books-18030?page="
URL_2 = "https://www.labirint.ru/books/?page="
URL_3 = "https://book24.ru/catalog/page-"

BASE_URL_1 = "https://www.chitai-gorod.ru"
BASE_URL_2 = "https://www.labirint.ru"
BASE_URL_3 = "https://book24.ru"

 #Читай Город без хедера 403 выбрасывает
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
}

field_altnames = {
    "Book_cover": [
        "тип обложки", 
        "переплет"
    ],
    "Page_count": [
        "количество страниц",
        "страниц"
    ],
    "Weight": [
        "вес",
        "вес, г"
    ],
    "Size": [
        "размер",
        "размеры",
        "формат"
    ],
    "Publisher": [
        "издательство"
    ],
    "Series": [
        "серия"
    ],
    "Age_limit": [
        "возрастные ограничения",
        "возрастное ограничение"
    ],
    "Year": [
        "год издания"
    ],
    "ISBN": [
        "ISBN"
    ],
    "Product_ID": [
        "ID товара"
    ],
    "Genres": [
        "жанры"
    ],
    "Themes": [
        "тематика"
    ],
    "Product_type": [
        "тип товара"
    ],
    "Sections": [
        "разделы",
        "раздел"
    ],
    "Author": [
        "автор",
    ],
    "Translator": [
        "переводчик"
    ],
    "Language": [
        "язык"
    ],
    "Design": [
        "оформление"
    ],
    "Illustrations": [
        "иллюстрации"
    ],
    "Title": [
        "наименование"
    ],
    "Description": [
        "описание"
    ],
    "Price": [
        "цена"
    ]
}

def get_parsing_page(url: str):
    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        print(f'Something went wrong, response code = {response.status_code}')
        return None
    # if 'br' in response.headers.get('Content-Encoding', '').lower():
    #     decoded_content = brotli.decompress(response.content)
    #     text = decoded_content.decode('utf-8', errors='replace')
    #     return BeautifulSoup(text, "html.parser")
    return BeautifulSoup(response.text, "html.parser")

def normalize_field_name(s: str) -> str:
    return s.strip().replace(":", "").replace("\xa0", " ")

field_altnames_norm = {
    field: [alt.lower() for alt in alts]
    for field, alts in field_altnames.items()
}

def get_product_urls(url: str):
    card_class_names = ['product-card__image-holder', 'product-card__image-wrapper', 'product-cover__cover-wrapper']
    parsed_text = get_parsing_page(url)
    if not parsed_text:
        return None
    for card_class_name in card_class_names:
        product_cards =  parsed_text.find_all(class_=card_class_name)
        if product_cards:
            return [c.find_next('a').get_attribute_list('href')[0] for c in product_cards]

def get_raw_info(url: str):
    product_info_class_names = [
        ['product-characteristic__item', 'product-about__text', 'app-price product-sidebar-price__price'], 
        ['_feature_mmfyx_1', '_wrapper_1rsml_1', 'rubl text-bold-28-md-32'], 
        ['product-properties-item', 'product-description-short__text', 'product-offer-price__actual']
    ]
    parsed_text = get_parsing_page(url)
    if not parsed_text:
        return None
    for info_class_name in product_info_class_names:
        info = parsed_text.find_all(class_=info_class_name[0])
        if info:
            raw_info = [i.get_text() for i in info]
            author = parsed_text.find(class_='product-authors')
            if author:
                raw_info.append(f'Автор: {author.get_text()}')
            raw_info.append(f'Наименование: {parsed_text.find('h1').get_text()}')
            if parsed_text.find_all(class_=info_class_name[1]): raw_info.append(f'Описание: {parsed_text.find(class_=info_class_name[1]).get_text()}')
            if parsed_text.find_all(class_=info_class_name[2]): raw_info.append(f'Цена: {parsed_text.find(class_=info_class_name[2]).get_text()}')
            return raw_info
        

def get_info(url: str):
    cleared_info = {}
    raw_info = get_raw_info(url)
    if not raw_info:
        return None
    for line in raw_info:
        norm_line = normalize_field_name(line)
        low = norm_line.lower()
        for field, alts in field_altnames_norm.items():
            for alt in alts:
                if low.startswith(alt):
                    value = norm_line[len(alt):].strip(" :—-")
                    if field == 'ISBN': value = value.replace('-','')
                    if field == 'Weight': value = re.sub(r"\D", " ", value.replace('.', ''))
                    if field in ('Page_count', 'Weight', 'Size', 'Price'): value = re.sub(r"\D", "", value)
                    cleared_info[field] = value
                    break
            else:
                continue  
            break        
    print(len(cleared_info))        
    return cleared_info

def parser_produce(page_count=1, url_base=1):
    url = [[URL_1, BASE_URL_1], [URL_2, BASE_URL_2], [URL_3, BASE_URL_3]][url_base-1]
    result = []
    for page in range(1, page_count+1):
        print(url[0]+str(page))
        prod_urls = get_product_urls(url[0]+str(page))
        print(prod_urls)
        if not prod_urls:
            return None
        prod_info = map(lambda x: get_info(url[1]+x), prod_urls)
        result.extend(prod_info)
    return result

            

# print(get_product_urls(URL_2))
# print(get_info('https://www.chitai-gorod.ru/product/ne-izdevaysya-nagatoro-tom-4-ne-drazni-menya-nagatoro-san-dont-toy-with-me-miss-nagatoro-manga-3048147'))
# print(get_info('https://www.labirint.ru/books/1017140/'))
# print(get_info('https://book24.ru/product/ne-drazni-menya-nagatoro-san-tom-4-7096231/'))

print(parser_produce(1, 1))