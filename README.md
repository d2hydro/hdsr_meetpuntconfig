# HDSR meetpuntconfig
Python scripts ter ondersteuning van het HDSR CAW FEWS:
 - het controleren van de consistentie van de configuratie met meetpunten
 - het aanvullen van attributen van locatiesets binnen de configuratie
 
## aanmaken caw python omgeving
Om conflicten met een bestaande python-installatie te voorkomen maken we een "python environment" aan met de naam 'caw'. Deze omgeving staat beschreven in environment.yml. Het aanmaken van de omgeving doe je met de volgende stappen:
1. open een windows command prompt (zie https://www.lifewire.com/how-to-open-command-prompt-2618089)
1. ga naar de locatie het bestandje environment.yml. Wanneer je van map moet veranderen gebruik je het commando 'cd' (zie https://www.lifewire.com/list-of-command-prompt-commands-4092302)
1. geef de volgende opdracht 

conda env create -f environment.yml

1. in de command prompt kun je de caw-omgeving nu openen met:

activate caw

## uitvoeren consistentie checks