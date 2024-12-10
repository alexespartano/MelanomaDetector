from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.urls import reverse
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image

from .models import User


model = tf.keras.models.load_model('./SkinCancerDetection/modelo_entrenado.h5')

def index(request):
    return render(request, "MelaSCAN/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "MelaSCAN/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "MelaSCAN/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "MelaSCAN/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "MelaSCAN/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "MelaSCAN/register.html")

def predict_image(request):
    # Aquí recibes la imagen (suponiendo que la imagen llega como un archivo en un formulario)
    if request.method == 'POST' and request.FILES['image']:
        img_file = request.FILES['image']
         # Convertir el archivo de imagen a un objeto que PIL pueda procesar
        img = Image.open(img_file)  # Abrir la imagen usando PIL
        img = img.convert('RGB')  # Asegurarse de que esté en formato RGB
        img = img.resize((224, 224))  # Redimensionar la imagen al tamaño que espera el modelo

        #img = image.load_img(img_file, target_size=(224, 224))  # Cambia el tamaño según tu modelo
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalización si es necesario
        # Hacer predicción
        prediction = model.predict(img_array)
        print(prediction)
        # Si la predicción es para una clasificación, puedes obtener la clase con np.argmax
        predicted_class = np.argmax(prediction, axis=1)

        print(predicted_class)
        # Mapear 1 y 0 a maligno y benigno
        result = "malignant" if prediction >= 0.312 else "benign"

        #Mostrar la predicción
        #print(prediccion)  # El resultado será un valor entre 0 y 1, donde 1 es "malignant" y 0 es "benign"

        # Pasar el resultado a la plantilla
        return render(request, 'MelaSCAN/index.html', {'prediction': result})

    return render(request, 'MelaSCAN/index.html')  # Si no es POST, solo renderiza el formulario