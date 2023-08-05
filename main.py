from fonctions import *
import time

# lancement du chronomètre
start_time = int(time.time())

# création d'un dictionnaire contenant les noms des catagories et leurs liens
dictionnary_categories_name_and_url = getAllCategoriesTitles(URL_HOME)

# création du dictionnaire contenant les urls des livres par catégories
dictionnary_all_books_urls_by_category = get_links_articles_by_categories(dictionnary_categories_name_and_url)

#Sauvegarde des données
save_data_by_categorie(dictionnary_all_books_urls_by_category)

#arrêt du chronomètre
end_time = int(time.time())

# Affichage du temps écoulé
timer(start_time, end_time)