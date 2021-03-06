from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TodoForm
from .models import Todo


def signup_user(request):
    if request.method == 'GET':
        return render(request, "todo/signup.html", {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request, "todo/signup.html",
                              {'form': UserCreationForm(), 'error': 'Username has already been used. Please try with '
                                                                    'a new username.'})
        else:
            # Password are not matched!
            print("Password are not matched!")
            return render(request, "todo/signup.html", {'form': UserCreationForm(), 'error': 'Password did not match'})


def login_user(request):
    if request.method == 'GET':
        return render(request, "todo/login.html", {'form': AuthenticationForm()})
    else:
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is None:
            return render(request, "todo/login.html", {'form': AuthenticationForm(), 'error': 'Username and password '
                                                                                              'did not match'})
        else:
            login(request, user)
            return redirect('current_todos')


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def current_todos(request):
    todos = Todo.objects.filter(user=request.user, completedDate__isnull=True)
    return render(request, 'todo/current_todos.html', {'todos': todos})


def home(request):
    return render(request, 'todo/home.html')


@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo/create_todo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/create_todo.html', {'form': TodoForm(), 'error': 'Invalid input data, Try '
                                                                                          'again!'})


@login_required
def get_todo(request, todo_pk):
    try:
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    except Todo.DoesNotExist:
        raise Http404("Todo does not exist")

    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/view_todo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/view_todo.html', {'todo': todo, 'form': form, 'error': 'Invalid input data!'})


@login_required
def complete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.completedDate = timezone.now()
        todo.save()
        return redirect('current_todos')


@login_required
def delete_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('current_todos')


@login_required
def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, completedDate__isnull=False).order_by('-completedDate')
    return render(request, 'todo/completed_todos.html', {'todos': todos})


def page_not_found(request, exception):
    return render(request, 'todo/error.html', {'message': "Seems,The page you are trying to reach doesn't exist."})
