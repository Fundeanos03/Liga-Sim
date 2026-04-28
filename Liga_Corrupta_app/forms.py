from django import forms

from Liga_Corrupta_app.models import Equipo


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'presidente', 'escudo', 'estadio', 'entrenador']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Sobornos United'}),
            'presidente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del testaferro'}),
            'escudo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL de la imagen o icono'}),
            'estadio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Donde ocurre la magia'}),
            'entrenador': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'El mago'}),
        }