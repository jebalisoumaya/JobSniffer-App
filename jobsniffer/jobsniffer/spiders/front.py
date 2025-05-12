import streamlit as st
import subprocess
import pandas as pd
import os
import sys
import re
import numpy as np

st.set_page_config(page_title="🔍 JOBSNIFFER 🔍", layout="centered")

st.title("🔍 Scraper d'offres AKA JOBSNIFFER 🔍")

# Champs pour les paramètres de scraping
job_title = st.text_input("🔧 Intitulé du poste :", placeholder="Exemple : Data Analyst")
location = st.text_input("📍 Localisation :", placeholder="Exemple : Paris")
max_pages = st.slider("📄 Nombre de pages à scraper :", 1, 10, 3)

# Fonction pour extraire et traiter les valeurs de salaire
def extract_salary(salary_text):
    if pd.isna(salary_text) or not isinstance(salary_text, str):
        return None
    
    # Extraire les nombres de la chaîne en gérant les formats avec espace comme séparateur de milliers
    numbers = re.findall(r'(\d+\s*\d*)', salary_text)
    
    if not numbers:
        return None
    
    # Traiter les fourchettes salariales
    values = []
    for num in numbers:
        # Enlever les espaces et convertir en nombre
        cleaned_num = num.replace(' ', '')
        if cleaned_num:
            try:
                values.append(float(cleaned_num))
            except:
                pass
    
    # Retourner la moyenne si c'est une fourchette, ou la valeur unique
    if values:
        return sum(values) / len(values)
    return None

if st.button("Lancer le scraping"):
    if not job_title or not location:
        st.warning("Merci de remplir les champs 'Intitulé du poste' et 'Localisation'.")
    else:
        with st.spinner("Scraping en cours... ⏳"):
            # Supprimer le fichier précédent s'il existe
            if os.path.exists("resultsHelloWork.json"):
                os.remove("resultsHelloWork.json")

            # Lancer le processus Scrapy
            result = subprocess.run([
                sys.executable, "-m", "scrapy", "crawl", "hellowork",
                "-a", f"job_title={job_title}",
                "-a", f"location={location}",
                "-a", f"max_pages={max_pages}",
                "-o", "resultsHelloWork.json"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Vérification du résultat du scraping
            if result.returncode == 0 and os.path.exists("resultsHelloWork.json"):
                st.success("Scraping terminé ! 🎉")
                with open("resultsHelloWork.json", encoding="utf-8") as f:
                    data = pd.read_json(f)

                # Traiter les salaires
                if 'salary' in data.columns:
                    data['salary_numeric'] = data['salary'].apply(extract_salary)

                # Store the resultsHelloWork in a CSV file
                if os.path.exists("all_resultsHelloWork.csv"):
                    existing_data = pd.read_csv("all_resultsHelloWork.csv")
                    combined_data = pd.concat([existing_data, data])
                    combined_data.to_csv("all_resultsHelloWork.csv", index=False)
                else:
                    data.to_csv("all_resultsHelloWork.csv", index=False)

                # Afficher les données
                st.subheader("📊 Résultats du scraping")
                
                # Add search filter
                search_query = st.text_input("🔍 Filtrer les résultats:", "")
                if search_query:
                    filtered_data = data[data.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)]
                    st.dataframe(filtered_data, use_container_width=True)
                    st.info(f"{len(filtered_data)} offres correspondant aux critères sur {len(data)} au total")
                else:
                    st.dataframe(data, use_container_width=True)
                
                # Créer un tableau de bord avancé
                st.subheader("📈 Analyse des offres d'emploi")
                
                # Première ligne d'analyses côte à côte
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Types de contrats**")
                    contract_type_count = data['contract_type'].value_counts().reset_index()
                    contract_type_count.columns = ['Type de contrat', 'Nombre']
                    
                    # Afficher graphique et tableau
                    st.bar_chart(contract_type_count.set_index('Type de contrat'))
                    st.dataframe(contract_type_count, hide_index=True, use_container_width=True)
                
                with col2:
                    st.write("**Répartition géographique**")
                    location_count = data['location'].value_counts().reset_index()
                    location_count.columns = ['Localisation', 'Nombre']
                    
                    # Limiter aux 10 premières régions pour lisibilité
                    top_locations = location_count.head(10)
                    st.bar_chart(top_locations.set_index('Localisation'))
                    st.dataframe(top_locations, hide_index=True, use_container_width=True)
                
                # Deuxième ligne d'analyses
                col3, col4 = st.columns(2)
                
                with col3:
                    st.write("**Analyse des entreprises**")
                    company_count = data['company_name'].value_counts().reset_index()
                    company_count.columns = ['Entreprise', 'Nombre d\'offres']
                    
                    # Top 10 des entreprises qui recrutent le plus
                    top_companies = company_count.head(10)
                    st.bar_chart(top_companies.set_index('Entreprise'))
                    st.dataframe(top_companies, hide_index=True, use_container_width=True)
                
                with col4:
                    # Essayer d'analyser les salaires s'ils existent
                    if 'salary_numeric' in data.columns and data['salary_numeric'].notna().any():
                        st.write("**Analyse des salaires**")
                        
                        # Filtrer les valeurs non nulles pour le salaire
                        salary_data = data[data['salary_numeric'].notna()]
                        
                        if len(salary_data) > 0:
                            avg_salary = salary_data['salary_numeric'].mean()
                            median_salary = salary_data['salary_numeric'].median()
                            min_salary = salary_data['salary_numeric'].min()
                            max_salary = salary_data['salary_numeric'].max()
                            
                            # Afficher les métriques clés
                            metrics_col1, metrics_col2 = st.columns(2)
                            metrics_col1.metric("Salaire moyen", f"{avg_salary:,.2f} €")
                            metrics_col2.metric("Salaire médian", f"{median_salary:,.2f} €")
                            
                            metrics_col3, metrics_col4 = st.columns(2)
                            metrics_col3.metric("Salaire minimum", f"{min_salary:,.2f} €")
                            metrics_col4.metric("Salaire maximum", f"{max_salary:,.2f} €")
                            
                            # Histogramme des salaires
                            salary_hist_data = pd.DataFrame({'Salaire': salary_data['salary_numeric']})
                            st.bar_chart(salary_hist_data)
                            
                            # Afficher quelques exemples
                            with st.expander("Exemples de salaires"):
                                samples = data[['job_title', 'salary', 'salary_numeric']].dropna(subset=['salary_numeric']).head(5)
                                st.dataframe(samples, use_container_width=True)
                    else:
                        st.write("**Analyse des dates de publication**")
                        if 'publication_date' in data.columns and data['publication_date'].notna().any():
                            # Convertir en datetime si nécessaire
                            try:
                                data['publication_date'] = pd.to_datetime(data['publication_date'])
                                pub_date_count = data['publication_date'].dt.date.value_counts().sort_index()
                                st.line_chart(pub_date_count)
                                st.write("Nombre d'offres publiées par jour")
                            except:
                                st.write("Impossible d'analyser les dates de publication")
                
                # Statistiques générales
                st.subheader("📊 Statistiques générales")
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                
                stats_col1.metric("Nombre total d'offres", len(data))
                stats_col2.metric("Type de contrat le plus fréquent", 
                                 data['contract_type'].value_counts().index[0] if 'contract_type' in data.columns and len(data) > 0 else "N/A")
                stats_col3.metric("Région avec le plus d'offres", 
                                 data['location'].value_counts().index[0] if 'location' in data.columns and len(data) > 0 else "N/A")

                # Bouton pour télécharger les résultats
                st.download_button(
                    "⬇️ Télécharger les résultats en JSON",
                    data=open("resultsHelloWork.json", "rb"),
                    file_name="hellowork_offres.json"
                )
            else:
                st.error("Une erreur est survenue pendant le scraping.")
                st.code(result.stderr)

# Ajouter un onglet pour comparer les résultats
st.subheader("🔍 Comparaison des recherches")
if os.path.exists("all_resultsHelloWork.csv"):
    all_data = pd.read_csv("all_resultsHelloWork.csv")
    
    # Générer les options de comparaison
    job_titles = sorted(all_data['job_title'].unique().tolist()) if 'job_title' in all_data.columns else []
    locations = sorted(all_data['location'].unique().tolist()) if 'location' in all_data.columns else []
    
    # Type de comparaison
    compare_type = st.radio("Mode de comparaison:", ["Par région", "Par intitulé de poste"])
    
    col1, col2 = st.columns(2)
    
    if compare_type == "Par région":
        with col1:
            compare_job = st.selectbox("Poste à comparer", ["Tous les postes"] + job_titles)
        with col2:
            compare_metric = st.selectbox("Métrique", ["Nombre d'offres", "Salaire moyen", "Types de contrat"])
        
        # Filtrer les données
        if compare_job != "Tous les postes":
            filtered_data = all_data[all_data['job_title'] == compare_job]
        else:
            filtered_data = all_data
        
        # Effectuer les comparaisons
        if compare_metric == "Nombre d'offres":
            region_counts = filtered_data['location'].value_counts().reset_index()
            region_counts.columns = ['Région', 'Nombre d\'offres']
            st.bar_chart(region_counts.set_index('Région'))
            st.dataframe(region_counts, hide_index=True, use_container_width=True)
            
        elif compare_metric == "Salaire moyen" and 'salary_numeric' in filtered_data.columns:
            # Traiter les salaires si ce n'est pas déjà fait
            if 'salary_numeric' not in filtered_data.columns and 'salary' in filtered_data.columns:
                filtered_data['salary_numeric'] = filtered_data['salary'].apply(extract_salary)
                
            # Grouper par région et calculer la moyenne
            salary_by_region = filtered_data.groupby('location')['salary_numeric'].mean().reset_index()
            salary_by_region.columns = ['Région', 'Salaire moyen']
            salary_by_region = salary_by_region.dropna()
            
            if not salary_by_region.empty:
                st.bar_chart(salary_by_region.set_index('Région'))
                st.dataframe(salary_by_region, hide_index=True, use_container_width=True)
            else:
                st.write("Pas de données salariales disponibles pour cette comparaison.")
                
        elif compare_metric == "Types de contrat":
            contract_by_region = filtered_data.groupby(['location', 'contract_type']).size().reset_index()
            contract_by_region.columns = ['Région', 'Type de contrat', 'Nombre']
            
            # Pivoter pour obtenir une colonne par type de contrat
            pivot_data = contract_by_region.pivot(index='Région', columns='Type de contrat', values='Nombre').fillna(0)
            
            # Afficher la table
            st.write("**Répartition des types de contrat par région**")
            st.dataframe(pivot_data, use_container_width=True)
            
            # Créer un graphique empilé
            st.bar_chart(pivot_data)
    
    else:  # Par intitulé de poste
        with col1:
            compare_location = st.selectbox("Région à comparer", ["Toutes les régions"] + locations)
        with col2:
            compare_metric = st.selectbox("Métrique", ["Nombre d'offres", "Salaire moyen", "Types de contrat"], key="metric_by_job")
        
        # Filtrer les données
        if compare_location != "Toutes les régions":
            # Permet une recherche partielle dans les locations (e.g. "Paris" trouvera "Paris - 75")
            filtered_data = all_data[all_data['location'].str.contains(compare_location, case=False, na=False)]
        else:
            filtered_data = all_data
        
        # Effectuer les comparaisons
        if compare_metric == "Nombre d'offres":
            job_counts = filtered_data['job_title'].value_counts().reset_index()
            job_counts.columns = ['Intitulé du poste', 'Nombre d\'offres']
            
            # Afficher le graphique et la table
            st.bar_chart(job_counts.set_index('Intitulé du poste'))
            st.dataframe(job_counts, hide_index=True, use_container_width=True)
            
        elif compare_metric == "Salaire moyen" and 'salary_numeric' in filtered_data.columns:
            # Grouper par poste et calculer la moyenne
            salary_by_job = filtered_data.groupby('job_title')['salary_numeric'].mean().reset_index()
            salary_by_job.columns = ['Intitulé du poste', 'Salaire moyen']
            salary_by_job = salary_by_job.dropna()
            
            if not salary_by_job.empty:
                salary_by_job = salary_by_job.sort_values(by='Salaire moyen', ascending=False)
                st.bar_chart(salary_by_job.set_index('Intitulé du poste'))
                st.dataframe(salary_by_job, hide_index=True, use_container_width=True)
                
                # Ajouter une visualisation supplémentaire - Box plot si possible
                st.write("**Distribution des salaires par poste**")
                try:
                    import plotly.express as px
                    fig = px.box(
                        filtered_data.dropna(subset=['salary_numeric']), 
                        x='job_title', 
                        y='salary_numeric',
                        title="Distribution des salaires par poste",
                        labels={"job_title": "Intitulé du poste", "salary_numeric": "Salaire"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.write("Graphique avancé indisponible - installez plotly pour une meilleure visualisation")
            else:
                st.write("Pas de données salariales disponibles pour cette comparaison.")
                
        elif compare_metric == "Types de contrat":
            contract_by_job = filtered_data.groupby(['job_title', 'contract_type']).size().reset_index()
            contract_by_job.columns = ['Intitulé du poste', 'Type de contrat', 'Nombre']
            
            # Pivoter pour obtenir une colonne par type de contrat
            pivot_job_data = contract_by_job.pivot(
                index='Intitulé du poste', 
                columns='Type de contrat', 
                values='Nombre'
            ).fillna(0)
            
            # Afficher la table
            st.write("**Répartition des types de contrat par poste**")
            st.dataframe(pivot_job_data, use_container_width=True)
            
            # Créer un graphique empilé
            st.bar_chart(pivot_job_data)
else:
    st.write("Aucune donnée disponible pour la comparaison. Veuillez d'abord effectuer une recherche.")

# Ajouter une section pour les insights
with st.expander("💡 Insights et recommandations"):
    st.write("""
    ### Insights clés basés sur vos recherches
    
    - **Découvrez les régions qui recrutent le plus** pour votre poste cible
    - **Comparez les salaires** entre différentes régions et postes
    - **Analysez les types de contrats** pour identifier les tendances du marché
    - **Suivez l'évolution** des offres d'emploi dans le temps
    
    ### Comment utiliser ces données
    
    Pour améliorer votre recherche d'emploi, utilisez les comparaisons pour:
    1. Cibler les régions avec le plus d'opportunités
    2. Négocier votre salaire avec des données réelles du marché
    3. Adapter votre candidature selon les types de contrats disponibles
    """)