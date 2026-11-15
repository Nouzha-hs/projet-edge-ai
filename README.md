# Projet Edge AI : Système d'Irrigation Intelligent (TinyML + Fog Computing)

Ce projet implémente un système d'irrigation autonome basé sur l'intelligence artificielle embarquée (**TinyML / Edge AI**) sur microcontrôleur **STM32**, relié à une passerelle **Fog (ESP32/ESP8266 + Mosquitto/Node-RED/Grafana)**.

---

## 🏗️ Architecture Globale

```
+-------------------------------------------------------------+
|                     EDGE (STM32)                           |
|                                                             |
|  [Capteur Humidité Sol v1.2] ---> ADC                       |
|  [DHT22 / BME280 (Air T/H)]  ---> GPIO / I2C                |
|  [Niveau d'eau (Optionnel)]  ---> ADC / GPIO                |
|                                                             |
|  => Inférence TinyML locale (TensorFlow Lite / X-CUBE-AI)   |
|  => Décision automatique & sécurité anti-inondation         |
|  => Commande Relais 5V -> Pompe à eau 5V/12V (alim externe) |
+------------------------------+------------------------------+
                               |
                        UART (TX / RX)
                               v
+-------------------------------------------------------------+
|              PASSERELLE FOG (ESP32 / ESP8266)               |
|                                                             |
|  - Réception des trames UART du STM32                       |
|  - Encapsulation JSON & publication WiFi / MQTT             |
+------------------------------+------------------------------+
                               |
                           WiFi / MQTT
                               v
+-------------------------------------------------------------+
|                SERVEUR FOG / PC / RASPBERRY PI              |
|                                                             |
|  - Broker MQTT (Eclipse Mosquitto)                          |
|  - Tableau de bord & monitoring (Node-RED ou Grafana)       |
|  - Historisation des données pour réentraînement            |
+-------------------------------------------------------------+
```

---

## 📁 Structure du Répertoire

```text
Projet Edge/
├── docs/                 # Documentation, schémas de câblage, notes de soutenance
├── data/                 # Datasets bruts, logs d'acquisition, données Kaggle
├── ai_model/             # Scripts Python, notebooks Jupyter, entraînement & conversion TFLite / C
├── firmware_stm32/       # Code source STM32 (CubeIDE / HAL / Drivers capteurs & modèle IA)
├── esp_gateway/          # Code pour ESP32 / ESP8266 (passerelle UART <-> MQTT)
├── fog_server/           # Configurations MQTT, dashboards Node-RED / Grafana, docker-compose
└── README.md             # Présentation générale du projet
```

---

## 🗓️ Calendrier de Réalisation (5 Semaines)

1. **Semaine 1 : Étude, Architecture & Banc d'essai Hardware**
   - Schéma d'interconnexion (STM32, capteurs, relais, alimentation séparée).
   - Validation unitaire des capteurs (ADC sol, I2C/1-wire température/humidité air).
2. **Semaine 2 : Collecte des Données & Télémétrie**
   - Firmware de collecte périodique (sol, air, horodatage, statut arrosage).
   - Enregistrement des données sur banc d'essai ou intégration d'un dataset public (Kaggle).
3. **Semaine 3 : Modélisation IA (TinyML)**
   - Nettoyage et préparation des données (`pandas`, `scikit-learn`).
   - Entraînement de modèles (Arbre de décision, Random Forest ou Réseau de Neurones dense).
   - Évaluation (Précision, Rappel, F1-score, Matrice de confusion).
4. **Semaine 4 : Déploiement Edge & Intégration Fog**
   - Quantification `int8` et génération du code C (`STM32Cube.AI` / `TFLite Micro`).
   - Boucle d'inférence autonome sur STM32 avec garde-fou de sécurité temporelle.
   - Pont UART -> ESP32/ESP8266 -> MQTT Broker (Mosquitto) + Dashboard.
5. **Semaine 5 : Benchmarking, Validation & Préparation Soutenance**
   - Comparaison modèle IA vs simple seuil fixe (consommation d'eau, réactivité).
   - Métriques embarquées : temps d'inférence (ms), occupation Flash & RAM, latence Edge vs Cloud.
   - Rédaction du rapport et préparation des 10 à 12 diapositives de soutenance.
