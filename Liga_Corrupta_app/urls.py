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

    path('arbitros/', views.gestionar_arbitros, name='arbitros'),
    path('arbitros/editar/<int:pk>/', views.gestionar_arbitros, name='editar_arbitro'),
    path('arbitros/borrar/<int:borrar_id>/', views.gestionar_arbitros, name='borrar_arbitro'),

    # Rutas actuales y nuevas
    path('jugadores/', views.gestionar_jugadores, name='jugadores'),
    path('jugadores/nuevo/', views.nuevo_jugador, name='nuevo_jugador'),  # NUEVA
    path('jugadores/cargar/', views.cargar_jugadores_csv, name='cargar_jugadores_csv'),
    path('jugadores/editar/<int:pk>/', views.editar_jugador, name='editar_jugador'),
    path('jugadores/eliminar/<int:pk>/', views.eliminar_jugador, name='eliminar_jugador'),
    path('jugadores/borrar-todo/', views.borrar_todos_jugadores, name='borrar_todos_jugadores'),  # NUEVA

]