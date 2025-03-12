# from django.shortcuts import render
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
    print(request.user)
    if request.method=="GET":
        return HttpResponse("Главная страница")
    else:
        return HttpResponse("Не тот метод запроса")