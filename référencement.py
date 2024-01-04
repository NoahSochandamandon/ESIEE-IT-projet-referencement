from collections import Counter
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import csv
import requests

# variable par défault
chemin_fichier_parasites = "mots_parasites.csv"
chemin_fichier_texte = "texte_test.csv"
chemin_fichier_html = "test_lecture.html"
url_lecture = "https://www.esiee-it.fr/fr"
balise = "h1"


# pas utilisé direct (pas important, utiliser pour les tests)
# récupère le texte qui sera annalyser dans un fichier csv
def recuperation_texte(chemin):
    texte = ""
    with open(chemin, mode="r", encoding="utf-8") as fichier:
        contenu = fichier.read()
    return contenu


# pas utilisé direct (utiliser dans compter_occurrences)
# sépare les mots et enlève la ponctuation à la fin des mots
def nettoyer_texte(texte):
    texte_nettoye = re.sub(r"[^\w\s]", "", texte)
    return texte_nettoye


# pas utilisé direct (utiliser dans compter_occurrences)
# récupère la chaine de mots parasite dans un csv
def lire_mots_parasites(chemin):
    mots_parasites = []
    with open(chemin, mode="r", encoding="utf-8") as fichier:
        lecteur_fichier = csv.reader(fichier)
        for ligne in lecteur_fichier:
            mots_parasites += ligne
    return mots_parasites


# a utilisé direct
# prend en paramètre un texte, et compte la récurences des mots, ressort un tableau
def compter_occurrences(texte):
    # texte = recuperation_texte(texte)

    texte = nettoyer_texte(texte)

    mots = texte.lower().split()

    comptage = Counter(mots)

    for mot in lire_mots_parasites(chemin_fichier_parasites):
        comptage.pop(mot, None)

    return dict(sorted(comptage.items(), key=lambda item: item[1], reverse=True))


# a utilisé en paramètre dans compter_occurances
# prend en paramètre une page internet, et retourne tout le texte présent
def html_en_texte(url):
    resultat = requests.get(url)
    soup = BeautifulSoup(resultat.text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


# a utilisé direct
# prend en paramètre une url, un nom de balise html et un attribut, et rend les valeurs des attributs des balises de l'url
def attribut_balise_url(url, balise, attribut):
    # gère pour voir si la page html est accessible
    try:
        response = requests.get(url)
    except requests.RequestException as e:
        return f"Erreur de requête : {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    # gère pour voir si la balise est présente dans la page html
    try:
        balises_url = soup.find_all(balise)
        if balises_url is None:
            return f"La balise '{balise}' n'a pas été trouvée."
    except Exception as e:
        return f"Erreur lors de l'analyse du HTML : {e}"

    valeurs_attribut = []
    for balise_url in balises_url:
        if attribut in balise_url.attrs:
            valeurs_attribut.append(balise_url[attribut])
    return valeurs_attribut


# a utilisé direct
# extrait le nom de domaine d'une url
def nom_de_domaine(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc


# a utilisé direct
# renvoie le nbr de lien externe de la page dont on spécifie l'url (ne compte que pour les balises <a>)
def nbr_lien_externe(url):
    all_lien = attribut_balise_url(url, "a", "href")
    lien_out = [
        href
        for href in all_lien
        if href.startswith("http://") or href.startswith("https://")
    ]
    return len(lien_out)


# a utilisé direct
# renvoie le nbr de lien interne de la page dont on spécifie l'url (ne compte que pour les balises <a>)
def nbr_lien_interne(url):
    all_lien = attribut_balise_url(url, "a", "href")
    lien_in = [
        href
        for href in all_lien
        if not (href.startswith("http://") or href.startswith("https://"))
    ]
    return len(lien_in)


# fonction qui permet d'appeler toute les autres pour faire le référencement de la page donné par l'utilisateur
def fonction_lancement():
    url_lecture = input(
        "Veuillez entre l'url à analysée (si elle n'est pas valide cela ne fonctionnera pas) : "
    )

    try:
        response = requests.get(url_lecture)
    except requests.RequestException as e:
        print("Le lien entré est invalide")
        return f"Erreur de requête : {e}"

    liste_des_mots = compter_occurrences(html_en_texte(url_lecture))
    liste_cut = {}
    compteur = 0
    nbr_lien_in = 0
    nbr_lien_out = 0
    nbr_balises_alt = 0

    nbr_lien_out = nbr_lien_externe(url_lecture)
    nbr_lien_in = nbr_lien_interne(url_lecture)
    nbr_balises_alt = len(attribut_balise_url(url_lecture, "img", "alt"))

    print("Voici les 3 mots les plus présent sur la page :")
    for cle, valeur in liste_des_mots.items():
        if compteur < 3:
            print("-", cle, valeur)
            liste_cut[cle] = valeur
            compteur += 1
    print("Voici le nbr de lien qui pointent vers un site externe :", nbr_lien_out)
    print(
        "Voici le nbr de lien qui pointent vers le site",
        nom_de_domaine(url_lecture),
        ":",
        nbr_lien_in,
    )
    print("Voici le nbr de balise alt présente sur la page :", nbr_balises_alt)


fonction_lancement()

# print(compter_occurrences(html_en_texte(url_lecture)))
