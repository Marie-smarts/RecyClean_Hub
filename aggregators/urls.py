from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register_view, name='aggregator_register'),
    path('register/done/', views.register_done_view, name='aggregator_register_done'),
    path('pending/', views.pending_view, name='aggregator_pending'),
    path('dashboard/', views.dashboard_view, name='aggregator_dashboard'),
    path('pickups/', views.pickups_view, name='aggregator_pickups'),
    path('pickups/accept/<int:pk>/', views.accept_pickup_view, name='aggregator_accept_pickup'),
    path('pickups/<int:pk>/', views.pickup_detail_view, name='aggregator_pickup_detail'),
    path(
        'pickups/<int:assignment_pk>/log-collection/',
        views.log_collection_view,
        name='aggregator_log_collection',
    ),
    path('collections/', views.collections_list_view, name='aggregator_collections'),
    path('collections/<int:pk>/', views.collection_detail_view, name='aggregator_collection_detail'),
    path('admin/verify/', views.admin_verify_list_view, name='aggregator_admin_verify'),
    path(
        'admin/verify/<int:pk>/<str:action>/',
        views.admin_verify_action_view,
        name='aggregator_admin_verify_action',
    ),
]
