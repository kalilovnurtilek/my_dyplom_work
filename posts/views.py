from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from posts.models import Post
from posts.forms import  PostForm, CommentForm
from django.db.models import Q
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.db import models    




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


class IndexView(generic.TemplateView):
    template_name = 'posts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        if user.is_authenticated:
            posts = Post.objects.filter(
                status='published'
            ).filter(
                models.Q(owner=user) | models.Q(allowed_users=user)
            ).distinct()
        else:
            posts = Post.objects.none()

        context['pdf_posts'] = posts
        return context








# class PostDetailView(generic.DetailView):
#     model =Post
#     context_object_name ='post'
#     template_name= "posts/post_detail.html"

#     def post(self, request, pk):
#         # post_id = request.POST.get("post_id",None)
#         post= Post.objects.all()
#         form = CommentForm(request.POST)

#         # name=request.POST.get("name", None)
#         # text = request.POST.get('text', None)
#         # if name and text:
#         #     comment = Comment.objects.create(name=name,text=text,post=post)
#         #     comment.save()

#         if form.is_valid():
#             pre_saved_comment = form.save(commit=False)
#             pre_saved_comment.post=post
#             pre_saved_comment.save()

#             return redirect('post-detail', pk)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["form"]= CommentForm()
    #     context["title"]="Просмотр поста" 
    #     return context

# class PostCreateView(generic.CreateView):
#     model = Post
#     template_name = 'posts/post_create.html'
#     fields = ['title', 'content', 'pdf_file', 'allowed_users', 'status']

#     def get_success_url(self):
#         return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})

class PostCreateView(generic.CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    form_class = PostForm  # Убедитесь, что форма указана правильно
    success_url = reverse_lazy("index-page")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Устанавливаем владельца поста
        print("Saving post...")
        form.save()  # Явно сохраняем объект
        return super().form_valid(form)

    
class PostUpdateView(generic.UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    form_class = PostForm
    success_url = reverse_lazy("index-page")


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comment_set.all()  # или post.comments.all(), если related_name указан
        context['form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            if request.user.is_authenticated:
                full_name = f"{request.user.first_name} {request.user.last_name}".strip()
                comment.author = full_name if full_name else request.user.email
            else:
                comment.author = "Аноним"

            comment.save()

        return redirect('post-detail', pk=post.pk)

        
 
class AboutView(generic.TemplateView):
    template_name="posts/about.html"
    extra_context = {
        "title": "Страница о нас"
    }
    

class PostDeleteView(generic.DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:post_list')  # Ссылка на страницу, куда направит после успешного удаления
