
# JOB SNIFFER

## Présentation

JOB SNIFFER est un outil de scraping d'offres d'emploi conçu pour extraire les annonces d'emploi de diverses sources, notamment HelloWork et Welcome to the Jungle. L'outil fournit une interface utilisateur conviviale pour rechercher des emplois, filtrer les résultats et analyser les tendances du marché de l'emploi.

## Fonctionnalités

*   Scraping d'offres d'emploi à partir de plusieurs sources (HelloWork, Welcome to the Jungle)
*   Recherche d'emplois par titre, localisation et autres critères
*   Filtrage des annonces d'emploi en fonction de divers attributs (type de contrat, entreprise, etc.)
*   Analyse des tendances et des statistiques du marché de l'emploi (nombre d'annonces, salaire moyen, etc.)
*   Comparaison des annonces d'emploi entre différentes sources et régions
*   -Export results to CSV and JSON formats


## Utilisation

1.  Entrez vos critères de recherche d'emploi (titre, localisation, etc.) dans la barre de recherche.
2.  Sélectionnez les sources que vous souhaitez scraper (HelloWork, Welcome to the Jungle, etc.).
3.  Cliquez sur le bouton "Lancer le scraping" pour lancer le processus de scraping.
4.  Parcourez les annonces d'emploi et filtrez-les en fonction de vos préférences.
5.  Analysez les tendances et les statistiques du marché de l'emploi fournies dans le tableau de bord.

## Tableau de bord

Le tableau de bord fournit diverses informations sur le marché de l'emploi, notamment :

*   Top 10 des entreprises avec le plus d'annonces d'emploi
*   Comparaison des annonces d'emploi entre différentes sources
*   Répartition des annonces d'emploi par type de contrat et localisation
*   Salaire moyen et salaire médian pour différents titres d'emploi
*   Tendances et statistiques du marché de l'emploi

![image](https://github.com/user-attachments/assets/21d7ac6b-d556-4c97-8fbe-e908b7c7ca6b)


![image](https://github.com/user-attachments/assets/98fe1d10-9e4d-4699-b2d4-00c592e93d5c)

![image](https://github.com/user-attachments/assets/215fb930-2290-4e3b-8aba-56a307c6cf49)

![image](https://github.com/user-attachments/assets/14583daa-7d02-480e-b20e-b8598884c088)

![image](https://github.com/user-attachments/assets/92e22920-88cb-4487-9ef3-825582704dc5)

![image](https://github.com/user-attachments/assets/09e6d88f-bf8a-4756-9a24-298048414c5e)

![image](https://github.com/user-attachments/assets/51bfa8e1-2e09-4c0f-aebd-20bdcb96e30d)

![image](https://github.com/user-attachments/assets/b0247be7-9805-4537-ae30-197016f4fe16)

![image](https://github.com/user-attachments/assets/e3b5d681-c00d-495e-b8c4-619f20a0da11)

![image](https://github.com/user-attachments/assets/3e107c9c-26cb-4207-b72e-fa7507476271)


## Exigences techniques

*   Python 3.x
*   Streamlit
*   Scrapy
*   Autres dépendances listées dans `requirements.txt`

## Installation

1.  Clonez le dépôt : `git clone (https://github.com/jebalisoumaya/JobSniffer-App.git)`

cd jobsniffer 

2.  Installez les dépendances : `pip install -r requirements.txt`
3.  Exécutez l'application : `streamlit run main.py`

## Partage des tâches 
HelloWork : Soumaya et Souhir 
Welcome to the jungle : Chaimae et Hoda
Indeed : (pas fini) : Chaimae 
Front : Soumaya & Chaimae
Analyse : Équipe 
--> Un push car plusieurs problèmes rencontrées avec Github & nos ordinateurs 

## Problèmes rencontrés 
-Indeed : Nous avons été confrontés à un CAPTCHA qui se rechargeait en boucle, malgré l’automatisation du clic sur le bouton "Je ne suis pas un robot". Ce comportement résulte de la détection par le site de signaux caractéristiques d’une automatisation, tels que des entêtes HTTP générés automatiquement et l’absence d’un contexte de navigation authentique. Lors du lancement du driver Selenium, le site identifie que le navigateur est piloté par un script, notamment à travers des propriétés comme navigator.webdriver ou une empreinte numérique non conforme à un usage humain. Par ailleurs, la fréquence élevée de nos requêtes a accentué cette détection, un trafic intensif étant typiquement associé à une activité automatisée. L’ensemble de ces facteurs déclenche une redirection systématique vers le CAPTCHA, bloquant l’accès sans mise en place d’une stratégie de contournement plus sophistiquée.


- Pagination : scrap que les résultats de la première page
