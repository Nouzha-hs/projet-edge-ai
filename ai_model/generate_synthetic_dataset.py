#!/usr/bin/env python3
"""
Générateur de dataset d'irrigation réaliste pour démarrer le projet en simulation.
Permet à l'équipe de développer et tester la chaîne IA sans attendre le dataset du professeur.
Dès que le professeur fournit le dataset final, il suffira de remplacer ce fichier !
"""

import numpy as np
import pandas as pd
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "irrigation_dataset_simulation.csv")

def generate_irrigation_dataset(n_samples=2500, random_state=42):
    np.random.seed(random_state)
    
    # 1. Variables temporelles
    hours = np.random.randint(0, 24, size=n_samples)
    
    # 2. Conditions météo de l'air
    # Température plus chaude l'après-midi (12h-17h)
    temp_base = 20 + 8 * np.sin((hours - 6) * np.pi / 12)
    temperature = temp_base + np.random.normal(0, 3, size=n_samples)
    temperature = np.clip(temperature, 10, 42)
    
    # Humidité de l'air inversement corrélée à la température
    hum_air_base = 70 - 25 * np.sin((hours - 6) * np.pi / 12)
    humidity_air = hum_air_base + np.random.normal(0, 6, size=n_samples)
    humidity_air = np.clip(humidity_air, 20, 95)
    
    # Pression atmosphérique (hPa)
    pressure = np.random.normal(1013.25, 6, size=n_samples)
    
    # Rayonnement solaire estimé (W/m²), nul la nuit
    solar_rad = np.where((hours >= 6) & (hours <= 20), 
                         800 * np.sin((hours - 6) * np.pi / 14) + np.random.normal(0, 50, size=n_samples), 
                         0)
    solar_rad = np.clip(solar_rad, 0, 1000)

    # 3. Humidité du sol actuelle (%)
    soil_moisture = np.random.uniform(10, 75, size=n_samples)

    # 4. Décision d'arrosage (Label cible : 0 = Pas d'arrosage, 1 = Arrosage requis)
    # Logique agronomique réaliste :
    # - Si sol < 22% : arrosage presque toujours obligatoire
    # - Si sol > 45% : pas d'arrosage
    # - Entre 22% et 45% : dépend de la météo (température élevée + fort ensoleillement = arrosage préventif)
    # - Éviter d'arroser en plein soleil (11h-15h) si le sol n'est pas critique (évaporation inutile)
    evaporation_risk = (temperature * 0.4) + (solar_rad * 0.03) - (humidity_air * 0.2)
    
    need_water = (
        (soil_moisture < 22) |
        ((soil_moisture < 35) & (evaporation_risk > 12) & ((hours < 10) | (hours > 17))) |
        ((soil_moisture < 28) & (temperature > 30))
    ).astype(int)

    df = pd.DataFrame({
        "hour": hours,
        "temperature_c": np.round(temperature, 2),
        "humidity_air_pct": np.round(humidity_air, 2),
        "pressure_hpa": np.round(pressure, 1),
        "solar_radiation_wm2": np.round(solar_rad, 1),
        "soil_moisture_pct": np.round(soil_moisture, 2),
        "water_required": need_water
    })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[OK] Dataset généré avec succès ({n_samples} échantillons) : {OUTPUT_PATH}")
    print("Distribution des classes (Besoin en eau) :")
    print(df["water_required"].value_counts(normalize=True).round(3))
    return df

if __name__ == "__main__":
    generate_irrigation_dataset()
