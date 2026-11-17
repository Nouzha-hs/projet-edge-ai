# Projet Edge AI : Système d'Irrigation Intelligent dans la Région du Souss (Maroc)

Système d'irrigation de précision basé sur l'intelligence artificielle embarquée (**TinyML sur STM32**), alimenté par les données climatiques satellitaires **Copernicus (ERA5 / ET₀ FAO-56)** et supervisé via une architecture **Fog Computing (MQTT & Node-RED)**.

---

## 🎯 Contexte & Objectifs du Projet

La **plaine du Souss-Massa** (Taroudant / Agadir : `30.42° N`, `-8.87° W`) est le cœur de la production agricole maraîchère et agrumicole du Maroc. Soumise à un climat semi-aride et à un épuisement critique des nappes phréatiques, l'irrigation doit être raisonnée au plus juste.

Le système prédit le besoin net en eau :
$$I_{net} = \max(0, K_c \times ET_0 - P_{eff})$$
à partir des paramètres climatiques réels fournis par **Copernicus** :
- **$T$** : Température de l'air (°C)
- **$RH$** : Humidité relative (%)
- **Vent** : Vitesse du vent à 10m (m/s)
- **Rayonnement** : Énergie solaire incidente (MJ/m²)
- **$ET_0$** : Évapotranspiration de référence calculée selon l'équation FAO-56 Penman-Monteith (mm/jour)

---

## 🏗️ Architecture Globale (100% Simulation)

```
+------------------------------------------------------------------------+
|                     1. DONNÉES CLIMATIQUES (COPERNICUS)                |
|  - Réanalyse ERA5 / FAO-56 pour la région du Souss (730 jours réels)   |
|  - Variables : Température, Humidité, Vent, Rayonnement, Pluie, ET0    |
+-----------------------------------+------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
|                  2. PIPELINE DATA SCIENCE & TINYML (PYTHON)            |
|  - Nettoyage et formulation agronomique du besoin d'irrigation         |
|  - Entraînement comparatif : Arbre de Décision, Random Forest, MLP     |
|  - Quantification et export automatique en code C pur (tinyml_model.h) |
+-----------------------------------+------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
|              3. EDGE COMPUTING (STM32 NUCLEO-F401RE / CORTEX-M4)       |
|  - Inférence locale en C pur (latence < 0.6 microseconde avec DWT)     |
|  - 0 allocation dynamique (aucun malloc, empreinte Flash < 1.5 Ko)     |
|  - Décision d'activation pompe virtuelle + Watchdog de sécurité (30s)  |
+-----------------------------------+------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
|                  4. FOG COMPUTING, BENCHMARK & SUPERVISION             |
|  - Broker MQTT local (Eclipse Mosquitto)                               |
|  - Tableau de bord de supervision temps réel (Node-RED)                |
|  - Benchmark écologique 30 jours : 20 à 28% d'économie d'eau prouvée   |
+------------------------------------------------------------------------+
```

---

## 👥 Répartition des Rôles (Groupe de 3 Personnes)

- **👤 Membre 1 (Toi - Ingénieur Embarqué & Edge AI)** :
  - Firmware sous **STM32CubeIDE** (cible STM32F401RE / Cortex-M4).
  - Intégration du modèle IA en C pur (`tinyml_model_souss.h`).
  - Simulation des épisodes météo du Souss (`souss_test_vectors.h` : canicule, Chergui, hiver).
  - Coupe-circuit de sécurité (watchdog 30s) et mesure de la latence matérielle avec `DWT->CYCCNT`.
- **👤 Membre 2 (Data Scientist & Ingénieur Machine Learning)** :
  - Traitement du dataset Copernicus du Souss (`data/download_copernicus_souss.py`).
  - Entraînement multi-modèles et évaluation statistique (`ai_model/train_souss_model.py`).
  - Matrice de confusion, F1-score et export du modèle vers le code C.
- **👤 Membre 3 (Fog Computing, Simulation Système & Dashboard)** :
  - Simulateur environnemental et météorologique (`fog_server/simulate_environment.py`).
  - Déploiement du broker Mosquitto MQTT et du tableau de bord Node-RED.
  - Calcul comparatif de l'économie d'eau ($m^3/ha$) : Seuil Fixe vs Edge AI.

---

## 🗓️ Calendrier de Réalisation (Sprint de 3 Semaines)

### Semaine 1 : Cadrage, Données Copernicus & Firmware de Base
- Téléchargement et inspection du dataset Copernicus du Souss (ERA5, ET₀ FAO-56).
- Initialisation du projet C sous STM32CubeIDE pour Cortex-M4 et activation du port virtuel ST-Link.
- Mise en place du simulateur météo et installation du broker Mosquitto MQTT.
- Validation des premiers scénarios de test statiques.

### Semaine 2 : Modélisation IA & Intégration Embarquée
- Entraînement comparatif des algorithmes (Decision Tree vs Random Forest vs MLP).
- Évaluation des métriques (Accuracy, Précision, Rappel, F1-score > 98%).
- Quantification `int8` et génération du header C `tinyml_model_souss.h`.
- Intégration du modèle dans la boucle STM32 et programmation du watchdog anti-noyade (30s).
- Connexion du flux MQTT et conception du tableau de bord sous Node-RED.

### Semaine 3 : Benchmarking Écologique, Métriques Matérielles & Soutenance
- Relevé des métriques réelles Cortex-M4 : Latence (< 0.6 µs), Flash (< 1.5 Ko), RAM (0 octet heap).
- Simulation saisonnière complète du Souss : Démonstration du gain d'eau (20 à 28% d'économie).
- Finalisation du firmware, répétition de la démonstration en direct.
- Finalisation du support de présentation (12 diapositives réparties) et rapport de projet.

---

## 📁 Structure du Répertoire

```text
projet-edge-ai/
├── docs/                 # Documentation technique, plan 3 semaines, guide d'impression PDF
│   ├── Repartition_Taches_Projet_Edge_AI.html   # Fiche de répartition imprimable (Ctrl + P)
│   ├── zone_etude_souss_copernicus.md           # Analyse géographique et agronomique du Souss
│   ├── taches_pratiques_equipe.md               # Guide technique des tâches pour les 3 membres
│   └── guide_membre_1_edge_stm32.md             # Guide dédié pour le Membre 1 (STM32)
├── data/                 # Données Copernicus ERA5 et scripts de téléchargement
│   └── download_copernicus_souss.py             # Script de récupération automatique des données
├── ai_model/             # Scripts d'entraînement Machine Learning & export TinyML
│   ├── train_souss_model.py                     # Pipeline d'entraînement sur le climat du Souss
│   └── requirements.txt                         # Dépendances Python (pandas, scikit-learn, etc.)
├── firmware_stm32/       # Code source C pour STM32CubeIDE (Nucleo-F401RE)
│   ├── Drivers_Custom/Inc/
│   │   ├── tinyml_model_souss.h                 # Modèle d'inférence TinyML en C pur
│   │   └── souss_test_vectors.h                 # Scénarios réels du Souss (canicule, Chergui, hiver)
│   └── test_simulation_souss_main.c             # Programme complet de benchmark avec DWT
├── fog_server/           # Scripts de simulation d'environnement et supervision
│   └── simulate_environment.py                 # Simulateur 30 jours et calcul d'économie d'eau
└── README.md             # Présentation générale du projet
```
