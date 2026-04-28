from django.urls import path

from . import views
urlpatterns = [
    path("", views.index, name="index"),

    path("clasificacion/", views.clasi, name="clasi"),

    path("mi-club/", views.mi_club, name="mi_club"),

    path("administracion/", views.vista_administrador, name="administracion"),

    path('equipos/', views.ver_equipos, name='equipos'),
    path('equipos/editar/<int:pk>/', views.ver_equipos, name='editar_equipo'),

    path("eliminar_equipo/<int:id>", views.eliminar_equipos, name="eliminar_equipo"),

]