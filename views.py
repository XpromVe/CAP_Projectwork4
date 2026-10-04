from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Article, Comment
from .forms import ArticleForm, CommentForm

def article_list(request):
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'blog/article_list.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all().order_by('created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'comments': comments,
        'comment_form': form
    })

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Статья создана!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'blog/article_form.html', {'form': form, 'title': 'Новая статья'})

@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user:
        messages.error(request, 'Вы не можете редактировать чужую статью!')
        return redirect('article_detail', pk=pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья обновлена!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'blog/article_form.html', {'form': form, 'title': 'Редактировать статью'})

@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author == request.user:
        article.delete()
        messages.warning(request, 'Статья удалена.')
    else:
        messages.error(request, 'Отказано в доступе.')
    return redirect('article_list')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('article_list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})