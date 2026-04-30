from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Message

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, 'Вы успешно вошли в систему.')
        return redirect('index')

    return render(request, 'chat/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
        return redirect('index')

    return render(request, 'chat/register.html', {'form': form})


@login_required(login_url='login')
def index(request):
    users = User.objects.exclude(pk=request.user.pk)
    messages_list = Message.objects.filter(
        models.Q(sender=request.user) | models.Q(recipient=request.user)
    ).select_related('sender', 'recipient')
    return render(request, 'chat/index.html', {
        'users': users,
        'messages': messages_list,
    })


@login_required(login_url='login')
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        text = request.POST.get('text', '').strip()
        recipient = get_object_or_404(User, pk=recipient_id)

        if recipient == request.user:
            return JsonResponse({'error': 'Нельзя отправить сообщение самому себе.'})
        elif not text:
            return JsonResponse({'error': 'Введите текст сообщения.'})
        else:
            Message.objects.create(sender=request.user, recipient=recipient, text=text)
            return JsonResponse({'success': 'Сообщение отправлено.'})

    return JsonResponse({'error': 'Неверный метод.'})


@login_required(login_url='login')
def get_messages(request):
    messages_list = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).select_related('sender', 'recipient').order_by('created_at')
    data = [
        {
            'sender': msg.sender.username,
            'recipient': msg.recipient.username,
            'text': msg.text,
            'created_at': msg.created_at.isoformat(),
        } for msg in messages_list
    ]
    return JsonResponse({'messages': data})
