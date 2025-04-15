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
   
    headers = {"name": "Alex",}
            #    "Content-Type" :"application/vnd.ms-exel"}
    return HttpResponse(body, headers=headers, status=500)







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
            if user.is_superuser:
                # Если это суперпользователь, показываем все опубликованные посты
                posts = Post.objects.filter(status='published')
            else:
                # Для обычных пользователей показываем их посты или разрешённые
                posts = Post.objects.filter(
                    status='published'
                ).filter(
                    models.Q(owner=user) | models.Q(allowed_users=user)
                ).distinct()
        else:
            # Если пользователь не авторизован, не показываем посты
            posts = Post.objects.none()

        context['pdf_posts'] = posts
        return context






#
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
