from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('households/create/', views.household_create, name='household_create'),
    path('households/<int:pk>/', views.household_detail, name='household_detail'),

    path('households/<int:household_pk>/expenses/add/', views.expense_create, name='expense_create'),
    path('households/<int:pk>/members/add/', views.add_member, name='add_member'),
    path('households/<int:household_pk>/chores/add/', views.chore_create, name='chore_create'),
    path('chores/<int:pk>/toggle/', views.chore_toggle_status, name='chore_toggle_status'),
]
