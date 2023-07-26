from fonctions import *

    

# lancement du programme
dictionnary_categorie_name_and_url = getAllCategoriesTitles(URL_HOME)

# création du dossier "Catégorie" et des fichiers excels pour chaque catégorie
create_categories_excel_files("Categories", dictionnary_categorie_name_and_url)

# création du dictionnaire contenant les catégories avec les urls pour chaque livre
dictionnary_categories_and_all_urls_articles = get_links_articles_by_categories(dictionnary_categorie_name_and_url)

# impression des données dans les fichiers excels et téléchargements des images
save_data_by_categorie(dictionnary_categories_and_all_urls_articles)