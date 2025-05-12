import streamlit as st
import subprocess
import pandas as pd
import os
import sys
import re
import numpy as np
import plotly.express as px

st.set_page_config(page_title="🔍 JOBSNIFFER 🔍", layout="centered")

st.title("🔍 Scraper d'offres AKA JOBSNIFFER 🔍")

# Fonction pour s'assurer qu'une colonne est bien numérique
def ensure_numeric(df, column_name):
    """Convert column to numeric, handling errors gracefully"""
    if column_name in df.columns:
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df

# Champs pour les paramètres de scraping
job_title = st.text_input("🔧 Intitulé du poste :", placeholder="Exemple : Data Analyst")
location = st.text_input("📍 Localisation :", placeholder="Exemple : Paris")
max_pages = st.slider("📄 Nombre de pages à scraper :", 1, 10, 3)

# Sélection des sources
st.write("### 🌐 Sources de données")
col1, col2 = st.columns(2)
with col1:
    scrape_hellowork = st.checkbox("HelloWork", value=True)
with col2:
    scrape_wttj = st.checkbox("Welcome to the Jungle", value=False)

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
    elif not scrape_hellowork and not scrape_wttj:
        st.warning("Veuillez sélectionner au moins une source de données.")
    else:
        # Dictionnaire pour stocker les résultats de chaque source
        all_results = {}
        
        # Scraper HelloWork si sélectionné
        if scrape_hellowork:
            with st.spinner("Scraping HelloWork en cours... ⏳"):
                # Supprimer le fichier précédent s'il existe
                if os.path.exists("results_hellowork.json"):
                    os.remove("results_hellowork.json")

                # Lancer le processus Scrapy pour HelloWork
                result_hw = subprocess.run([
                    sys.executable, "-m", "scrapy", "crawl", "hellowork",
                    "-a", f"job_title={job_title}",
                    "-a", f"location={location}",
                    "-a", f"max_pages={max_pages}",
                    "-o", "results_hellowork.json"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Vérification du résultat du scraping
                if result_hw.returncode == 0 and os.path.exists("results_hellowork.json"):
                    with open("results_hellowork.json", encoding="utf-8") as f:
                        data_hw = pd.read_json(f)
                        data_hw['source'] = 'HelloWork'
                        all_results['HelloWork'] = data_hw
                        st.success(f"HelloWork: {len(data_hw)} offres trouvées")
                else:
                    st.error("Une erreur est survenue pendant le scraping de HelloWork.")
                    with st.expander("Détails de l'erreur"):
                        st.code(result_hw.stderr)
        
        # Scraper Welcome to the Jungle si sélectionné
        if scrape_wttj:
            with st.spinner("Scraping Welcome to the Jungle en cours... ⏳"):
                # Supprimer le fichier précédent s'il existe
                if os.path.exists("results_wttj.json"):
                    os.remove("results_wttj.json")

                # Lancer le processus Scrapy pour WTTJ
                result_wttj = subprocess.run([
                    sys.executable, "-m", "scrapy", "crawl", "wttj",
                    "-a", f"job_title={job_title}",
                    "-a", f"location={location}",
                    "-a", f"max_pages={max_pages}",
                    "-o", "results_wttj.json"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Vérification du résultat du scraping
        if result_wttj.returncode == 0 and os.path.exists("results_wttj.json"):
                    with open("results_wttj.json", encoding="utf-8") as f:
                        data_wttj = pd.read_json(f)
                        data_wttj['source'] = 'WTTJ'
                        all_results['WTTJ'] = data_wttj
                        st.success(f"WTTJ: {len(data_wttj)} offres trouvées")
        else:
                    st.error("Une erreur est survenue pendant le scraping de Welcome to the Jungle.")
                    with st.expander("Détails de l'erreur"):
                        st.code(result_wttj.stderr)
        
        # Combiner tous les résultats en un seul DataFrame
        if all_results:
            combined_data = pd.concat(all_results.values()).reset_index(drop=True)
            
            # Traiter les salaires
            if 'salary' in combined_data.columns:
                combined_data['salary_numeric'] = combined_data['salary'].apply(extract_salary)
                # S'assurer que salary_numeric est bien numérique
                combined_data = ensure_numeric(combined_data, 'salary_numeric')
            
            # Créer une colonne de date de publication unifiée
            if 'publication_date' in combined_data.columns:
                try:
                    combined_data['publication_date'] = pd.to_datetime(combined_data['publication_date'], errors='coerce')
                except:
                    pass
            
            # Enregistrer les résultats combinés
            combined_filename = f"results_{job_title.replace(' ', '_')}_{location.replace(' ', '_')}.json"
            combined_data.to_json(combined_filename, orient='records', indent=2)
            
            # Stocker dans all_results.csv pour comparaisons futures
            if os.path.exists("all_results.csv"):
                existing_data = pd.read_csv("all_results.csv")
                # Assurer que les colonnes numériques sont correctement typées
                if 'salary_numeric' in existing_data.columns:
                    existing_data = ensure_numeric(existing_data, 'salary_numeric')
                full_data = pd.concat([existing_data, combined_data])
                full_data.to_csv("all_results.csv", index=False)
            else:
                combined_data.to_csv("all_results.csv", index=False)
            
            # Afficher les résultats
            st.subheader(f"📊 Résultats du scraping ({len(combined_data)} offres)")
            
            # Afficher les statistiques par source si plusieurs sources ont été utilisées
            if len(all_results) > 1:
                sources_stats = combined_data['source'].value_counts().reset_index()
                sources_stats.columns = ['Source', 'Nombre d\'offres']
                
                st.write("#### Répartition des offres par source")
                st.bar_chart(sources_stats.set_index('Source'))
            
            # Onglets pour voir les résultats par source ou combinés
            if len(all_results) > 1:
                tab1, tab2 = st.tabs(["📑 Toutes les offres", "🔄 Comparaison des sources"])
            else:
                tab1, tab2 = st.tabs(["📑 Toutes les offres", "📊 Analyse"])
            
            with tab1:
                # Add search filter
                search_query = st.text_input("🔍 Filtrer les résultats:", "")
                if search_query:
                    filtered_data = combined_data[combined_data.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)]
                    st.dataframe(filtered_data, use_container_width=True)
                    st.info(f"{len(filtered_data)} offres correspondant aux critères sur {len(combined_data)} au total")
                else:
                    st.dataframe(combined_data, use_container_width=True)
            
            with tab2:
                if len(all_results) > 1:
                    # Afficher des statistiques comparatives entre les sources
                    st.write("#### Comparaison des plateformes de recrutement")
                    
                    # 1. Répartition des types de contrat par source
                    if 'contract_type' in combined_data.columns:
                        contract_by_source = combined_data.groupby(['source', 'contract_type']).size().reset_index()
                        contract_by_source.columns = ['Source', 'Type de contrat', 'Nombre']
                        
                        contract_pivot = contract_by_source.pivot(
                            index='Source', 
                            columns='Type de contrat', 
                            values='Nombre'
                        ).fillna(0)
                        
                        st.write("**Types de contrats proposés par source**")
                        st.dataframe(contract_pivot, use_container_width=True)
                        st.bar_chart(contract_pivot)
                    
                    # 2. Comparaison des entreprises qui recrutent le plus
                    if 'company_name' in combined_data.columns:
                        st.write("**Top entreprises qui recrutent par source**")
                        
                        for source, data in all_results.items():
                            with st.expander(f"Top 10 entreprises sur {source}"):
                                company_counts = data['company_name'].value_counts().reset_index().head(10)
                                company_counts.columns = ['Entreprise', 'Nombre d\'offres']
                                st.dataframe(company_counts, hide_index=True, use_container_width=True)
                    
                    # 3. Si les salaires sont disponibles, comparer les salaires moyens
                    if 'salary_numeric' in combined_data.columns and combined_data['salary_numeric'].notna().any():
                        # Assurer que c'est un nombre
                        combined_data = ensure_numeric(combined_data, 'salary_numeric')
                        
                        salary_by_source = combined_data.groupby('source')['salary_numeric'].agg(
                            ['mean', 'median', 'min', 'max', 'count']
                        ).reset_index()
                        
                        salary_by_source.columns = ['Source', 'Moyenne', 'Médiane', 'Minimum', 'Maximum', 'Nb offres avec salaire']
                        
                        st.write("**Comparaison des salaires entre sources**")
                        st.dataframe(salary_by_source, hide_index=True, use_container_width=True)
                        
                        st.write("**Salaire moyen par source**")
                        st.bar_chart(salary_by_source.set_index('Source')['Moyenne'])
                    
                    # 4. Comparer les exigences de missions ou qualifications si disponible
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Localisation des offres par source**")
                        location_by_source = combined_data.groupby(['source', 'location']).size().reset_index()
                        location_by_source.columns = ['Source', 'Localisation', 'Nombre']
                        
                        # Prendre les 5 premières localisations pour chaque source
                        top_locations = []
                        for source in all_results.keys():
                            source_data = location_by_source[location_by_source['Source'] == source]
                            top_source_locations = source_data.sort_values('Nombre', ascending=False).head(5)
                            top_locations.append(top_source_locations)
                        
                        top_locations_df = pd.concat(top_locations)
                        st.dataframe(top_locations_df, hide_index=True, use_container_width=True)
                    
                    with col2:
                        st.write("**Postes les plus fréquents par source**")
                        if 'job_title' in combined_data.columns:
                            job_by_source = combined_data.groupby(['source', 'job_title']).size().reset_index()
                            job_by_source.columns = ['Source', 'Poste', 'Nombre']
                            
                            # Prendre les 5 premiers postes pour chaque source
                            top_jobs = []
                            for source in all_results.keys():
                                source_data = job_by_source[job_by_source['Source'] == source]
                                top_source_jobs = source_data.sort_values('Nombre', ascending=False).head(5)
                                top_jobs.append(top_source_jobs)
                            
                            top_jobs_df = pd.concat(top_jobs)
                            st.dataframe(top_jobs_df, hide_index=True, use_container_width=True)
                else:
                    # Réutiliser le code d'analyse existant
                    # Créer un tableau de bord avancé
                    st.subheader("📈 Analyse des offres d'emploi")
                    
                    # Première ligne d'analyses côte à côte
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Types de contrats**")
                        if 'contract_type' in combined_data.columns:
                            contract_type_count = combined_data['contract_type'].value_counts().reset_index()
                            contract_type_count.columns = ['Type de contrat', 'Nombre']
                            
                            # Afficher graphique et tableau
                            st.bar_chart(contract_type_count.set_index('Type de contrat'))
                            st.dataframe(contract_type_count, hide_index=True, use_container_width=True)
                    
                    with col2:
                        st.write("**Répartition géographique**")
                        if 'location' in combined_data.columns:
                            location_count = combined_data['location'].value_counts().reset_index()
                            location_count.columns = ['Localisation', 'Nombre']
                            
                            # Limiter aux 10 premières régions pour lisibilité
                            top_locations = location_count.head(10)
                            st.bar_chart(top_locations.set_index('Localisation'))
                            st.dataframe(top_locations, hide_index=True, use_container_width=True)
            
            # Créer un tableau de bord avancé
            st.subheader("📈 Analyse des offres d'emploi")
            
            # Première ligne d'analyses côte à côte
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Types de contrats**")
                contract_type_count = combined_data['contract_type'].value_counts().reset_index() if 'contract_type' in combined_data.columns else pd.DataFrame()
                if not contract_type_count.empty:
                    contract_type_count.columns = ['Type de contrat', 'Nombre']
                    
                    # Afficher graphique et tableau
                    st.bar_chart(contract_type_count.set_index('Type de contrat'))
                    st.dataframe(contract_type_count, hide_index=True, use_container_width=True)
            
            with col2:
                st.write("**Répartition géographique**")
                location_count = combined_data['location'].value_counts().reset_index() if 'location' in combined_data.columns else pd.DataFrame()

            # Bouton pour télécharger les résultats
            st.download_button(
                "⬇️ Télécharger les résultats en JSON",
                data=open(combined_filename, "rb"),
                file_name=f"jobsniffer_{job_title}_{location}.json"
            )
        else:
            st.error("Aucune donnée n'a été récupérée.")

# Ajouter un onglet pour comparer les résultats
st.subheader("🔍 Comparaison des recherches")
if os.path.exists("all_results.csv"):
    all_data = pd.read_csv("all_results.csv")
    
    # Assurer que les colonnes numériques sont correctement typées
    all_data = ensure_numeric(all_data, 'salary_numeric')
    
    # Générer les options de comparaison
    job_titles = sorted(all_data['job_title'].unique().tolist()) if 'job_title' in all_data.columns else []
    locations = sorted(all_data['location'].unique().tolist()) if 'location' in all_data.columns else []
    sources = sorted(all_data['source'].dropna().unique().tolist()) if 'source' in all_data.columns else []
    
    # Type de comparaison
    compare_options = ["Par région", "Par intitulé de poste"]
    if len(sources) > 1:
        compare_options.append("Par source")
    
    compare_type = st.radio("Mode de comparaison:", compare_options)
    
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
            # S'assurer que salary_numeric est numérique
            filtered_data = ensure_numeric(filtered_data, 'salary_numeric')
                
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
    
    elif compare_type == "Par intitulé de poste":
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
            # S'assurer que salary_numeric est numérique
            filtered_data = ensure_numeric(filtered_data, 'salary_numeric')
            
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
                    
                    fig = px.box(
                        filtered_data.dropna(subset=['salary_numeric']), 
                        x='job_title', 
                        y='salary_numeric',
                        title="Distribution des salaires par poste",
                        labels={"job_title": "Intitulé du poste", "salary_numeric": "Salaire"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.write("Erreur lors de la génération du box plot:", str(e))
                    
    elif compare_type == "Par source":
        # Code pour comparer par source
        pass
