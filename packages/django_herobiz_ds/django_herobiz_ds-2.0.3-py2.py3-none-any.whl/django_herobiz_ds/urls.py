from django.urls import path
from . import views

app_name = 'herobizds'

urlpatterns = [
    # robots.txt는 반드시 가장 먼저
    path('robots.txt', views.robots),
    path('', views.home, name='home'),
    path('<int:id>/', views.details, name='details'),
    path('terms_of_use/', views.terms, name='terms'),
    path('privacy_policy/', views.privacy, name='privacy'),

    path('blog/', views.blog),
    path('blog-details/', views.blog_details),
]
