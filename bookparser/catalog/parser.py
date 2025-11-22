import requests
from bs4 import BeautifulSoup
import re
from .models import Book, Author, Publisher, Genre

URL_1 = "https://www.chitai-gorod.ru/catalog/books-18030?page="
URL_2 = "https://www.labirint.ru/books/?page="
URL_3 = "https://book24.ru/catalog/page-"

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
        "жанры",
        "раздел"
    ],
    "Author": [
        "автор",
    ],
    "Title": [
        "наименование"
    ],
    "Description": [
        "описание"
    ],
    "Price": [
        "цена"
    ],
    "Image_Url": [
        "Изображение_обложки"
    ]
}


def get_parsing_page(url: str):
    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        print(f'Something went wrong, response code = {response.status_code}')
        return None
    return BeautifulSoup(response.text, "html.parser")

def normalize_field_name(s: str) -> str:
    return s.strip().replace(":", "").replace("\xa0", " ")

field_altnames_norm = {
    field: [alt.lower() for alt in alts]
    for field, alts in field_altnames.items()
}

def _find_first_matching(parsed, class_names):
    for name in class_names:
        found = parsed.find_all(class_=name)
        if found:
            return found
    return None

def _append_if_found(parsed, class_name, prefix, target_list):
    elem = parsed.find(class_=class_name)
    if elem:
        target_list.append(f'{prefix}{elem.get_text()}')

def get_product_urls(url: str):
    card_class_names = [
        'product-card__image-holder',
        'product-card__image-wrapper',
        'product-cover__cover-wrapper'
    ]
    parsed_text = get_parsing_page(url)
    if not parsed_text:
        return None
    product_cards = _find_first_matching(parsed_text, card_class_names)
    if product_cards:
        return [c.find_next('a').get_attribute_list('href')[0] for c in product_cards]

def _extract_common_info(parsed_text, info_class_name):
    info = parsed_text.find_all(class_=info_class_name[0])
    if not info:
        return None
    raw_info = [i.get_text() for i in info]
    raw_info.append(f'Наименование: {parsed_text.find("h1").get_text()}')
    author = parsed_text.find(class_='product-authors')
    if author:
        raw_info.append(f'Автор: {author.get_text()}')
    image = parsed_text.find(class_=info_class_name[3])
    if image:
        img_url = image.get('src')
        if img_url.startswith('http'):
            img_url = img_url[:]
        raw_info.append(f'Изображение_обложки {img_url}')
    _append_if_found(parsed_text, info_class_name[1], 'Описание: ', raw_info)
    _append_if_found(parsed_text, info_class_name[2], 'Цена: ', raw_info)
    return raw_info

def get_raw_info(url: str):
    product_info_class_names = [
        ['product-characteristic__item', 'product-about__text', 'app-price product-sidebar-price__price', 'product-poster__main-image'], 
        ['_feature_mmfyx_1', '_wrapper_1rsml_1', 'rubl text-bold-28-md-32', '_image_1qke2_7'], 
        ['product-properties-item', 'product-description-short__text', 'product-offer-price__actual', 'product-preview__placeholder']
    ]
    parsed_text = get_parsing_page(url)
    if not parsed_text:
        return None
    for info_class_name in product_info_class_names:
        raw_info = _extract_common_info(parsed_text, info_class_name)
        if raw_info:
            return raw_info

def _process_value(field, value):
    if field == 'ISBN':
        return value.replace('-', '')
    if field == 'Weight':
        return re.sub(r"\D", " ", value.replace('.', ''))
    if field in ('Page_count', 'Weight', 'Size', 'Price', 'Year'):
        if '.' in value:
            return re.sub(r"\D", "", value) + '0'
        return re.sub(r"\D", "", value)
    return value

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
                    value = _process_value(field, value)
                    cleared_info[field] = value
                    break
            else:
                continue
            break
    return cleared_info


def parser_worker(page_count, base_url, list_url):
    for page in range(1, page_count + 1):
        url_list = get_product_urls(list_url + str(page))
        for url in url_list:
            info = get_info(base_url + url)
            if not info or not info.get("ISBN"):
                continue

            obj, created = Book.objects.get_or_create(isbn=info["ISBN"])
            print(f'Book created: {base_url+ url}')
            for field, value in info.items():
                if field in ("ISBN", "Author", "Publisher", "Genres"):
                    continue
                current_value = getattr(obj, field.lower(), None)
                if current_value is None and value is not None:
                    setattr(obj, field.lower(), value)

            author_name = info.get("Author")
            if author_name:
                author_objs = []
                for a_name in author_name.split(','):
                    author_obj, _ = Author.objects.get_or_create(author_name=a_name.strip())
                    author_objs.append(author_obj)
                obj.author.set(author_objs)

            publisher_name = info.get("Publisher")
            if publisher_name:
                publisher_objs = []
                for p_name in publisher_name.split(','):
                    publisher_obj, _ = Publisher.objects.get_or_create(publisher_name=p_name.strip())
                    publisher_objs.append(publisher_obj)
                obj.publisher.set(publisher_objs)

            genre_names = info.get("Genres")
            if genre_names:
                genre_objs = []
                for g_name in genre_names.split(','):
                    genre_obj, _ = Genre.objects.get_or_create(gener_name=g_name.strip())
                    genre_objs.append(genre_obj)
                obj.genres.set(genre_objs)

            obj.save()



        
