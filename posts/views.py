from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic

from posts.models import Post
from posts.forms import CommentForm, PostForm

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

    def post(self, request, pk):
        # post_id = request.POST.get("post_id",None)
        post= Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        # name=request.POST.get("name", None)
        # text = request.POST.get('text', None)
        # if name and text:
        #     comment = Comment.objects.create(name=name,text=text,post=post)
        #     comment.save()

        if form.is_valid():
            pre_saved_comment = form.save(commit=False)
            pre_saved_comment.post=post
            pre_saved_comment.save()

            return redirect('post-detail', pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"]= CommentForm()
        context["title"]="Просмотр поста" 
        return context

class PostCreateView(generic.CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    fields=["title","content"]
    success_url = reverse_lazy("index-page")
    form = PostForm

class PostUpdateView(generic.UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    form_class = PostForm
    success_url = reverse_lazy("index-page")


class PostDeleteView(generic.DeleteView):
    model = Post
    success_url= reverse_lazy("index-page")

 
class AboutView(generic.TemplateView):
    template_name="posts/about.html"
    extra_context = {
        "title": "Страница о нас"
    }
    
