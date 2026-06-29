from django.urls import path

from . import views

urlpatterns = [
    path('', views.AdminCompanyListView.as_view(), name='recycler_admin_list'),
    path('<int:pk>/', views.AdminCompanyReviewView.as_view(), name='recycler_admin_review'),
    path('<int:pk>/approve/', views.AdminApproveCompanyView.as_view(), name='recycler_admin_approve'),
    path('<int:pk>/reject/', views.AdminRejectCompanyView.as_view(), name='recycler_admin_reject'),
]
