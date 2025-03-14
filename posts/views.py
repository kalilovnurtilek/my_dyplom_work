from django.shortcuts import render
from django.http import HttpResponse

def hello(request):
    body = "<h1>Hello</h1>"
    # body = """
#     <!DOCTYPE html>
# <html>
#     <head>
#         <title>Geek TEST</title>
#     </head>
# <body>

#         <h1>Загаловок первого уровня</h1>
#         <p>Параграф</p>

# </body>
# </html>
#     """

    headers = {"name": "Alex",}
            #    "Content-Type" :"application/vnd.ms-exel"}
    return HttpResponse(body, headers=headers, status=500)

def get_index(request):
    context = {
        "title" : "Главная страница",
        "my_list": [1,2,3,4],
    }
    return render(request, "posts/index.html", context=context)
def get_contacts(request):
    context = {
        "title": "Страница контакты"
    }
    return render(request, "posts/contact.html", context=context)

def get_about(request):
    context = {
        "title": "Страница о нас"
    }
    return render(request, "posts/about.html", context = context)

