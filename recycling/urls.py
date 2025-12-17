from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('submit/', views.submit_recyclable_view, name='submit_recyclable'),
    path('my-items/', views.my_recyclables_view, name='my_recyclables'),
    path('edit/<int:pk>/', views.edit_recyclable_view, name='edit_recyclable'),
    path('delete/<int:pk>/', views.delete_recyclable_view, name='delete_recyclable'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('centers/', views.drop_off_centers_view, name='drop_off_centers'),
    path('request-pickup/', views.request_pickup_view, name='request_pickup'),
]