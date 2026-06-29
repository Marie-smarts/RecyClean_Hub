from django.urls import path

from . import views

urlpatterns = [
    path('register/step1/', views.RegisterStep1View.as_view(), name='recycler_register_step1'),
    path('register/step2/', views.RegisterStep2View.as_view(), name='recycler_register_step2'),
    path('register/step3/', views.RegisterStep3View.as_view(), name='recycler_register_step3'),
]
