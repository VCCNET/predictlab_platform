from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_main, name='post_main'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('pswdmod/', views.pswdmod, name='pswdmod'),
]
