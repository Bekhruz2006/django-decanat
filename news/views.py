from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from main.models import News
from main.forms import NewsForm


def is_dean(user):
    return user.is_authenticated and user.role == 'dean'


def news_list(request):
    """Список всех новостей"""
    news = News.objects.all().order_by('-created_at')
    return render(request, 'news/news_list.html', {'news': news})


def news_detail(request, news_id):
    """Детальный просмотр новости"""
    news_item = get_object_or_404(News, id=news_id)
    return render(request, 'news/news_detail.html', {'news_item': news_item})


@login_required
@user_passes_test(is_dean)
def news_create(request):
    """Создание новости (только декан)"""
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.created_by = request.user
            news.save()
            messages.success(request, 'Новость опубликована!')
            return redirect('news_list')
    else:
        form = NewsForm()
    
    return render(request, 'news/news_form.html', {'form': form})


@login_required
@user_passes_test(is_dean)
def news_edit(request, news_id):
    """Редактирование новости"""
    news_item = get_object_or_404(News, id=news_id)
    
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новость обновлена!')
            return redirect('news_list')
    else:
        form = NewsForm(instance=news_item)
    
    return render(request, 'news/news_form.html', {
        'form': form,
        'news_item': news_item
    })


@login_required
@user_passes_test(is_dean)
def news_delete(request, news_id):
    """Удаление новости"""
    news_item = get_object_or_404(News, id=news_id)
    news_item.delete()
    messages.success(request, 'Новость удалена!')
    return redirect('news_list')