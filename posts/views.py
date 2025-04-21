# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from posts.models import Post, ApprovalStep, Specialty
from posts.forms import PostForm, CommentForm, SpecialtyForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
# from .utils.pdf_generator import generate_post_pdf  # добавили







class SuperuserPostListView(UserPassesTestMixin, ListView):
    model = Post
    template_name = 'posts/superuser_post_list.html'
    context_object_name = 'posts'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = Post.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset



class PostCreateView(generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = get_user_model().objects.all()
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.owner = self.request.user
        post.save()
        form.save_m2m()  # сохранит specialty

        # Создаём этапы согласования
        approver_ids = self.request.POST.getlist('approvers[]')
        for i, uid in enumerate(approver_ids):
            user = get_user_model().objects.get(pk=uid)
            ApprovalStep.objects.create(post=post, user=user, order=i+1)

        return redirect('index-page')

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
        action = request.POST.get("action")

        if action == "approval":
            current_step = post.approval_steps.filter(is_approved=None).order_by("order").first()
            if current_step and current_step.user == request.user:
                current_step.is_approved = "approve" in request.POST
                current_step.reviewed_at = timezone.now()
                current_step.save()

                if not current_step.is_approved:
                    post.status = "draft"
                    post.save()
                elif not post.approval_steps.filter(is_approved=None).exists():
                    post.status = "published"
                    post.save()
            return redirect("post-detail", pk=post.pk)

        elif action == "comment":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user.get_full_name() or request.user.email
                comment.save()
            return redirect("post-detail", pk=post.pk)

        return redirect("post-detail", pk=post.pk)




class CreateSpeciltyView(generic.CreateView):
    model = Specialty
    template_name = 'posts/specialty_create.html'
    fields=["name","code"]
    success_url = reverse_lazy("create-special")
    form = SpecialtyForm   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        specialties = Specialty.objects.all()
        if query:
            specialties = specialties.filter(name__icontains=query)
        context["specialties"] = specialties
        return context


class IndexView(generic.TemplateView):
    template_name = 'posts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            context['my_posts'] = Post.objects.filter(owner=user)

        # Посты, которые ещё нужно согласовать
            context['approval_posts'] = Post.objects.filter(
            approval_steps__user=user,
                approval_steps__is_approved=None
            ).distinct()

        # Посты, которые пользователь уже согласовал
            context['approved_posts'] = Post.objects.filter(
                approval_steps__user=user,
                approval_steps__is_approved=True
            ).distinct()

        return context

class PostUpdateView(generic.UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    form_class = PostForm
    success_url = reverse_lazy("index-page")

class AboutView(generic.TemplateView):
    template_name="posts/about.html"
    extra_context = {
        "title": "Страница о нас"
    }
    

class PostDeleteView(generic.DeleteView):
    model = Post
    success_url= reverse_lazy("index-page")