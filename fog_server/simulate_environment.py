#!/usr/bin/env python3
"""
Simulateur d'Environnement & Benchmark Écologique (Membre 3).
Simule 30 jours de conditions météo et compare :
1. Système Traditionnel (Seuil fixe : arrose dès que l'humidité < 25%)
2. Système Edge AI (Inférence locale intelligente prenant en compte météo et évapotranspiration)

Génère les statistiques d'économies d'eau pour la soutenance et le rapport final.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_PLOT = os.path.join(os.path.dirname(__file__), "..", "docs", "schemas", "benchmark_water_savings.png")

def run_simulation(days=30):
    np.random.seed(101)
    hours_total = days * 24

    # Profils météo simulés sur 30 jours
    t = np.arange(hours_total)
    hour_of_day = t % 24
    
    # Cycles de température journalière (avec vagues de chaleur occasionnelles)
    heatwave = 5 * np.sin(2 * np.pi * t / (24 * 7)) # Variation hebdomadaire
    temperature = 22 + 7 * np.sin((hour_of_day - 6) * np.pi / 12) + heatwave + np.random.normal(0, 1.5, hours_total)
    temperature = np.clip(temperature, 12, 38)
    
    # Humidité de l'air
    humidity_air = 65 - 20 * np.sin((hour_of_day - 6) * np.pi / 12) + np.random.normal(0, 4, hours_total)
    humidity_air = np.clip(humidity_air, 25, 90)

    # Initialisation de l'humidité du sol pour les 2 systèmes
    soil_fixed = np.zeros(hours_total)
    soil_ai = np.zeros(hours_total)
    
    soil_fixed[0] = 50.0 # Sol humide au départ
    soil_ai[0] = 50.0

    water_used_fixed = 0.0 # Litres d'eau
    water_used_ai = 0.0
    pump_triggers_fixed = 0
    pump_triggers_ai = 0

    fixed_threshold = 25.0 # Seuil fixe classique

    for i in range(1, hours_total):
        # Évaporation naturelle basée sur la température et l'humidité de l'air
        evap_rate = (temperature[i] * 0.025) - (humidity_air[i] * 0.005) + 0.1
        evap_rate = max(0.05, evap_rate)

        # 1. Système Seuil Fixe
        soil_fixed[i] = soil_fixed[i-1] - evap_rate
        if soil_fixed[i] < fixed_threshold:
            # Déclenchement arrosage fixe (ex: +25% d'humidité, coût 5L)
            soil_fixed[i] += 25.0
            water_used_fixed += 5.0
            pump_triggers_fixed += 1

        # 2. Système Edge AI
        soil_ai[i] = soil_ai[i-1] - evap_rate
        
        # Logique IA : arrose préventivement le matin/soir si sol moyen et forte chaleur annoncée,
        # ou arrose immédiatement si sol critique (< 20%)
        is_cool_hour = (hour_of_day[i] <= 8) or (hour_of_day[i] >= 19)
        ai_decision = False
        
        if soil_ai[i] < 20.0:
            ai_decision = True # Urgence absolue
        elif (soil_ai[i] < 32.0) and is_cool_hour and (temperature[i] > 24):
            ai_decision = True # Arrosage nocturne optimal sans évaporation directe

        if ai_decision:
            # L'IA dose l'arrosage : arrosage d'appoint de 3.5L suffisant
            soil_ai[i] += 20.0
            water_used_ai += 3.5
            pump_triggers_ai += 1

    # Bilan chiffré
    savings_liters = water_used_fixed - water_used_ai
    savings_pct = (savings_liters / water_used_fixed) * 100.0

    print("===========================================================")
    print(f"   RÉSULTATS DU BENCHMARK SUR {days} JOURS SIMULÉS")
    print("===========================================================")
    print(f"Système Seuil Fixe : {water_used_fixed:.1f} L consommés | {pump_triggers_fixed} cycles pompe")
    print(f"Système Edge AI    : {water_used_ai:.1f} L consommés | {pump_triggers_ai} cycles pompe")
    print(f"--> ÉCONOMIE D'EAU : {savings_liters:.1f} Litres ({savings_pct:.1f}% de gain !)")
    print("===========================================================")

    # Génération du graphique comparatif pour la soutenance
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    ax1.plot(t[:168], soil_fixed[:168], label="Seuil Fixe Traditionnel", color="#ef4444", linewidth=1.8)
    ax1.plot(t[:168], soil_ai[:168], label="Edge AI Intelligent", color="#10b981", linewidth=1.8)
    ax1.axhline(fixed_threshold, color="#94a3b8", linestyle="--", label="Seuil Fixe (25%)")
    ax1.set_ylabel("Humidité Sol (%)")
    ax1.set_title(f"Dynamique de l'Humidité du Sol sur 7 Jours (Économie globale : {savings_pct:.1f}%)", fontweight="bold")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    ax2.plot(t[:168], temperature[:168], color="#f59e0b", label="Température (°C)")
    ax2.set_xlabel("Temps (Heures)")
    ax2.set_ylabel("Température Air (°C)")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(OUTPUT_PLOT), exist_ok=True)
    plt.savefig(OUTPUT_PLOT, dpi=200)
    print(f"[OK] Graphique comparatif enregistré dans : {OUTPUT_PLOT}")

if __name__ == "__main__":
    run_simulation(30)
