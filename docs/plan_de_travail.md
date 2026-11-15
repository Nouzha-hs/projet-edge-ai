# Plan de Travail & Spécifications du Projet

Voir également le document interactif complet dans l'espace de suivi Antigravity.

## Structure du Projet

```text
Projet Edge/
├── docs/                 # Documentation, schémas de câblage, notes de soutenance
├── data/                 # Datasets bruts, logs d'acquisition, données Kaggle
├── ai_model/             # Scripts Python, notebooks Jupyter, modèles TFLite / Cube.AI
├── firmware_stm32/       # Projets STM32CubeIDE, drivers capteurs & code C
├── esp_gateway/          # Firmware ESP32 / ESP8266 (pont UART -> WiFi/MQTT)
├── fog_server/           # Configurations MQTT Mosquitto, flows Node-RED, dashboard
└── README.md             # Vue d'ensemble du projet
```

## Étapes Clés
1. **Semaine 1** : Montage & test unitaire des capteurs sur STM32.
2. **Semaine 2** : Firmware de collecte & dataset (local + Kaggle).
3. **Semaine 3** : Entraînement et validation du modèle d'IA (Python).
4. **Semaine 4** : Conversion STM32Cube.AI / TFLite Micro, inférence embarquée et passerelle Fog MQTT.
5. **Semaine 5** : Benchmarks, mesures (latence, Flash/RAM) et préparation de la soutenance.
