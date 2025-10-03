# BEST PRACTICE RULE - NEVER VIOLATE
# =================================
#
# RULE: Altijd een script gebruiken, NOOIT python -c
#
# Dit betekent:
# - NOOIT `python -c "import json; ..."` gebruiken
# - NOOIT `python -c 'print("hello")'` gebruiken
# - NOOIT `py -c ` gebruiken
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
#
# Nieuwe regel handmatig ingevoerd: Gebruik voor alle analyses en alles wel zo veel mogelijk Python (via scripts).
# NOOIT samengestelde commando's proberen uit te voeren, ook niet met cd of powershell met | omdat die nooit automatisch 
# zijn goed te keuren. Ook nooit met ; op de command line.
# Dus werkt vooral met python script bestanden, zo dat uitvoer altijd door blijft lopen. 
# Op de command geen samengestelde commando's gebruiken.