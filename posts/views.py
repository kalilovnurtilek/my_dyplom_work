from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from .forms import PDFPostForm
from .models import PDFPost
from django.contrib.auth.decorators import login_required
from posts.models import Post
from posts.forms import CommentForm, PostForm

from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import PDFPost




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
    


@login_required
def upload_pdf(request):
    if request.method == 'POST':
        form = PDFPostForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_post = form.save(commit=False)
            pdf_post.owner = request.user
            pdf_post.save()
            form.save_m2m()  # Сохраняем ManyToMany
            return redirect('index-page')  # Перенаправление на список
    else:
        form = PDFPostForm()
    return render(request, 'posts/upload_pdf.html', {'form': form})

@login_required
def view_pdf(request, post_id):
    post = get_object_or_404(PDFPost, id=post_id)

    if request.user == post.owner or request.user in post.allowed_users.all():
        return FileResponse(post.pdf_file.open(), content_type='application/pdf')
    else:
        return HttpResponseForbidden("У вас нет доступа к этому PDF.")
    

# def my_pdfs_view(request):
#     # Ваша логика для обработки запроса
#     return render(request, 'posts/my_pdfs.html')  # или другая логика