# HDSR meetpuntconfig
Python scripts ter ondersteuning van het HDSR CAW FEWS:
 - het controleren van de consistentie van de configuratie met meetpunten
 - het aanvullen van attributen van locatiesets binnen de configuratie
 
## Python omgeving
Deze scripts zijn afhankelijk van een python-omgeving met de volgende bibliotheken:
 - GeoPandas
 - Pandas: versie 1.1.0 of hoger
 - lxml

Wanneer je nog niet beschikt over zo'n omgeving, raden wij aan om een python-omgeving (python environment) aan te maken. We beschijven hieronder de stappen voor het aanmaken van de juiste omgeving met de naam 'caw'.

Wanneer je nog niet beschikt over een Anaconda of Miniconda installatie, dan kun je deze downloaden via:
 - https://www.anaconda.com/products/individual
 - https://docs.conda.io/en/latest/miniconda.html

Gedurende de installatie, vink de check-box 'Add Anaconda to PATH' en negeer de waarschuwing.

Het aanmaken van de omgeving doe je met de volgende stappen:
1. open een windows command prompt (zie https://www.lifewire.com/how-to-open-command-prompt-2618089)
1. ga naar de locatie het bestandje environment.yml. Wanneer je van map moet veranderen gebruik je het commando 'cd' (zie https://www.lifewire.com/list-of-command-prompt-commands-4092302)
1. geef de volgende opdracht 

*conda env create -f environment.yml*

1. in de command prompt kun je de caw-omgeving nu openen met:

*conda activate caw*

In het geval je deze omgeving weer wilt verwijderen van je machine kan dit via de command prompt:

*conda env remove -n caw*

In het geval je deze omgeving wilt updaten met een nieuwe yml-file:

*conda env update -f environment.yml*

## Voorbereiden configuratie
Het bestand *config\config_example.ini* staat een voorbeeld bestand met variabelen die worden ingelezen door de scripts. Pas dit bestand aan met de volgende stappen:
1. hernoem/kopieer *config\config_example.ini* naar *config\config.ini*
1. zet alle paden in de sectie *[paden]* goed

## Uitvoeren consistentie-checks
Draai het script in de map scripts vanuit de command prompt:

*python consistency_checks.py*