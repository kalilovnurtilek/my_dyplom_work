from django.shortcuts import render
from django.http import HttpResponse
from posts.models import Post
from django.urls import reverse_lazy
from django.views import generic

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






# def get_index(request):
#     posts = Post.objects.filter(status=True)
#     context = {
#         "title" : "Главная страница",
#         "posts":posts,
#     }
#     return render(request, "posts/index.html", context=context)



def get_contacts(request):
    context = {
        "title": "Страница контакты"
    }
    return render(request, "posts/contact.html", context=context)


class IndexView(generic.ListView):
    queryset = Post.objects.filter(status=True)
    context_object_name='posts'
    # model =Post
    template_name= "posts/index.html"

class PostDetailView(generic.DetailView):
    model =Post
    context_object_name ='post'
    template_name= "posts/post_detail.html"

class PostCreateView(generic.CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    fields=["title","content"]
    success_url = reverse_lazy("index-page")

class PostUpdateView(generic.UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    fields=["title","content"]
    success_url = reverse_lazy("index-page")


class PostDeleteView(generic.DeleteView):
    model = Post
    success_url= reverse_lazy("index-page")



class AboutView(generic.TemplateView):
    template_name="posts/about.html"
    extra_context = {
        "title": "Страница о нас"
    }
    

#def get_about(request):
#     context = {
#         "title": "Страница о нас"
#     }
#     return render(request, "posts/about.html", context = context)


# def get_post(request):
#     context = {
#         "title":"Получить сообщение"
#     }
#     return render(request, "posts/post_create.html", context=context)

# def update_post(request):
#     context = {
#         "title":"Изменить сообщение"
#     }
#     return render(request, "posts/post_update.html", context=context)

# def delete_post(request):
#     context = {
#         "title":"Удалить пост"
#     }
#     return render(request, "posts/post_deletehtml", context=context)