# P2OC
Projet 2 du parcours "développeur concepteur Python" d'OC
<p align="center">
    <img src="logo.png" alt="logo" />
</p>
<h1 align="center">Scraping <em>BooksToScrape</em></h1>
<p align="center">
    <a href="https://www.python.org">
        <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" alt="python-badge">
    </a>
    <a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/">
        <img src="https://img.shields.io/badge/BeautifulSoup-4.12+-d71b60?style=flat" alt="Beautiful Soup">
    </a>
    <a href="https://github.com/psf/requests">
        <img src="https://img.shields.io/badge/Requests-2.31+-00838f?style=flat" alt="Requests">
    </a>
</p>

# A propos du projet

**OpenClassrooms Projet 2 : Utilisez les bases de Python pour l'analyse de marché**

_Testé sur Windows 10, Python 3.11.1._

### Objectifs

Scraping du site [books.toscrape.com](http://books.toscrape.com) avec **BeautifulSoup4** et **Requests**, 
exporter les données en fichier .csv  et télécharger les images de couvertures dans les dossiers *"Images/catégorie_correspondante"*.

Implementation du processus ETL: 
- **E**xtract pour **E**xtraire des données pertinentes et spécifiques d'une ressource en ligne
- **T**ransform pour **T**ransformer,  filtrer et nettoyer les données
- **L**oad pour **C**harger les données dans des fichiers consultable et récuperable

# Installation

### Cloner le dépôt

- `git clone https://github.com/Gaiden92/P2OC.git`

### Créer l'environnement virtuel

- `cd P2`
- `python -m venv env`
- Activer l'environnement `source env/bin/activate` (macOS and Linux) ou `env\Scripts\activate` (Windows)
    
### Installation des packages requis

- `pip install -r requirements.txt`

# Utilisation

Afin de scraper l'entièreté du site [books.toscrape.com](https://books.toscrape.com) en fichiers .csv, 
utiliser la commande `python main.py`.

## Utilisation des fichiers .csv

Si vous souhaitez exporter les fichiers .csv dans un tableur (Microsoft Excel, LibreOffice/OpenOffice Calc, Google Sheets...),
assurez-vous de sélectionner les options suivantes lorq  de l'ouverture du tableur:
- UTF-8 encoding 
- virgule `,` comme *separateur*
