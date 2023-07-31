from fonctions import *


# création d'un dictionnaire contenant les noms des catagories et leurs liens
dictionnary_categories_name_and_url = getAllCategoriesTitles(URL_HOME)



# création du dossier "Catégorie" et des fichiers excels pour chaque catégorie
try:
    os.mkdir("Categories")

except FileExistsError:
    print("Le dossier existe déjà.")

create_excel_files_by_categories_names("Categories", dictionnary_categories_name_and_url)

# création du dictionnaire contenant les urls des livres par catégories
dictionnary_all_books_urls_by_category = get_links_articles_by_categories(dictionnary_categories_name_and_url)


# impression des données dans les fichiers excels et téléchargements des images
save_data_by_categorie(dictionnary_all_books_urls_by_category)
