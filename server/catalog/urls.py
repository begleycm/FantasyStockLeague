from django.urls import path
from . import views

urlpatterns = [
    path("404/", views.response_not_found_view, name='404_page')
]
