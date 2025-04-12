from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from posts.models import Post
from posts.forms import CommentForm, PostForm
from django.db.models import Q
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404





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
    context_object_name = 'posts'
    template_name = "posts/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Показываем только PDF-документы, к которым у пользователя есть доступ
        user = self.request.user
        if user.is_authenticated:
            context['pdf_posts'] = Post.objects.filter(
                Q(owner=user) | Q(allowed_users=user)
            ).distinct()
        else:
            context['pdf_posts'] = Post.objects.none()

        return context

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_user_turn = False
    next_approver = None
    is_fully_approved = False

    # Проверка на одобрение
    approved_users = post.approvals.all().values_list('user', flat=True)
    if len(approved_users) == post.allowed_users.count():
        is_fully_approved = True
    else:
        # Находим пользователя, который должен подтвердить
        next_approver = post.allowed_users.exclude(id__in=approved_users).first()

    # Проверка, если текущий пользователь может подтвердить
    if request.user == next_approver:
        is_user_turn = True

    if request.method == 'POST':
        # Если пост подтверждается
        if 'approve' in request.POST and is_user_turn:
            PostApproval.objects.create(post=post, user=request.user)
            return redirect('post-detail', pk=pk)

        # Добавление комментария
        elif 'comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.save()
                return redirect('post-detail', pk=pk)

    # Комментарии и формы
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'is_user_turn': is_user_turn,
        'is_fully_approved': is_fully_approved,
        'next_approver': next_approver,
    }
    return render(request, 'post_detail.html', context)



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
    fields = ['title', 'content', 'pdf_file', 'allowed_users', 'status']
    success_url = reverse_lazy("index-page")

class PostDeleteView(generic.DeleteView):
    model = Post
    success_url= reverse_lazy("index-page")

 
class AboutView(generic.TemplateView):
    template_name="posts/about.html"
    extra_context = {
        "title": "Страница о нас"
    }
    


# @login_required
# def upload_pdf(request):
#     if request.method == 'POST':
#         form = PDFPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             pdf_post = form.save(commit=False)
#             pdf_post.owner = request.user
#             pdf_post.save()
#             form.save_m2m()  # Сохраняем ManyToMany
#             return redirect('index-page')  # Перенаправление на список
#     else:
#         form = PDFPostForm()
#     return render(request, 'posts/upload_pdf.html', {'form': form})

# @login_required
# def view_pdf(request, post_id):
#     post = get_object_or_404(PDFPost, id=post_id)

#     if request.user == post.owner or request.user in post.allowed_users.all():
#         return FileResponse(post.pdf_file.open(), content_type='application/pdf')
#     else:
#         return HttpResponseForbidden("У вас нет доступа к этому PDF.")
    

# def my_pdfs_view(request):
#     # Ваша логика для обработки запроса
#     return render(request, 'posts/my_pdfs.html')  # или другая логика