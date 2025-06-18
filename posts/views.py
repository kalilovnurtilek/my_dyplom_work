import json
from django.shortcuts import redirect 
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Post, ApprovalStep, Specialty, Subject, PostSubject, Curriculum, SpecialtyTranscript
from .forms import PostForm, CommentForm, SpecialtyForm, SubjectForm, CurriculumUploadForm
from .services import calculate_credit_transfer, parse_transcript_pdf
from .utils.pdf_generator import generate_post_pdf
from django.views import generic
from django.contrib.auth import get_user_model

from django.contrib import messages









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
    success_url = reverse_lazy('index-page')

    def get_form_kwargs(self):
        """Передаем request в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        """Добавляем в контекст пользователей и предметы"""
        context = super().get_context_data(**kwargs)
        context['users'] = get_user_model().objects.all()
        context['subjects'] = Subject.objects.all()
        context['specialties_with_transcripts'] = Specialty.objects.filter(
            transcript__isnull=False
        ).distinct().values_list('id', flat=True)
        return context

    def form_valid(self, form):
        """Обработка валидной формы"""
        post = form.save(commit=False)
        post.owner = self.request.user
        
        # Автоматическая загрузка транскрипта
        if not post.pdf_file and form.cleaned_data.get('specialty'):
            transcript = SpecialtyTranscript.objects.filter(
                specialty=form.cleaned_data['specialty']
            ).first()
            if transcript:
                post.pdf_file = transcript.transcript_file
        
        post.save()
        form.save_m2m()

        # Создание этапов согласования
        self.create_approval_steps(post)
        
        # Привязка предметов
        self.attach_subjects(post)
        
        # Генерация PDF
        generate_post_pdf(post)
        
        messages.success(self.request, 'Заявление успешно создано!')
        return redirect(self.get_success_url())

    def create_approval_steps(self, post):
        """Создание этапов согласования"""
        approver_ids = self.request.POST.getlist('approvers[]')
        for i, uid in enumerate(approver_ids):
            try:
                user = get_user_model().objects.get(pk=uid)
                ApprovalStep.objects.create(
                    post=post, 
                    user=user, 
                    order=i+1
                )
            except (get_user_model().DoesNotExist, ValueError):
                continue

    def attach_subjects(self, post):
        """Привязка предметов с кредитами"""
        subject_ids = self.request.POST.getlist('subjects[]')
        credits = self.request.POST.getlist('credits[]')

        for sid, credit in zip(subject_ids, credits):
            if sid and credit:
                try:
                    subject = Subject.objects.get(pk=sid)
                    PostSubject.objects.create(
                        post=post, 
                        subject=subject, 
                        credits=float(credit)
                    )
                except (Subject.DoesNotExist, ValueError):
                    continue

    def get_success_url(self):
        """URL для перенаправления после успешного создания"""
        return self.success_url
class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Данные о кредитах
        if post.credit_diff_data:
            context['credit_diff'] = post.credit_diff_data
            context['missing_credits'] = post.missing_credits
        
        # Комментарии и форма
        context['comments'] = post.comment_set.all()
        context['form'] = CommentForm()
        
        # Логика согласования
        user = self.request.user
        if user.is_authenticated:
            current_step = post.approval_steps.filter(
                is_approved=None
            ).order_by('order').first()
            context['can_approve'] = current_step and current_step.user == user
            context['approval_step'] = current_step
        
        context['approval_steps'] = post.approval_steps.select_related('user')
        context['post_subjects'] = post.post_subjects.all()
        
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        action = request.POST.get("action")

        if action == "approval":
            self.handle_approval(post, request)
        elif action == "comment":
            self.handle_comment(post, request)
        
        return redirect("post-detail", pk=post.pk)

    def handle_approval(self, post, request):
        current_step = post.approval_steps.filter(
            is_approved=None
        ).order_by("order").first()
        
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

    def handle_comment(self, post, request):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user.get_full_name() or request.user.email
            comment.save()

class CreateSpecialtyView(generic.CreateView):
    model = Specialty
    template_name = 'posts/specialty_create.html'
    fields=["name","code","short_name","pdf_file"]
    success_url = reverse_lazy("create-special")
    form = SpecialtyForm ,   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        specialties = Specialty.objects.all()
        if query:
            specialties = specialties.filter(name__icontains=query)
        context["specialties"] = specialties
        return context
    

class CreateSubjectView(generic.CreateView):
    model = Subject
    template_name = 'posts/subject_create.html'
    form_class = SubjectForm  # Указываем форму, если хотим использовать кастомную форму
    success_url = reverse_lazy("create-subject")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        subjects = Subject.objects.all()
        if query:
            subjects = subjects.filter(name__icontains=query)
        context["subjects"] = subjects
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

@csrf_exempt
def calculate_credits_api(request):
    if request.method == 'POST':
        try:
            # Получение файла и учебного плана
            pdf_file = request.FILES.get('pdf_file')
            curriculum_id = request.POST.get('curriculum_id')
            
            if not pdf_file or not curriculum_id:
                return JsonResponse({'error': 'Missing required data'}, status=400)
            
            curriculum = Curriculum.objects.get(id=curriculum_id)
            student_subjects = parse_transcript_pdf(pdf_file)
            
            # Расчет разницы кредитов
            result = calculate_credit_transfer(
                student_subjects, 
                curriculum.subjects.all()
            )
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_curriculums(request):
    """API для получения учебных планов по специальности"""
    specialty_id = request.GET.get('specialty_id')
    if not specialty_id:
        return JsonResponse({'error': 'Specialty ID required'}, status=400)
    
    curriculums = Curriculum.objects.filter(
        specialty_id=specialty_id,
        is_active=True
    ).order_by('-year').values('id', 'year')
    
    return JsonResponse(list(curriculums), safe=False)


class CurriculumCreateView(UserPassesTestMixin, generic.CreateView):
    model = Curriculum
    form_class = CurriculumUploadForm
    template_name = 'posts/curriculum_create.html'
    success_url = reverse_lazy('curriculum-create')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curriculums'] = Curriculum.objects.all().order_by('-year')
        return context

    def form_valid(self, form):
        curriculum = form.save(commit=False)
        
        # Парсинг PDF учебного плана при его наличии
        if curriculum.pdf_file:
            self.parse_curriculum_pdf(curriculum)
        
        curriculum.save()
        return redirect(self.success_url)

    def parse_curriculum_pdf(self, curriculum):
        """Парсинг PDF учебного плана и создание предметов"""
        # Здесь должна быть реализация парсинга PDF
        # Временная заглушка:
        print(f"Need to implement PDF parsing for curriculum {curriculum.id}")

def get_specialty_transcript(request):
    specialty_id = request.GET.get('specialty_id')
    if not specialty_id:
        return JsonResponse({'error': 'No specialty_id provided'}, status=400)

    try:
        transcript = SpecialtyTranscript.objects.get(specialty_id=specialty_id)
        return JsonResponse({'transcript_url': transcript.transcript_file.url})
    except SpecialtyTranscript.DoesNotExist:
        return JsonResponse({'error': 'Transcript not found'}, status=404)