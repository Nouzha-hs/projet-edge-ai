#!/usr/bin/env python3
"""
Script de téléchargement automatique des données climatiques Copernicus (ERA5 / FAO-56)
pour la région du SOUSS (Maroc) - Coordonnées : Taroudant / Plaine du Souss (30.42°N, -8.87°W).

Paramètres récupérés :
- Température moyenne, max, min (°C)
- Humidité relative moyenne (%)
- Vitesse du vent à 10m (m/s)
- Rayonnement solaire global (MJ/m²)
- Précipitations cumulées (mm)
- ET0 FAO-56 : Évapotranspiration de référence (mm/jour)

Sortie : data/copernicus_souss_climate_data.csv
"""

import os
import json
import urllib.request
import pandas as pd
import numpy as np

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "copernicus_souss_climate_data.csv")

# 1. Définition géographique de la zone du Souss (Maroc)
LATITUDE = 30.42     # Taroudant / Plaine agricole du Souss
LONGITUDE = -8.87
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"

def fetch_souss_copernicus_data():
    print("==================================================================")
    print("  TÉLÉCHARGEMENT DES DONNÉES CLIMATIQUES COPERNICUS (ERA5)")
    print(f"  Zone d'étude : Région du Souss (Lat: {LATITUDE}°N, Lon: {LONGITUDE}°W)")
    print(f"  Période      : du {START_DATE} au {END_DATE} (731 jours)")
    print("==================================================================")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={LATITUDE}&longitude={LONGITUDE}&"
        f"start_date={START_DATE}&end_date={END_DATE}&"
        f"daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
        f"relative_humidity_2m_mean,precipitation_sum,et0_fao_evapotranspiration,"
        f"wind_speed_10m_max,shortwave_radiation_sum&"
        f"timezone=Africa%2FCasablanca"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-EdgeAI-Agent/1.0"})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw_data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERREUR] Échec du téléchargement en ligne : {e}")
        return None

    daily = raw_data.get("daily", {})
    if not daily:
        print("[ERREUR] Données journalières absentes de la réponse.")
        return None

    df = pd.DataFrame({
        "date": daily["time"],
        "temp_mean_c": daily["temperature_2m_mean"],
        "temp_max_c": daily["temperature_2m_max"],
        "temp_min_c": daily["temperature_2m_min"],
        "humidity_mean_pct": daily["relative_humidity_2m_mean"],
        "wind_speed_max_ms": daily["wind_speed_10m_max"],
        "solar_radiation_mj": daily["shortwave_radiation_sum"],
        "precipitation_mm": daily["precipitation_sum"],
        "et0_fao_mm": daily["et0_fao_evapotranspiration"]
    })

    # Nettoyage des éventuelles valeurs nulles
    df = df.dropna()

    # 2. Calcul agronomique pour le Souss (Culture maraîchère / Agrumes)
    # Coefficient cultural moyen Kc = 0.85
    KC_SOUSS = 0.85
    df["etc_mm"] = np.round(df["et0_fao_mm"] * KC_SOUSS, 2)
    
    # Précipitations efficaces (P_eff = 80% de la pluie si P > 2mm, sinon 0)
    df["p_eff_mm"] = np.where(df["precipitation_mm"] > 2.0, df["precipitation_mm"] * 0.8, 0.0)
    
    # Besoin net en irrigation (mm/jour)
    df["irrigation_need_mm"] = np.clip(df["etc_mm"] - df["p_eff_mm"], 0, None)
    df["irrigation_need_mm"] = np.round(df["irrigation_need_mm"], 2)

    # 3. Label de classification pour l'IA embarquée (STM32)
    # 1 = Arrosage requis (besoin net >= 2.0 mm/jour)
    # 0 = Pas d'arrosage (pluie suffisante ou faible évapotranspiration)
    df["water_required"] = (df["irrigation_need_mm"] >= 2.0).astype(int)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n[SUCCÈS] Dataset sauvegardé ({len(df)} jours) : {OUTPUT_CSV}")
    print("\n--- Statistiques Climat du Souss (2023-2024) ---")
    print(f"Température moyenne : {df['temp_mean_c'].mean():.1f} °C (Min: {df['temp_min_c'].min():.1f} °C, Max: {df['temp_max_c'].max():.1f} °C)")
    print(f"Humidité moyenne    : {df['humidity_mean_pct'].mean():.1f} %")
    print(f"ET0 FAO moyenne     : {df['et0_fao_mm'].mean():.2f} mm/jour (Max estival: {df['et0_fao_mm'].max():.2f} mm/jour)")
    print(f"Pluviométrie totale : {df['precipitation_mm'].sum():.1f} mm/an en moyenne")
    print("\nRépartition du besoin en arrosage :")
    print(df["water_required"].value_counts(normalize=True).round(3))

    return df

if __name__ == "__main__":
    fetch_souss_copernicus_data()
