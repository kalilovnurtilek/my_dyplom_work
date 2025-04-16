from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from posts.models import Post, ApprovalStep
from posts.forms import  PostForm, CommentForm
from django.db.models import Q
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.db import models    
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)




# @staff_member_required  # Этот декоратор ограничивает доступ только для суперпользователей
# def user_list(request):
#     users = User.objects.all()  # Получаем всех пользователей
#     return render(request, 'users/user_list.html', {'users': users})





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






logger = logging.getLogger(__name__)

class PostCreateView(generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = get_user_model().objects.all()  # Передаем список пользователей в контекст
        return context

    def form_valid(self, form):
        logger.debug("Form is valid, preparing to save post...")
    
        if not form.is_valid():
            logger.error(f"Form is not valid: {form.errors}")
            return super().form_invalid(form)  # Отправляем обратно, если форма не валидна

        post = form.save(commit=False)
        post.owner = self.request.user
        logger.debug(f"Saving post with title: {post.title}")
        post.save()

        approval_users = form.cleaned_data['approval_users']
        logger.debug(f"Approval users: {approval_users}")

        for i, user in enumerate(approval_users):
            ApprovalStep.objects.create(post=post, user=user, order=i+1)
            logger.debug(f"Created approval step for {user.get_full_name()} with order {i+1}")

    # Проверяем редирект
        try:
            response = redirect('post-detail', pk=post.pk)
            logger.debug(f"Redirecting to: {response.url}")
            return response
        except Exception as e:
            logger.error(f"Error during redirect: {e}")
            return super().form_invalid(form)



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
        context['comments'] = post.comment_set.all()
        context['form'] = CommentForm()

        user = self.request.user
        if user.is_authenticated:
            current_step = post.approval_steps.filter(is_approved=None).order_by('order').first()
            context['can_approve'] = current_step and current_step.user == user
            context['approval_step'] = current_step

        context['approval_steps'] = post.approval_steps.select_related('user')
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        if 'approve' in request.POST or 'reject' in request.POST:
            current_step = post.approval_steps.filter(is_approved=None).order_by('order').first()

            if current_step and current_step.user == request.user:
                current_step.is_approved = 'approve' in request.POST
                current_step.reviewed_at = timezone.now()
                current_step.save()

                if not current_step.is_approved:
                    post.status = 'draft'
                    post.save()
                elif not post.approval_steps.filter(is_approved=None).exists():
                    post.status = 'published'
                    post.save()

            return redirect('post-detail', pk=post.pk)

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
    success_url= reverse_lazy("index-page")