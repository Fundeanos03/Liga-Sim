from django.urls import path

from . import views
urlpatterns = [
    path("", views.index, name="index"),

    path("clasificacion/", views.clasi, name="clasi"),

    path("mi-club/", views.mi_club, name="mi_club"),

]