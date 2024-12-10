from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime


class User(AbstractUser):
    pass

class MelanomaDiagnosis(models.Model):
    # ID único para el diagnóstico
    diagnosis_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Relación con el usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnoses')
    
    # Campo para almacenar la foto (se puede agregar validación de formatos en el archivo)
    photo = models.ImageField(upload_to='melanoma_photos/')
    
    # Diagnóstico de la imagen (Melanoma o no)
    diagnosis_result = models.CharField(max_length=20, choices=[('Melanoma', 'Melanoma'), ('No Melanoma', 'No Melanoma')])
    
    # Timestamp de cuando se realizó el diagnóstico
    timestamp = models.DateTimeField(default=datetime.now)
    
    # Opción de agregar una foto relacionada a un diagnóstico anterior (actualización)
    actualizacion = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_diagnosis')
    
    # Método para mostrar información de manera legible
    def __str__(self):
        return f'Diagnóstico {self.diagnosis_id} - Usuario: {self.user.username} - {self.diagnosis_result}'