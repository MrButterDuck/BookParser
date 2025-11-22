import json
from multiprocessing import Process
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .parser import parser_worker
from .models import Book

@staff_member_required
def admin_global_action(request):
    if request.method != "POST":
        return JsonResponse({"error": "Неверный метод"}, status=400)

    try:
        data = json.loads(request.body)
        page_count = int(data.get("value", 0))
        sites = data.get("sites", [])
    except Exception:
        return JsonResponse({"error": "Некорректные данные"}, status=400)

    if not (1 <= page_count <= 1000):
        return JsonResponse({"error": "Число вне диапазона"}, status=400)
    
    if not sites:
        return JsonResponse({"error": "Ни один сайт не выбран"}, status=400)

    json_resp = {'status': '', 'pid': []}
    if '1' in sites:
        p1 = Process(target=parser_worker, args=(page_count, "https://www.chitai-gorod.ru", "https://www.chitai-gorod.ru/catalog/books-18030?page="))
        p1.start()
        json_resp["status"] += "Parser Chitay-Gorod launched \n"
        json_resp["pid"].append(p1.pid)
    if '2' in sites:
        p2 = Process(target=parser_worker, args=(page_count, "https://www.labirint.ru", "https://www.labirint.ru/books/?page="))
        p2.start()
        json_resp["status"] += "Parser Labirint launched \n"
        json_resp["pid"].append(p2.pid)
    if '3' in sites:
        p3 = Process(target=parser_worker, args=(page_count, "https://book24.ru", "https://book24.ru/catalog/page-"))
        p3.start()
        json_resp["status"] += "Parser book24 launched \n"
        json_resp["pid"].append(p3.pid)

    return JsonResponse(json_resp)

def book_list(request):
    book_list = Book.objects.prefetch_related('author').all()
    paginator = Paginator(book_list, 100)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/book_list.html', {'page_obj': page_obj})

def book_detail(request, isbn):
    book = get_object_or_404(Book.objects.prefetch_related('author', 'publisher', 'genres'), isbn=isbn)
    return render(request, 'books/book_detail.html', {'book': book})