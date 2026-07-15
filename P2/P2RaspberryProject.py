"""
Program do klasyfikacji cyfr MNIST przy użyciu modelu EfficientNet-B0 na Raspberry Pi z kamerą PiCamera i Sense HAT.
"""

import cv2 as cv
from picamera2 import Picamera2
from sense_hat import SenseHat

import torch
from torch import nn
from torchvision.models import efficientnet_b0
from torchvision import transforms as t


def load_model(path, device):    
    model = efficientnet_b0(weights=None) # Stworzenie modelu EfficientNet-B0 bez wstępnie wytrenowanych wag
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, 10) # Zmiana liczby wyjść klasyfikatora na 10 (dla 10 klas MNIST)
    model.features[0][0] = nn.Conv2d(1, 32, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), bias=False) # Zmiana liczby kanałów wejściowych pierwszej warstwy konwolucyjnej na 1 (dla obrazów MNIST)

    model.load_state_dict(torch.load(path, map_location=device)) # Wczytanie wag modelu z pliku
    model.to(device) # Przeniesienie modelu na wybrane urządzenie (CPU lub GPU)
    model.eval() # Ustawienie modelu w tryb ewaluacji
    return model

device = torch.device("cpu")
model = load_model("mnist_efficientnet_b0.pth", device)

transforms = t.Compose([
    t.ToTensor(), # Konwersja obrazu do tensora z zakresem wartości [0, 1]
    t.Normalize((0.1307,), (0.3081,)) # Standaryzacja obrazu
])

def transform_image(image):
    # Konwersja obrazu do skali szarości
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Wycięcie centralnego kwadratu obrazu
    h, w = image.shape[:2]
    min_dim = min(h, w)
    start_x = (w - min_dim) // 2
    start_y = (h - min_dim) // 2
    image = image[start_y:start_y + min_dim, start_x:start_x + min_dim]
    # Zmiana rozmiaru obrazu na 28x28 pikseli
    image = cv.resize(image, (28, 28))
    # Konwersja obrazu do tensora i normalizacja
    image = transforms(image)
    return image
    
def inference(model, image, device):
    model.eval()  # Ustawienie modelu w tryb ewaluacji
    with torch.no_grad():  # Wyłączenie obliczania gradientów
        image = image.to(device)  # Przeniesienie obrazu na odpowiednie urządzenie (CPU lub GPU)
        image = image.unsqueeze(0)  # Dodanie wymiaru batcha (1, C, H, W) dla pojedynczego obrazu
        probs = model(image)  # Wnioskowanie na modelu -> zwracanie prawdopodobieństw dla każdej klasy
        pred = probs.argmax(dim=1) # Predykcja etykiet na podstawie najwyższego prawdopodobieństwa dla każdej próbki (ARGMAX)
        max_prob = probs[:,pred] # Prawdopodobieństwo dla wybranej klasy
    return int(pred.item()), float(max_prob.item())

# Inicjalizuj kamerę
picam = Picamera2()
picam.configure(picam.create_still_configuration(main={"size": (3280, 2464)}))
picam.start()

# Inicjalizuj Sense HAT
hat = SenseHat()

try:
    while not len(hat.stick.get_events()):
        # Pobierz obraz z PiCamera
        frame = picam.capture_array(name="main")
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        # Przetwórz do TENSORa
        tensor = transform_image(frame)
        # Wnioskowanie
        result, result_prob = inference(model, tensor, device)
        print(f"Predicted digit: {result}, {result_prob*100.0:.1f}%")
        # Wyswietlenie na Sense HAT
        hat.show_letter(str(result))
        
finally:
    # Zamknij kamerę
    picam.stop()
    # Wyczyść LED
    hat.clear()
