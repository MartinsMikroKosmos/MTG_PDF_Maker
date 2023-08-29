import os
import time
import requests
from PIL import Image
from io import BytesIO
from fpdf import FPDF
from PyPDF2 import PdfMerger


# Funktion, um Kartenbilder aus der Datei zu extrahieren
def get_card_images_from_file(filename):
    card_data = []

    # Öffne die Datei und lese die Zeilen
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split(" ", 1)
            if len(parts) >= 2:
                quantity = parts[0]  # Anzahl der Karten
                card_info = parts[1]  # Karteninformationen

                # Extrahiere den Kartennamen und entferne Klammer-Informationen
                card_name = card_info.split("<", 1)[0].split("(", 1)[0].split("[", 1)[0].strip()

                card_data.append((quantity, card_name))

    # Erstelle PDFs für jede Karte und führe sie dann zusammen
    create_pdf(card_data, filename)


# Funktion, um PDFs für die Karten zu erstellen und sie dann zusammenzuführen
def create_pdf(cards, original_filename):
    pdf_merger = PdfMerger()  # Initialisiere den PDF-Merger

    for index, card_info in enumerate(cards):
        quantity, card_name = card_info

        url = 'https://api.scryfall.com/cards/named'
        params = {'fuzzy': card_name}

        response = requests.get(url, params=params)
        data = response.json()
        time.sleep(0.1)

        try:
            image_url = data['image_uris']['large']
            print(f"Bild URL: {image_url}")
        except KeyError:
            print(f"Fehler: Bild URL nicht gefunden für Karte '{card_name}'. Überspringe...")
            continue

        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(f"downloaded_image_{index}.jpg", "wb") as f:
                f.write(image_response.content)
            print(f"Bild {index} erfolgreich heruntergeladen und gespeichert.")
        else:
            print("Fehler beim Herunterladen des Bildes.")

        image = Image.open(f"downloaded_image_{index}.jpg")

        pdf = FPDF()  # Initialisiere PDF-Objekt
        pdf.add_page()  # Füge eine Seite zum PDF hinzu
        pdf.set_font('Arial', 'B', 24)  # Setze Schriftart und Größe

        # Berechne Bildgröße und Position
        max_width = pdf.w - 2 * pdf.l_margin
        max_height = pdf.h - 2 * pdf.b_margin - 16

        image_width, image_height = image.size
        aspect_ratio = image_width / image_height

        if aspect_ratio >= max_width / max_height:
            new_width = max_width
            new_height = new_width / aspect_ratio
        else:
            new_height = max_height
            new_width = new_height * aspect_ratio

        x = (pdf.w - new_width) / 2
        y = (pdf.h - new_height) / 2

        pdf.image(f"downloaded_image_{index}.jpg", x=x, y=y, w=new_width, h=new_height)
        pdf.cell(0, 10, txt=card_name, ln=1, align='C')  # Füge den Kartenamen hinzu

        pdf_output_path = f'{card_name}.pdf'
        pdf.output(pdf_output_path)  # Speichere das PDF
        print(f"PDF '{pdf_output_path}' erfolgreich erstellt.")

        pdf_merger.append(pdf_output_path)  # Füge das PDF zum PDF-Merger hinzu

    # Führe alle einzelnen PDFs zu einer PDF-Datei zusammen
    merged_output_path = f'{os.path.splitext(original_filename)[0]}.pdf'
    with open(merged_output_path, 'wb') as merged_file:
        pdf_merger.write(merged_file)
    print(f"Alle PDFs zu '{merged_output_path}' zusammengeführt.")

    # Lösche die einzelnen Bilder und PDFs
    for index, _ in enumerate(cards):
        os.remove(f"downloaded_image_{index}.jpg")
        os.remove(f'{cards[index][1]}.pdf')
    print("Einzelne Bilder und PDFs gelöscht.")


# Starte den Prozess mit der Eingabedatei 'Atraxa.txt'
get_card_images_from_file('/Users/install/Desktop/Privat/Decks/Nahiri Commander.txt')
