from functions import *
import time

# lancement du chronomètre
start_time = int(time.time())

# création d'un dictionnaire contenant les noms des catégories et leurs liens
dictionnary_categories_name_and_url = get_all_categories_titles(URL_HOME)

# création d'un dictionnaire contenant les liens de chaque livre par catégories
dictionnary_all_books_urls_by_category = get_links_books_by_categories(dictionnary_categories_name_and_url)

# sauvegarde des données
load_data(dictionnary_all_books_urls_by_category)

#arrêt du chronomètre
end_time = int(time.time())

# Affichage du temps écoulé
timer(start_time, end_time)