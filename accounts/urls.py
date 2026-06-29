from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import EmailPasswordResetForm

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('register/user/', views.register_user_view, name='register_user'),
    path('register/host/', views.register_host_view, name='register_host'),
    path('register/host/done/', views.register_host_done_view, name='register_host_done'),
    path('register/recycler/', views.register_recycler_view, name='register_recycler'),
    path('register/recycler/done/', views.register_recycler_done_view, name='register_recycler_done'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('my-center/', views.my_center_view, name='my_center'),
    path('household/dashboard/', views.household_dashboard_view, name='household_dashboard'),
    path('host/dashboard/', views.host_dashboard_view, name='host_dashboard'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            form_class=EmailPasswordResetForm,
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]