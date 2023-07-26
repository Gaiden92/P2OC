from bs4 import BeautifulSoup
import requests, openpyxl, os, re, openpyxl.styles, random

URL_HOME = "https://books.toscrape.com/"

def getAllCategoriesTitles(url:str)-> dict:
    """
    Cette fonction permet de récuper les titres et les liens de chaque catégories de la page d'accueil.
    Elle prend en paramètre une variable avec le contenu d'une page html parsée.
    Elle retourne 1 dictionnaire avec les catégories comme clefs et les urls des catégories comme valeurs

    """ 

    CONTENT_BODY_HOME = requests.get(url).text
    reponse = requests.get(url)


    soup = BeautifulSoup(CONTENT_BODY_HOME, "html.parser")
    menu_nav_categories = soup.find("ul", class_="nav nav-list")

    ul_category = menu_nav_categories.li.ul

    # récuperation des titres
    tab_titles = [ul_category.li.a.getText('',True) for ul_category.li.a in ul_category]
    tab_titles = " ".join(tab_titles).removeprefix(' ').removesuffix(' ').split('  ')

    #récupération des liens
    tab_links = [url+e['href'] for e in ul_category.find_all('a')]

    dictionnaire = {tab_titles[i]:tab_links[i] for i in range(len(tab_links))}
    return dictionnaire



def create_categories_excel_files(directory_categories: str, dic: dict)-> bool:
    """
    Cette fonction permet de créer un dossier contenant des fichiers excels.
    Elle prend 2 paramètres :
        - le nom du repertoir à créer
        - le dictionnaire dont les clefs seront les noms des fichiers excels à créer
    Elle retourne un booléen.

    """
    try:
        os.mkdir(directory_categories)

    except FileExistsError:
        return False
    for k in dic.keys():
        fichier_excel = openpyxl.Workbook()
        fichier_excel.save((f"{directory_categories}/{k}.xlsx"))
        print(f"Création du fichier {k}")

    return True



def image_download(url_image, article_name, image_dir):
    reponse = requests.get(url_image)

    if reponse.status_code == 200:
        salt = str(random.randint(0,100))
        article_name = re.sub('[^a-zA-Z]+', '', article_name).lower()
        article_name = salt+article_name
        if len(article_name) > 40:
            article_name = article_name[0:30]+salt
        f = open(f'Categories/{image_dir}/{article_name}.jpg', 'wb')
        f.write(reponse.content)
        f.close()
        print(f"Téléchargement de l'image du livre {article_name} terminée.")
        return True
    else:
        print(f"ERREUR : {reponse.status_code}")


def get_infos_article(url):

    requete = requests.get(url)
    requete.encoding = requete.apparent_encoding

    soup = BeautifulSoup(requete.text, "html.parser")

    # titre
    article_name = soup.h1.text

    # récuperation des notes
    block_article = soup('div', class_="product_main")
    for e in block_article:
        rate = e.select_one('p[class*="star-rating"]')['class'][1]

    # description
    description = "aucune description" if not soup.find("div", id="product_description") else soup.find("div", id="product_description").find_next('p').text

    # tableau infos
    tableau = soup.find("table", class_="table table-striped")


    # image
    bloc_image = soup.find('div', id="product_gallery")
    image_url = bloc_image.div.div.div.img['src'].replace("../../", URL_HOME)


    # création dictionnaire
    dictionnaire_infos_article = {}

    dictionnaire_infos_article["Nom"]           = article_name
    dictionnaire_infos_article["Note"]          = rate
    dictionnaire_infos_article["Description"]   = description
    for e in tableau:
        info = e.get_text(",", True).split(",")
        if len(info) > 1:
            dictionnaire_infos_article[info[0]] = info[1]
    dictionnaire_infos_article["Image"]         = image_url

    return dictionnaire_infos_article




def save_data_by_categorie(dict_url:dict):
    os.makedirs(f"Categories/Images", exist_ok=True)
    for categorie, liste_url in dict_url.items():
        liste_infos_articles_categorie = []
        
        for i in range(len(liste_url)):
            print(f"récupération infos par livres de la catégorie {categorie} en cours...")
            liste_infos_articles_categorie.append(get_infos_article(liste_url[i]))


        print(f"impression des données de la catégorie {categorie} en cours ...")
        fichier = openpyxl.load_workbook(f"Categories/{categorie}.xlsx")
        sheet = fichier.active
        row = 2



        for i in range(len(liste_infos_articles_categorie)):
            coll = 1
            for keys, values in liste_infos_articles_categorie[i].items():
                if keys == "Image":
                    url_img = liste_infos_articles_categorie[i]['Image']
                    name_img = liste_infos_articles_categorie[i]['Nom']
                    image_download(url_img, name_img,"Images")

                sheet.cell(1, coll).value = keys
                sheet.cell(row,coll).value = values
                coll+=1
                
            row+=1
        print(f"l'impression des données pour la catégorie {categorie} a bien été effectuée.")
        fichier.save(f"Categories/{categorie}.xlsx")



def is_many_pages(soupe:object)->bool:
    li_next = soupe.find("li", class_="next")
    return True if li_next else False





# tant qu'il y a de h3 (articles) on places les liens et les titles de la balise a dans un dictionnaire

def get_links_articles_for_one_categorie(url_article, tab_vide, numero_page=1):

    #récuperation de l'url de la page courant et instanciation d'un objet "soup"
    reponse = requests.get(url_article)
    CONTENT_CATEGORY_PAGE = reponse.text

    soup = BeautifulSoup(CONTENT_CATEGORY_PAGE, "html.parser")

    # récupération des baliises h3 et de leurs nombres par pages
    all_h3 = soup.find_all('h3')
    nb_h3 = len(all_h3)
    for i in range(nb_h3):
        article_link = all_h3[i].a["href"]
        tab_vide.append(article_link.replace("../../../", f"{URL_HOME}catalogue/"))

    # vérififcation d'un bouton next sur la page
    if not is_many_pages(soup):
        return tab_vide
    elif is_many_pages(soup) and numero_page == 1:
        url_article = url_article.replace("index.html", f"page-{numero_page}.html")
        empty_tab = []
        return get_links_articles_for_one_categorie(url_article, empty_tab, numero_page+1)
    elif is_many_pages(soup):
        url_article = url_article.replace(f"page-{numero_page-1}.html", f"page-{numero_page}.html")
        return get_links_articles_for_one_categorie(url_article,tab_vide, numero_page+1)



def get_links_articles_by_categories(dict_categories_and_links):
    dict_urls_by_categories = {}

    for categorie, link in dict_categories_and_links.items():
        list_urls_by_categories = []
        print(f"Récupération des urls des livres pour la catégorie {categorie}")
        dict_urls_by_categories[categorie] = get_links_articles_for_one_categorie(link,list_urls_by_categories ,1)

    return dict_urls_by_categories
