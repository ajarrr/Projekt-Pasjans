# -*- coding: utf-8 -*-
from config import *
import re
import json
from datetime import datetime
from cryptography.fernet import Fernet
from enum import Enum


# Enum przechowujący kody błędów i odpowiadające im komunikaty
class ErrorCode(Enum):
    INVALID_MOVE = "\033[91mRuch niedozwolony. Sprawdź zasady i spróbuj ponownie.\033[39m"
    EMPTY_COLUMN = "\033[91mNie można pobrać karty z pustej kolumny.\033[39m"
    INVALID_INPUT = "\033[91mNieprawidłowy wybór. Wprowadź poprawne dane.\033[39m"
    EMPTY_WASTE = "\033[91mStos rezerwowy jest pusty. Nie można dobrać więcej kart.\033[39m"
    INVALID_DIFFICULTY = "\033[91mNieprawidłowy poziom trudności.\033[39m"


# Funkcja ładująca klucz szyfrowania
def load_key():
    with open("./data/fernet.key", "rb") as key_file:
        return key_file.read()


# Funkcja szyfrująca plik
def encrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    with open(file_path, "wb") as f:
        f.write(encrypted)


# Funkcja deszyfrująca plik
def decrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    decrypted = fernet.decrypt(encrypted_data)
    return decrypted.decode("utf-8")


# Funkcja obsługująca błędy i wyświetlająca odpowiednie komunikaty
def handle_error(error_code):
    print(error_code.value if isinstance(error_code, ErrorCode) else "\033[93mNieznany błąd.\033[39m")


# Funkcja zwracająca wartość liczbową dla symboli kart
def card_value(value):
    values = {'A': 1, 'J': 11, 'Q': 12, 'K': 13}
    try:
        return values.get(value, int(value))
    except ValueError:
        return None


# Funkcja usuwająca kody ANSI z tekstu
def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


# Funkcja zapisująca wynik gry do pliku scores.txt
def save_score(turns):
    try:
        with open("./data/scores.txt", "a", encoding="utf-8") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {turns}\n")
    except IOError:
        print("\033[91mNie udało się zapisać wyniku do pliku.\033[39m")


# Funkcja wczytująca wyniki z pliku scores.txt
def read_scores():
    scores = []
    try:
        with open("./data/scores.txt", "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(" | ")
                if len(parts) == 2:
                    date, moves = parts
                    scores.append((date, int(moves)))
        scores.sort(key=lambda x: x[1])
    except FileNotFoundError:
        print("\033[93mPlik z wynikami nie istnieje. Zostanie utworzony po pierwszej grze.\033[39m")
    except IOError:
        print("\033[91mNie udało się odczytać pliku z wynikami.\033[39m")
    return scores


# Funkcja wyświetlająca najlepsze wyniki w formie tabeli
def display_scores():
    scores = read_scores()
    if not scores:
        print("\033[93mBrak zapisanych wyników.\033[39m")
    else:
        scores.sort(key=lambda x: x[1])

        print("\n\033[92m=== Ranking najlepszych wyników ===\033[39m")
        print(f"{'Nr':<4} | {'Data':<20} | {'Liczba Ruchów':<15}")
        print("-" * 50)

        for i, (date, moves) in enumerate(scores[:10], start=1):
            print(f"{i:<4} | {date:<20} | {moves:<15}")
