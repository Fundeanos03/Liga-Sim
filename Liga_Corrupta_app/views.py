from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def index(request):
    return render(request, "inicio.html")
def clasi(request):
    return render(request, "clasi.html")
def mi_club(request):
    return render(request, "mi_club.html")