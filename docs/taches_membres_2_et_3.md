# Feuille de Route et Tâches : Membre 2 & Membre 3
**Projet :** Système d'Irrigation Intelligente Edge AI (Région du Souss-Massa)  
**Référentiel Matériel / Firmware :** STM32 Nucleo-F401RE (Cortex-M4 @ 84 MHz)

---

## 📌 Rappel de ce qui a déjà été réalisé par le Membre 1 (Systèmes Embarqués & Edge)

Le Membre 1 a finalisé l'infrastructure embarquée et les tests de validation :
1. **Pilotes Matériels C purs (`Drivers_Custom/`)** :
   - Capteur capacitif de sol (ADC1 12 bits sur broche PA0).
   - Actionneur relais pompe (GPIO Output sur PA5 avec circuit anti-rebond).
   - Watchdog matériel & sécurité temporelle (coupure automatique d'urgence après 30s max en cas d'anomalie capteur).
2. **Modèle C TinyML (`tinyml_model_souss.h`)** :
   - Arbre de décision optimisé exporté directement en C ANSI.
   - Empreinte Flash : **100 octets** (sur 512 Ko).
   - Empreinte RAM : **0 octet dynamique** (aucun `malloc`, buffer statique ultra-sécurisé).
   - Latence d'inférence : **0.183 microseconde** (15.4 cycles CPU @ 84 MHz).
3. **Validation & Simulation (`firmware_stm32/simulator/`)** :
   - Test des 5 scénarios climatiques extrêmes du Souss (Canicule Taroudant, Chergui, Hiver humide, etc.) : **100% validé**.
   - Test en continu sur 731 jours (2023-2024) avec injection de panne capteur : **Watchdog déclenché avec succès**, risque d'inondation **0%**.

---

## 👨‍💻 MEMBRE 2 : Data Science, Climatologie & Modélisation IA

### 🎯 Mission Principale
Exploiter les données climatiques réelles de la région du Souss-Massa, justifier mathématiquement les besoins hydriques (Évapotranspiration $ET_0$), concevoir et comparer plusieurs architectures d'apprentissage automatique (Scikit-Learn, TFLite Micro), et documenter la matrice de choix pour l'embarqué.

### 📋 Liste Détaillée des Tâches à Réaliser

- [ ] **Tâche 2.1 — Analyse et Validation du Dataset Climatique Copernicus ERA5**
  - **Source :** Données horaires/journalières ERA5 sur les coordonnées GPS du Souss ($30.42^\circ\text{N}, -8.87^\circ\text{W}$) de 2023 à 2024 (731 jours).
  - **Variables analysées :** Température de l'air (°C), Humidité relative (%), Vitesse du vent à 2m (m/s), Rayonnement solaire global ($MJ/m^2/jour$).
  - **Livrable :** Script ou Notebook Jupyter avec graphiques de saisonnalité (histogrammes, profils mensuels de température et d'humidité du Souss).

- [ ] **Tâche 2.2 — Justification de la Formule FAO-56 Penman-Monteith ($ET_0$)**
  - Documenter le calcul standardisé international FAO-56 de l'évapotranspiration de référence ($ET_0$ en mm/jour) :
    $$ET_0 = \frac{0.408 \Delta (R_n - G) + \gamma \frac{900}{T + 273} u_2 (e_s - e_a)}{\Delta + \gamma (1 + 0.34 u_2)}$$
  - Comparer l'impact d'un épisode de **Chergui** (vent chaud d'est, humidité < 15%, $ET_0 > 8\text{ mm/jour}$) par rapport à une journée d'hiver normale.
  - **Livrable :** Section théorique dans le rapport expliquant pourquoi $ET_0$ est l'indicateur universel de la soif des cultures maraîchères et d'agrumes.

- [ ] **Tâche 2.3 — Étude Comparative Multi-Modèles**
  - Entraîner et comparer formellement au moins 3 modèles sur la prédiction du besoin d'arrosage :
    1. **Arbre de Décision (Decision Tree)** : Léger, interprétable, facilement traduisible en C pur.
    2. **Forêt Aléatoire (Random Forest)** : Ensemble d'arbres, haute précision mais empreinte mémoire plus lourde.
    3. **Réseau de Neurones Perceptron Multicouche (MLP)** : Approche deep learning classique.
  - Calculer pour chaque modèle : Précision (Accuracy), Rappel (Recall), Score F1 et Matrice de Confusion.
  - **Livrable :** Tableau comparatif justifiant pourquoi l'Arbre de Décision (96.72% de précision) est le compromis optimal pour un microcontrôleur STM32 sans OS par rapport au surcoût mémoire du MLP/Random Forest.

- [ ] **Tâche 2.4 — Pipeline de Quantisation et d'Export C / TinyML**
  - Valider l'export automatique du modèle Python (`ai_model/train_souss_model.py`) vers le fichier header C (`tinyml_model_souss.h`).
  - Documenter la reproductibilité : commande `python ai_model/train_souss_model.py`.
  - Fournir les visualisations générées (`docs/schemas/slide_comparaison_modeles.png` et `docs/schemas/slide_matrice_confusion_dt.png`) pour les slides de soutenance.

---

## 🌐 MEMBRE 3 : Architecture IoT / Fog Computing, Intégration & Tableau de Bord

### 🎯 Mission Principale
Concevoir la couche passerelle locale (Fog Node / Raspberry Pi), assurer la communication avec les nœuds Edge STM32 (MQTT / LoRaWAN), mettre en place le tableau de bord de supervision pour l'agriculteur et quantifier l'impact économique et environnemental (benchmark d'économie d'eau).

### 📋 Liste Détaillée des Tâches à Réaliser

- [ ] **Tâche 3.1 — Définition de l'Architecture Hybride Edge-Fog-Cloud**
  - Schématiser le flux des données :
    - **Niveau 1 (Edge - STM32)** : Inférence ultra-rapide (0.18 µs), prise de décision locale autonome en cas de coupure réseau, pilotage direct de la vanne/pompe.
    - **Niveau 2 (Fog - Passerelle locale / Raspberry Pi)** : Réception des télémétries, historisation locale en base de données (SQLite/InfluxDB), détection des alertes de défaillance.
    - **Niveau 3 (Cloud / Dashboard)** : Vue d'ensemble multi-parcelles, rapports hebdomadaires d'irrigation.
  - **Livrable :** Schéma d'architecture réseau (format SVG/PNG ou Mermaid) intégré au dossier `docs/`.

- [ ] **Tâche 3.2 — Modélisation du Protocole de Télémétrie (Payload JSON)**
  - Définir le format compact des messages envoyés par la carte STM32 vers la passerelle :
    ```json
    {
      "node_id": "STM32_SOUSS_01",
      "timestamp": 1719748800,
      "temp_c": 38.5,
      "hum_pct": 20.0,
      "et0_mm": 7.8,
      "soil_moisture_pct": 18.5,
      "pump_state": 1,
      "latency_us": 0.183,
      "safety_watchdog": "OK"
    }
    ```
  - Documenter le choix du protocole de transport (MQTT pour réseau Wi-Fi/Ethernet ou LoRaWAN pour les zones rurales isolées sans couverture 4G).

- [ ] **Tâche 3.3 — Benchmark d'Économie d'Eau et Analyse ROI**
  - Exploiter les résultats du script de simulation 365 jours (`docs/schemas/slide_benchmark_eau_365jours.png`) :
    - **Système classique (Horloge fixe / Timer traditionnel)** : Consommation de **4 305 Litres/an/parcelle** (arrosage aveugle même s'il pleut ou si le sol est humide).
    - **Système Edge AI (Arbre de Décision TinyML)** : Consommation de **2 914 Litres/an/parcelle**.
    - **Bilan d'économie :** **1 391 Litres économisés par an et par zone testée**, soit **32.3% de réduction d'eau**.
  - Rédiger l'extrapolation pour une exploitation moyenne du Souss (ex: 5 à 10 hectares d'agrumes) : calcul des mètres cubes d'eau préservés et des économies sur la facture énergétique de pompage.

- [ ] **Tâche 3.4 — Maquette ou Dashboard de Supervision (Streamlit ou Grafana)**
  - Développer un mini script de tableau de bord (ex: `dashboard_fog/app.py` en Streamlit ou Dash) affichant :
    1. État de la pompe en temps réel (ON/OFF).
    2. Courbe d'humidité du sol et indicateur $ET_0$.
    3. Alerte Watchdog visuelle si la pompe fonctionne plus de 30 secondes en continu.
    4. Compteur d'eau cumulée et pourcentage d'économie d'eau réalisé.
  - **Livrable :** Script fonctionnel + captures d'écran de l'interface pour la soutenance.

---

## 🤝 Matrice de Synchronisation Globale pour la Soutenance

| Étape de la Démonstration | Rôle Membre 1 (Edge) | Rôle Membre 2 (IA & Data) | Rôle Membre 3 (Fog & IoT) |
| :--- | :--- | :--- | :--- |
| **Introduction & Contexte** | Présentation de la contrainte temps réel embarqué | Présentation des défis hydriques du Souss & Données Copernicus | Présentation des limites du Cloud dans les fermes isolées |
| **Cœur Technique** | Code C, Pilotes ADC/GPIO, Watchdog 30s | Théorie $ET_0$ FAO-56 & Entraînement de l'Arbre 96.72% | Protocole de communication & Architecture Edge/Fog |
| **Démonstration en Direct** | Exécution de la simulation STM32 (5 scénarios + coupure Watchdog) | Explication des matrices de confusion et des scores | Affichage du Dashboard et télémétries en temps réel |
| **Conclusion & Résultats** | 100 octets Flash, 0 RAM, 0.18 µs de latence | Justification de la robustesse mathématique | **32.3% d'eau économisée** (1 391 L/an/zone) & Éco-responsabilité |
