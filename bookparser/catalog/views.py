import json
import time
import asyncio
from django.http import StreamingHttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from .parser import get_product_urls, get_info
from .models import Product

# Асинхронная функция, которая возвращает словарь

    

@staff_member_required
def admin_global_action(request):
    if request.method != "POST":
        return StreamingHttpResponse("Неверный метод.", content_type="text/plain")

    try:
        data = json.loads(request.body)
        page_count = int(data.get("value", 0))
    except Exception:
        return StreamingHttpResponse("Ошибка: некорректные данные.", content_type="text/plain")

    if not (1 <= page_count <= 1000):
        return StreamingHttpResponse("Ошибка: число вне диапазона.", content_type="text/plain")

    def event_stream():
        yield "Старт обработки...\n"
        for page in range(1, page_count+1):
            prod_urls = get_product_urls("https://www.chitai-gorod.ru/catalog/books-18030?page=")
            print(prod_urls)
            if not prod_urls:
                return None
            yield f"Готово {len(prod_urls)} для обряботки с {page} страници\n"
            for url in prod_urls:
                prod_info = get_info('https://www.chitai-gorod.ru'+url)
                if not prod_info.get('ISBN'):
                    continue
                obj, created = Product.objects.get_or_create(isbn=prod_info["ISBN"])
                print(created)
                for field, value in prod_info.items():
                    if field in ("ISBN", "Publisher"):
                        continue 
                    current_value = getattr(obj, field.lower(), None)
                    if current_value is None and value is not None:
                        setattr(obj, field.lower(), value)

                obj.save()
                yield f"Объект {prod_info['ISBN']} обновлен\n"

        yield "Готово! 🎉\n"

    return StreamingHttpResponse(event_stream(), content_type="text/plain")