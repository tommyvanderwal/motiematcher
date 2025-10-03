# BEST PRACTICE RULE - NEVER VIOLATE
# =================================
#
# RULE: Altijd een script gebruiken, NOOIT python -c
#
# Dit betekent:
# - NOOIT `python -c "import json; ..."` gebruiken
# - NOOIT `python -c 'print("hello")'` gebruiken
# - NOOIT inline Python code uitvoeren
#
# Altijd:
# - Maak een .py bestand aan
# - Schrijf de complete code daarin
# - Run het met `python bestandsnaam.py`
#
# EXCEPTIE: Alleen voor heel korte, triviale operaties die geen analyse vereisen
# EN alleen als het geen data processing betreft.
#
# Deze regel is ingesteld op [2025-10-03] en MOET altijd worden nageleefd.
# Overtreding van deze regel is niet toegestaan.