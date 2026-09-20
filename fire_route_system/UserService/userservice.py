from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from DataAccess.decorators import admin_required
from .models import Role, User
from .forms import RoleForm, UserForm


# ── AUTHENTICATION VIEWS ─────────────────────────────────────────────────────

def login_view(request):
    """
    Officer / User Login view handling both username and email authentication.
    """
    if request.user.is_authenticated:
        # Redirect based on user authority
        if getattr(request.user, 'is_dispatcher', False) or getattr(request.user, 'is_admin', False):
            return redirect('dashboard')
        elif getattr(request.user, 'is_firefighter', False):
            return redirect('dashboard')
        return redirect('report_fire')

    error_message = None
    success_message = None
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', next_url)

        if not username or not password:
            error_message = "Please provide both username/email and password."
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='DataAccess.backends.RoleAuthBackend')
                if next_url and next_url != reverse('login') and next_url != reverse('logout'):
                    return redirect(next_url)
                if user.is_dispatcher or user.is_admin or user.is_firefighter:
                    return redirect('dashboard')
                return redirect('report_fire')
            else:
                error_message = "Invalid credentials or account is inactive."

    return render(request, 'auth/login.html', {
        'error_message': error_message,
        'success_message': success_message,
        'next': next_url,
        'username': request.POST.get('username', ''),
    })


def logout_view(request):
    """
    Officer logout view. Clears session and redirects to login.
    """
    logout(request)
    return redirect(reverse('login'))


@login_required
def profile_view(request):
    """
    Current user profile management view.
    """
    message = None
    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not email:
            error = "Email address is required."
        elif new_password and new_password != confirm_password:
            error = "New passwords do not match."
        else:
            request.user.email = email
            request.user.phone_number = phone_number
            if new_password:
                request.user.set_password(new_password)
            request.user.save()
            message = "Profile updated successfully."

    return render(request, 'user/profile.html', {
        'message': message,
        'error': error,
    })


# ── ROLE CRUD (Admin Only) ───────────────────────────────────────────────────

@admin_required
def role_list(request):
    roles = Role.objects.all().order_by('id')
    return render(request, 'role/list.html', {'roles': roles})


@admin_required
def role_create(request):
    form = RoleForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('role_list')

    return render(request, 'role/form.html', {'form': form})


@admin_required
def role_update(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)

    if form.is_valid():
        form.save()
        return redirect('role_list')

    return render(request, 'role/form.html', {'form': form})


@admin_required
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)

    if request.method == 'POST':
        role.delete()
        return redirect('role_list')

    return render(request, 'role/delete.html', {'role': role})


# ── USER CRUD (Admin Only) ───────────────────────────────────────────────────

@admin_required
def user_list(request):
    query = request.GET.get('q', '').strip()

    if query:
        from django.db.models import Q
        users = User.objects.select_related('role').filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )
    else:
        users = User.objects.select_related('role').all()

    from django.core.paginator import Paginator
    users = users.order_by('id')

    per_page_param = request.GET.get('per_page', '10').strip()
    try:
        per_page = int(per_page_param)
        if per_page not in [5, 10, 20, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10

    paginator = Paginator(users, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'user/list.html', {
        'page_obj': page_obj,
        'users': page_obj.object_list,
        'paginator': paginator,
        'per_page': per_page,
        'query': query
    })


@admin_required
def user_create(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('user_list')

    return render(request, 'user/form.html', {'form': form})


@admin_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=user)

    if form.is_valid():
        form.save()
        return redirect('user_list')

    return render(request, 'user/form.html', {'form': form})


@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user.delete()
        return redirect('user_list')

    return render(request, 'user/delete.html', {'user': user})
