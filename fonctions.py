from bs4 import BeautifulSoup
import requests, os
import csv


URL_HOME = "https://books.toscrape.com/"

def getAllCategoriesTitles(url:str)-> dict:
    """
    Cette fonction permet de récuperer les titres et les liens de chaque catégories de la page d'accueil.
    Elle prend en paramètre l'url de la page d'acceuil.
    Elle retourne un dictionnaire avec les catégories comme clefs et les urls des catégories comme valeurs

    """ 

    CONTENT_BODY_HOME = requests.get(url).text
    reponse = requests.get(url)

    soup = BeautifulSoup(CONTENT_BODY_HOME, "html.parser")

    # récupération du menu "catégories"
    menu_nav_categories = soup.find("ul", class_="nav nav-list")
    ul_category = menu_nav_categories.li.ul

    # récuperation des titres
    tab_titles = []
    category_title = ul_category.li.a
    for category_title in ul_category:
        category_title_strip = category_title.getText('',True)
        if not category_title_strip == "":
            tab_titles.append(category_title_strip)

    #récupération des liens
    tab_links = []
    all_tag_a = ul_category.find_all('a')
    for tag_a in all_tag_a:
        link = url+tag_a['href']
        tab_links.append(link)

    # création du dictionnaire
    dictionnary = dict(zip(tab_titles[0:1],tab_links[0:1]))

    return dictionnary



def create_excel_files_by_categories_names(folder_categories_name: str, dictionnary_categories_names_and_url: dict)->bool:
    """
    Cette fonction permet de créer un dossier contenant des fichiers excels. 
    Elle prend 2 paramètres :
        - le nom du répertoire à créer
        - le dictionnaire dont les clefs seront les noms des fichiers excels à créer

    """
    for index, category_name in enumerate(dictionnary_categories_names_and_url.keys()):
        file = open(f"{folder_categories_name}/{category_name}.csv", "w")
        file.close()
        print(f"Création du fichier {category_name}. {index+1}/{len(dictionnary_categories_names_and_url)}")

    if index == len(dictionnary_categories_names_and_url):
        return True
    else:
        return False



def is_many_pages(soup:object)->bool:
    """
    Fonction permettant de savoir si le bouton "next" est présent une page.
    Elle prend en paramètre un objet "soup".
    Elle retourne un booléen.

    """
    li_next = soup.find("li", class_="next")
    return li_next



# tant qu'il y a de h3 (livres) on places les liens et les titles de la balise "a" dans le dictionnaire

def get_links_articles_for_one_categorie(url_article, tab, numero_page=1):
    """
    Cette fonction permets de récuperer les url des livres par catégorie.
    Elle prend en paramètre:
        - l'url de la page d'une catégorie
        - un tableau vide
        - le numéro de page  
    """
    
    #récuperation de l'url de la page courant et instanciation d'un objet "soup"
    reponse = requests.get(url_article)
    CONTENT_CATEGORY_PAGE = reponse.text

    soup = BeautifulSoup(CONTENT_CATEGORY_PAGE, "html.parser")

    # récupération des balises h3 et de leurs nombres par pages
    all_h3 = soup.find_all('h3')

    for index, h3 in enumerate(all_h3):

        article_link = h3.a["href"]
        tab.append(article_link.replace("../../../", f"{URL_HOME}catalogue/"))
        print(f"Récupération de l'url du livre : {h3.a.text}. {index+1}/{len(all_h3)}")
        
    # vérififcation d'un bouton next sur la page
    if not is_many_pages(soup):
        return tab
    elif is_many_pages(soup) and numero_page == 1:
        url_article = url_article.replace("index.html", f"page-{numero_page}.html")
        empty_tab = []
        return get_links_articles_for_one_categorie(url_article, empty_tab, numero_page+1)
    elif is_many_pages(soup):
        url_article = url_article.replace(f"page-{numero_page-1}.html", f"page-{numero_page}.html")
        return get_links_articles_for_one_categorie(url_article,tab, numero_page+1)



def get_links_articles_by_categories(dict_categories_and_links):
    dict_urls_by_categories = {}
    for category, link in dict_categories_and_links.items():
        list_urls_by_categories = []
        print(f"Récupération des urls des livres pour la catégorie {category}.")
        dict_urls_by_categories[category] = get_links_articles_for_one_categorie(link, list_urls_by_categories ,1)

    return dict_urls_by_categories


def image_download(url_image, article_name, image_folder):
    reponse = requests.get(url_image)
    
    if reponse.status_code == 200:
        f = open(f'Categories/{image_folder}/{url_image[-36:]}', 'wb')
        f.write(reponse.content)
        f.close()
        print(f"Téléchargement de l'image du livre {article_name} terminée.")
        return True
    else:
        print(f"ERREUR : {reponse.status_code}")

def get_rates(a_block_informations_of_book:list)->str:
    """
    Cette fonction permet de transformer une note alphabétique en numérique.
    Elle prend en paramètre une liste contenant la note à transformer.
    Elle retourne une chaine de caractère (la note en numérique)
    
    """
    for informations in a_block_informations_of_book:
        rate = informations.select_one('p[class*="star-rating"]')['class'][1]

    match rate:
        case "One":
            rate = "1"
        case "Two":
            rate = "2"
        case "Three":
            rate = "3"
        case "Four":
            rate = "4"
        case "Five":
            rate = "5"
        case _:
            rate = "no rate"
    return rate

def generate_dictionnary_informations_book(article_name, rate, description, informations_table, image_url, book_category,book_url)->dict:
    dictionnary = {}

    dictionnary["Url"]   = book_url
    dictionnary["Name"]  = article_name
    
    for data in informations_table:
        header = data.get_text(",", True).split(",")
        
        if len(header) > 1:
            match header[0]:
                case "Tax":
                    continue
                case "Number of reviews":
                    continue
                case "Price (excl. tax)":
                    price_exclude_tax = header[0].replace('Price' ,"Price (£)")
                    dictionnary[price_exclude_tax] = header[1].removeprefix("£")
                case "Price (incl. tax)":
                    price_include_tax = header[0].replace('Price' ,"Price (£)")
                    dictionnary[price_include_tax] = header[1].removeprefix("£")                    
                case "Availability":
                    number_book_in_stock = header[1].removeprefix("In stock (").removesuffix(" available)")
                    dictionnary[header[0]] = number_book_in_stock
                case _:
                    dictionnary[header[0]] = header[1]

    dictionnary["Description"]   = description
    dictionnary["Category"]      = book_category
    dictionnary["Rate"]          = rate
    dictionnary["Image"]         = image_url


    return dictionnary

def get_informations_book(book_url, book_category):
    """
    Cette fonction permet de récuperer les informations d'un livre à partir de son url.
    Elle prend en paramètre l'url du livre en question ainsi que sa catégorie.
    Elle retourne ces informations dans un dictionnaire

    """
    requete = requests.get(book_url)
    requete.encoding = requete.apparent_encoding

    soup = BeautifulSoup(requete.text, "html.parser")

    # titre
    article_name = soup.h1.text

    # récuperation des notes
    block_article = soup('div', class_="product_main")
    rate = get_rates(block_article)

    # description
    if not soup.find("div", id="product_description"):
        description = "no description" 
    else:
        description = soup.find("div", id="product_description").find_next('p').text
    description = description.replace(",", "")

    # tableau informations
    informations_table = soup.find("table", class_="table table-striped")
    
    # image
    block_image = soup.find('div', id="product_gallery")
    image_url = block_image.div.div.div.img['src'].replace("../../", URL_HOME)

    # url du produit
    product_page_url = book_url

    # catégorie du livre
    category = book_category

    # création dictionnaire
    dictionnary_informations_book = generate_dictionnary_informations_book(article_name, rate, description, informations_table, image_url, category, product_page_url)

    return dictionnary_informations_book



def save_data_by_categorie(dict_url:dict):
    os.makedirs(f"Categories/Images", exist_ok=True)
    for category, liste_url in dict_url.items():
        os.makedirs(f"Categories/Images/{category}", exist_ok=True)
        path_img = f"Images/{category}/"
        liste_infos_articles_category = []
        

        for index, url in enumerate(liste_url):
            print(f"Récupération des informations des livres de la catégorie {category} en cours... {index+1}/{len(liste_url)}")
            liste_infos_articles_category.append(get_informations_book(url, category))
        
        print(f"Impression des données de la catégorie {category} en cours ...")

        for dictionnaire in liste_infos_articles_category:
            with open(f'Categories/{category}.csv', 'w', encoding='utf-8', newline='') as f:
                fieldnames = dictionnaire.keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                [writer.writerow(dictionnary) for dictionnary in liste_infos_articles_category]
                # for dictionnary in liste_infos_articles_categorie:
                #     writer.writerow(dictionnary)

                url_img = dictionnaire['Image']
                name_img = dictionnaire['Name']
                image_download(url_img, name_img, path_img)
        
        print(f"L'impression des données pour la catégorie {category} a bien été effectuée.")