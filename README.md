# StrateGis — Site vitrine

Site vitrine de StrateGis présentant 4 services :
- Site vitrine
- Applications mobiles & iOS
- Applications desktop
- Agents IA (RAG)

## Structure du projet

    strategis/
      index.html          Page principale
      README.md           Ce fichier
      css/
        style.css         Styles
      js/
        main.js           Scripts
      img/
        service-web.jpg
        service-mobile.jpg
        service-desktop.jpg
        service-ia.jpg
        showcase-design.jpg
        showcase-ia.jpg

## Images

Les 6 images sont téléchargées automatiquement par le script create_project.py.
Si vous voulez les remplacer, gardez les mêmes noms de fichiers.

## Configuration Formspree

Déjà configuré — Le formulaire utilise l'ID Formspree : mvkgjpjn
Si vous voulez le changer, modifiez dans index.html :
action="https://formspree.io/f/mvkgjpjn"

## Lancement local

Ouvrez simplement index.html dans un navigateur, ou lancez un serveur local :

    cd "C:\projetPersonnelle\strategis"
    python -m http.server 8000

Puis ouvrez http://localhost:8000
"# Site_vitrine" 
