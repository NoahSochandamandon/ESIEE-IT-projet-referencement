from collections import Counter
from tkinter import *
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
    balises_url = balise_url_list(url, balise)

    valeurs_attribut = []
    for balise_url in balises_url:
        if attribut in balise_url.attrs:
            valeurs_attribut.append(balise_url[attribut])
    return valeurs_attribut


# a utilisé direct
# prend en paramètre une url, un nom de balise html et rend les valeurs des balises de l'url
def balise_url_list(url, balise):
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
        return balises_url
    except Exception as e:
        return f"Erreur lors de l'analyse du HTML : {e}"


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


# fonction qui permet d'appeler toute les autres pour faire le référencement de la page donné par l'utilisateur adapter pour les demande de la partie 2
def fonction_analyse(url, mots_clefs_entree):
    url_lecture = url
    mots_clefs = mots_clefs_entree.split(",")
    mots_clefs = [mot.strip().lower() for mot in mots_clefs]

    try:
        response = requests.get(url_lecture)
    except requests.RequestException as e:
        print("Le lien entré est invalide")
        return f"Erreur de requête : {e}"

    liste_des_mots = compter_occurrences(html_en_texte(url_lecture))

    liste_cut = {}
    liste_mot_cle_pres = []
    nbr_lien_in = 0
    nbr_lien_out = 0
    pourcentage_balise_alt = 0

    nbr_balises_alt = 0
    nbr_balise_img = 0
    compteur = 0

    nbr_lien_in = nbr_lien_interne(url_lecture)
    nbr_lien_out = nbr_lien_externe(url_lecture)
    nbr_balises_alt = len(attribut_balise_url(url_lecture, "img", "alt"))
    nbr_balise_img = len(balise_url_list(url_lecture, "img"))

    pourcentage_balise_alt = (nbr_balises_alt / nbr_balise_img) * 100

    # regarde les mots cle les plus presents sur la page
    for cle, valeur in liste_des_mots.items():
        if compteur < 3:
            liste_cut[cle] = valeur
            compteur += 1

    # regarde si les mots clef sont dans la liste des 3 mots les plus présent sur le site
    for mot in mots_clefs:
        if liste_cut.get(mot) is not None:
            liste_mot_cle_pres.append(mot)

    affichage_resultats(
        nbr_lien_in,
        nbr_lien_out,
        liste_cut,
        liste_mot_cle_pres,
        pourcentage_balise_alt,
    )


def lancement_ihm():
    interface_1 = Tk()
    interface_1.title("Référencement")

    url_analyse_label = Label(interface_1, text="URL à analyser :").pack()
    url_analyse = Entry(interface_1, width=50)
    url_analyse.pack()

    mots_clefs_entree_label = Label(
        interface_1,
        text='Mots-clés pour le référencement : (ecrire comme ceci : "mot1, mot2, mot3")',
    ).pack()
    mots_clefs_entree = Entry(interface_1, width=50)
    mots_clefs_entree.pack()

    bouton_analyse = Button(
        interface_1,
        text="Lancer l'analyse",
        command=lambda: [
            fonction_analyse(url_analyse.get(), mots_clefs_entree.get()),
            interface_1.destroy(),
        ],
    ).pack()

    interface_1.mainloop()


def affichage_resultats(
    nbr_lien_in,
    nbr_lien_out,
    liste_mot_present,
    liste_mot_cle_pres,
    pourcentage_balise_alt,
):
    interface_2 = Tk()
    interface_2.title("Résultats de l'analyse")

    nbr_lien_in_label = Label(
        interface_2,
        text=f"Il y a sur votre site : {nbr_lien_in} liens qui pointe sur votre site",
    ).pack()

    nbr_lien_out_label = Label(
        interface_2,
        text=f"Il y a sur votre site : {nbr_lien_out} liens qui pointe sur un site externe",
    ).pack()

    pourcentage_balise_alt_label = Label(
        interface_2,
        text=f"Il y a {pourcentage_balise_alt}% de balise alt sur votre page",
    ).pack()

    if len(liste_mot_cle_pres) == 0:
        mots_cle_present_label = Label(
            interface_2,
            text=f"Il n'y a pas le moindre mots cle que vous souhaitié parmis les 3 mots les plus presents votre page",
        ).pack()
    elif len(liste_mot_cle_pres) == 1:
        mots_cle_present_label = Label(
            interface_2,
            text=f"Le seul mot cle que vous souhaitier qui est dans les plus presents sur votre page est : {liste_mot_cle_pres[0]}",
        ).pack()
    elif len(liste_mot_cle_pres) == 2:
        mots_cle_present_label = Label(
            interface_2,
            text=f"Les seul mots cles que vous souhaitier qui sont dans les plus presents sur votre page sont : {liste_mot_cle_pres[0]} et {liste_mot_cle_pres[1]}",
        ).pack()
    elif len(liste_mot_cle_pres) == 3:
        mots_cle_present_label = Label(
            interface_2,
            text=f"Tout les mots que vous souhaitiez vérifier, sont parmis les 3 plus présent de votre page",
        ).pack()

    compteur = 0
    mots_cle_txt = ""

    for cle, valeur in liste_mot_present.items():
        if compteur < 3:
            mots_cle_txt += f"- {cle}: {valeur}\n"
            compteur += 1

    liste_mot_cle_pres_label = Label(
        interface_2,
        text=f"Voici les 3 mots cle les plus presents sur votre page :\n {mots_cle_txt}",
    ).pack()

    interface_2.mainloop()


lancement_ihm()
