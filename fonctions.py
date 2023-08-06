from bs4 import BeautifulSoup
import requests, os, re, random
import csv


URL_HOME            = "https://books.toscrape.com/"
DATA_FOLDER_NAME    = "Data"
IMG_FOLDER_NAME     = "Images"

def timer(start:int, end:int):
    """
    Fonction permettant de calculer le temps écoulé pour l'execution du programme.
    Elle prend en paramètre :
        - un nombre représentant le début du chronomètre.
        - un nombre représentant l'arrèt du chronomètre.
    Elle ne retourne aucune valeur.
    """
    elapsed = end - start
    print(f"Le programme s'est executé en : {elapsed//60} minutes")

def getAllCategoriesTitles(url:str)-> dict:
    """
    Cette fonction permet de récuperer les titres et les liens de chaque catégories de la page d'accueil.
    Elle prend en paramètre l'url de la page d'acceuil.
    Elle retourne un dictionnaire avec les catégories comme clefs et les urls des catégories comme valeurs

    """ 

    CONTENT_BODY_HOME = requests.get(url).text

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
    dictionnary = dict(zip(tab_titles[0:2],tab_links[0:2]))

    return dictionnary


def is_many_pages(soup:object)->bool:
    """
    Fonction permettant de savoir si le bouton "next" est présent une page.
    Elle prend en paramètre un objet "soup".
    Elle retourne un booléen.

    """
    li_next = soup.find("li", class_="next")
    return li_next



def get_links_articles_for_one_categorie(url_article:str, tab:list, numero_page:int=1)->list:
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
        new_list = []
        return get_links_articles_for_one_categorie(url_article, new_list, numero_page+1)
    elif is_many_pages(soup):
        url_article = url_article.replace(f"page-{numero_page-1}.html", f"page-{numero_page}.html")
        return get_links_articles_for_one_categorie(url_article,tab, numero_page+1)



def get_links_articles_by_categories(dict_categories_and_links:dict)->dict:
    """
    Cette fonction permet de récuperer tous les liens des livres des différentes catégories.
    Elle prend en paramètre un dictionnaire contenant les urls des catégories.
    Elle retourne un dictionnaire contenant une catégorie en clef et une liste des liens des livres en valeur 
    """
    dict_urls_by_categories = {}
    for category, link in dict_categories_and_links.items():
        list_urls_by_categories = []
        print(f"Extraction des urls des livres pour la catégorie {category}.")
        dict_urls_by_categories[category] = get_links_articles_for_one_categorie(link, list_urls_by_categories,1)

    return dict_urls_by_categories


def image_download(url_image:str, article_name:str, image_folder:str):
    """
    Cette fonction permet de télécharger une image.
    Elle prend en paramètre :
        - l'url de l'image du livre
        - le nom du livre
        - le répertoire où télécharger l'image
    Elle ne retourne aucune valeur.
    """
    response = requests.get(url_image)
    img_name = re.sub(r'[^A-Za-z0-9 ]+', '', article_name[0:60])
    img_name = img_name.lower().replace(' ', '-')
    salt = random.randint(0,100)
    
    f = open(f'{DATA_FOLDER_NAME}/{image_folder}/{img_name}-{salt}.jpg', 'wb')
    f.write(response.content)
    f.close()
    print(f"Téléchargement de l'image du livre {article_name} terminée.")

    

def get_rates(a_block_informations_of_book:list)->str:
    """
    Cette fonction permet de passer la représentation verbale d'une note en sa répresentation numérique.
    Elle prend en paramètre une liste contenant la note à transformer.
    Elle retourne une chaine de caractère (la note en représentation numérique)
    
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

def generate_dictionnary_informations_book(book_url:str, book_category:str, book_name:str, rate:str, description:str, informations_table:list, image_url:str)->dict:
    """
    Cette fonction permet de récuperer les données d'un livre et de les stocker dans un dictionnaire.
    Elle prend en paramètre :
        - l'url du produit
        - sa catégorie
        - son nom 
        - sa note
        - sa description
        - la liste de ses caractéristiques (UPC, Prix, disponibilitée,...)
        - l'url de l'image de sa couverture

    Elle retourne les informations dans un dictionnaire.

    """
    dictionnary = {}
    dictionnary["Url"]   = book_url
    dictionnary["Name"]  = book_name
    
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

def get_informations_book(book_url:str, book_category:str)->dict:
    """
    Cette fonction permet de récuperer les informations d'un livre à partir de son url.
    Elle prend en paramètre l'url du livre en question ainsi que sa catégorie.
    Elle retourne ces informations sous la forme d'un dictionnaire

    """
    requete = requests.get(book_url)
    requete.encoding = requete.apparent_encoding

    soup = BeautifulSoup(requete.text, "html.parser")

    # titre
    book_name = soup.h1.text

    # récuperation des notes
    block_book = soup('div', class_="product_main")
    rate = get_rates(block_book)

    # description
    if not soup.find("div", id="product_description"):
        description = "no description" 
    else:
        description = soup.find("div", id="product_description").find_next('p').text
    description = description.replace(",","").replace(";","")

    # tableau informations
    informations_table = soup.find("table", class_="table table-striped")
    
    # image
    block_image = soup.find('div', id="product_gallery")
    image_url = block_image.div.div.div.img['src'].replace("../../", URL_HOME)

    # url du produit
    product_page_url = book_url

    # catégorie du livre
    category = book_category

    # création d'un dictionnaire contenant toutes les informations d'un livre 
    dictionnary_informations_book = generate_dictionnary_informations_book(product_page_url, category, book_name, rate, description, informations_table, image_url)

    return dictionnary_informations_book


def save_data(list_of_dictionnary_of_book_informations:list, category_name:str, path_img:str):

    for dictionnary in list_of_dictionnary_of_book_informations:
        with open(f'{DATA_FOLDER_NAME}/{category_name}.csv', 'w', encoding='utf-8', newline='') as f:
            fieldnames = dictionnary.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames,delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            # [writer.writerow(row) for row in list_of_dictionnary_of_book_informations]
            for row in list_of_dictionnary_of_book_informations:
                writer.writerow(row)

            url_img = dictionnary['Image']
            name_img = dictionnary['Name']
            image_download(url_img, name_img, path_img)


def load_data(dict_url:dict):
    """
    Cette fonction permet de sauvegarder des données dans des fichiers CSV ainsi que des images par catégories.
    Elle prend en paramètre un dictionnaire contenant les urls des livres par catégories.
    Elle ne retourne aucune valeur.
    """

    # Création du répertoire image 
    os.makedirs(f"{DATA_FOLDER_NAME}/{IMG_FOLDER_NAME}", exist_ok=True)
    for category, liste_url in dict_url.items():
        # Création d'un répertoire d'images pour chaque catégorie
        os.makedirs(f"{DATA_FOLDER_NAME}/{IMG_FOLDER_NAME}/{category}", exist_ok=True)
        path_img = f"{IMG_FOLDER_NAME}/{category}/"

        list_of_dictionnary_of_book_informations = []
        
        for index, url in enumerate(liste_url):
            print(f"Extraction des informations des livres de la catégorie {category} en cours... {index+1}/{len(liste_url)}")
            list_of_dictionnary_of_book_informations.append(get_informations_book(url, category))

        print(f"Sauvegarde des données de la catégorie {category} en cours ...")
        save_data(list_of_dictionnary_of_book_informations, category, path_img)
        print(f"La sauvegarde des données pour la catégorie {category} a bien été effectuée.")