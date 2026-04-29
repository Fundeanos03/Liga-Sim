from django import forms

from Liga_Corrupta_app.models import Equipo, Arbitro, Jugador


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

class ArbitroForm(forms.ModelForm):
    class Meta:
        model = Arbitro
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Mateu Maletines'
            }),
        }

class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['nombre', 'edad', 'posicion', 'media', 'equipo_actual']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),
            'posicion': forms.Select(attrs={'class': 'form-select'}),
            'media': forms.NumberInput(attrs={'class': 'form-control'}),
            'equipo_actual': forms.Select(attrs={'class': 'form-select'}), # Este es el selector
        }

