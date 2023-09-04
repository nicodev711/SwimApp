from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.decorators.cache import cache_page

from . import views
from .views import *

app_name = 'Swimapp'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('explore', views.explore, name='explore'),
    path('explore/<slug:spot>/', views.spot_detail, name='spot_detail'),
    path('edit/<int:spot_id>/', views.edit_swimming_spot, name='edit_swimming_spot'),
    path('spot/<int:spot_id>/delete/', views.delete_spot, name='delete_spot'),
    path('search/', views.search_results, name='search_results'),
    path('api', SwimmingSpotListView.as_view(), name='get_spots'),
    path('community/', views.community, name='community'),
    path('subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
    path('about/', views.about, name='about'),

    path('plans/', views.list_plans, name='list_plans'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),

    path('login/', auth_views.LoginView.as_view(next_page='Swimapp:homepage'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='Swimapp:homepage'), name='logout'),

    path('password-change/',
         auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('swimapp:password_change_done')),
         name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(success_url=reverse_lazy('swimapp:password_reset_done')),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),

    path('accounts/profile/', redirect_to_home, name='redirect_to_home'),
]
