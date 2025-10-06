# -*- coding: utf-8 -*-
import random
import os
from time import sleep
from datetime import datetime
from enum import Enum
import re
import json
from cryptography.fernet import Fernet

# Zmienna określająca, czy włączyć tryb debugowania
# Tryb debugowania pozwala na wyświetlanie dodatkowych informacji.
__debug = False

# Ścieżka do pliku zapisu gry
save_file = "./data/save1.txt"

# Sprawdzanie, czy istnieje zapisany plik gry
save_file_exist = os.path.exists(save_file)
if __debug:
    print("\033[93mSave istnieje\033[39m" if save_file_exist else "\033[93mSave nie istnieje\033[39m")
