from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('accounts/register/', core_views.register_view, name='register'),
    path('accounts/login/', core_views.email_login_view, name='login'),
    path('accounts/logout/', core_views.logout_view, name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Handle /accounts/profile/ by sending to dashboard
    path('accounts/profile/', core_views.profile_redirect, name='profile'),

    # Core app (dashboard, households, expenses, chores)
    path('', include('core.urls')),
]