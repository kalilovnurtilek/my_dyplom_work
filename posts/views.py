import os
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import ListView

from posts.forms import CommentForm, PostForm, SpecialtyForm, SubjectForm
from posts.models import ApprovalStep, Cours, Post, PostSubject, Specialty, Subject
from .utils.pdf_generator import generate_post_pdf


def serve_pdf(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(filepath):
        raise Http404("Файл табылган жок")
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


def generate_unique_protocol_number():
    year = datetime.now().year
    last_post = Post.objects.filter(protocol_number__startswith=str(year)).order_by('-id').first()
    if last_post and last_post.protocol_number and '/' in last_post.protocol_number:
        try:
            last_number = int(last_post.protocol_number.split('/')[-1])
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0
    return f"{year}/{last_number + 1:03}"


class SuperuserPostListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Post
    template_name = 'posts/superuser_post_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created')
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = get_user_model().objects.all()
        context['subjects'] = Subject.objects.all()
        context['courses'] = Cours.objects.all()
        context['specialty'] = Specialty.objects.all()
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.owner = self.request.user

        course_id = self.request.POST.get('cours') or self.request.POST.get('course')
        if course_id:
            try:
                course = Cours.objects.get(pk=course_id)
                post.cours = course
            except Cours.DoesNotExist:
                pass

        post.protocol_number = generate_unique_protocol_number()
        post.save()
        form.save_m2m()

        approver_ids = self.request.POST.getlist('approvers[]')
        for order, user_id in enumerate(approver_ids, start=1):
            try:
                user = get_user_model().objects.get(pk=user_id)
                ApprovalStep.objects.create(post=post, user=user, order=order)
            except get_user_model().DoesNotExist:
                continue

        subject_ids = self.request.POST.getlist('subjects[]')
        credits = self.request.POST.getlist('credits[]')
        for subject_id, credit in zip(subject_ids, credits):
            if subject_id and credit:
                try:
                    subject = Subject.objects.get(pk=subject_id)
                    PostSubject.objects.create(post=post, subject=subject, credits=float(credit))
                except (Subject.DoesNotExist, ValueError):
                    continue

        try:
            generate_post_pdf(post)
        except Exception as e:
            messages.warning(self.request, f"Ошибка при генерации PDF: {e}")

        return redirect('index-page')


class PostDetailView(LoginRequiredMixin, generic.DetailView):
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
        context['post_subjects'] = post.post_subjects.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        post = self.object
        action = request.POST.get("action")
        if action == "approval" and request.user.is_authenticated:
            return self.handle_approval(request, post)
        elif action == "comment" and request.user.is_authenticated:
            return self.handle_comment(request, post)
        return redirect("post-detail", pk=post.pk)

    def handle_approval(self, request, post):
        current_step = post.approval_steps.filter(is_approved=None).order_by("order").first()
        if current_step and current_step.user == request.user:
            is_approved_str = request.POST.get('approve')
            current_step.is_approved = True if is_approved_str == 'true' else False
            current_step.reviewed_at = timezone.now()
            current_step.save()
            if current_step.is_approved:
                if not post.approval_steps.filter(is_approved=None).exists():
                    post.status = "published"
            else:
                post.status = "draft"
            post.save()
        return redirect("post-detail", pk=post.pk)

    def handle_comment(self, request, post):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user.get_full_name() or request.user.email
            comment.save()
            messages.success(request, "Комментарий успешно добавлен.")
        else:
            messages.error(request, "Ошибка при добавлении комментария.")
        return redirect("post-detail", pk=post.pk)


class CreateSpecialtyView(LoginRequiredMixin, generic.CreateView):
    model = Specialty
    template_name = 'posts/specialty_create.html'
    form_class = SpecialtyForm
    success_url = reverse_lazy("create-special")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        specialties = Specialty.objects.all()
        if query:
            specialties = specialties.filter(name__icontains=query)
        paginator = Paginator(specialties, 20)
        page_number = self.request.GET.get('page')
        context["specialties"] = paginator.get_page(page_number)
        return context


class CreateSubjectView(LoginRequiredMixin, generic.CreateView):
    model = Subject
    template_name = 'posts/subject_create.html'
    form_class = SubjectForm
    success_url = reverse_lazy("create-subject")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        subjects = Subject.objects.all()
        if query:
            subjects = subjects.filter(name__icontains=query)
        paginator = Paginator(subjects, 20)
        page_number = self.request.GET.get('page')
        context["subjects"] = paginator.get_page(page_number)
        return context


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'posts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['my_posts'] = Post.objects.filter(owner=user)
        context['approval_posts'] = Post.objects.filter(
            approval_steps__user=user,
            approval_steps__is_approved=None
        ).distinct()
        context['approved_posts'] = Post.objects.filter(
            approval_steps__user=user,
            approval_steps__is_approved=True
        ).distinct()
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    template_name = 'posts/post_update.html'
    form_class = PostForm
    success_url = reverse_lazy("index-page")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.owner or self.request.user.is_superuser


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("index-page")

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.owner or self.request.user.is_superuser


class AboutView(generic.TemplateView):
    template_name = "posts/about.html"
    extra_context = {
        "title": "Страница о нас"
    }


@login_required
def get_curriculum_file(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    if specialty.curriculum:
        file_path = specialty.curriculum.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        else:
            raise Http404("Файл табылган жок")
    else:
        raise Http404("Учебный план жок")
