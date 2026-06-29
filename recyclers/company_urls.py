from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='recycling_company_dashboard'),
    path('directory/', views.AggregatorDirectoryView.as_view(), name='recycler_directory'),
    path('reports/export/', views.ExportReportsCSVView.as_view(), name='recycler_export_csv'),
    path('pending/', views.PendingView.as_view(), name='recycler_pending'),
]
