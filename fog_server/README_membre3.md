# Membre 3 : Fog Computing, Supervision & Simulation Système

Projet Edge AI / TinyML : irrigation intelligente dans la région du Souss (Agadir / Taroudant, 30.42°N, -8.87°W).

Cette partie simule l'environnement du Souss, supervise le système en temps réel (MQTT + Node-RED) et mesure l'économie d'eau de la décision Edge AI (basée sur l'ET₀) par rapport à un seuil fixe.

## 1. Architecture

```
simulateur_souss.py --MQTT souss/sensors--> Mosquitto --> Node-RED (dashboard + decisions.csv)
                                                |
                                                +--> bridge_serial_mqtt.py --serie--> STM32 (Membre 1)
STM32 / décision --"PUMP=ON/OFF"--> bridge --MQTT souss/pump--> simulateur (la pompe arrose) / dashboard
```

| Topic MQTT | Sens | Contenu |
|---|---|---|
| `souss/sensors` | simulateur → broker | JSON : `hour, t, rh, wind, rad, et0, soil, pump, scenario` |
| `souss/pump` | bridge / dashboard → simulateur | `ON` ou `OFF` |
| `souss/stm32/log` | bridge → broker | lignes de log de la STM32 (si carte) |

## 2. Fichiers

| Fichier | Rôle |
|---|---|
| `mosquitto.conf` | Broker MQTT (port 1883, accès anonyme local) |
| `simulateur_souss.py` | Météo du Souss : scénarios canicule (38°C), Chergui (42°C), matinée d'hiver (16°C), assèchement du sol, pompe |
| `bridge_serial_mqtt.py` | Pont série STM32 ↔ MQTT (mode test `--fake-stm32` sans carte) |
| `flow_souss.json` | Flow Node-RED (Dashboard 2.0) : jauge température, courbes ET₀ et humidité du sol, état de la pompe, interrupteur manuel, log CSV |
| `decisions.csv` | Journal des mesures et de l'état de la pompe |
| `benchmark_eau.py` | Benchmark offline seuil fixe vs Edge AI sur une saison |
| `benchmark_graphiques.png`, `resultats_benchmark.csv` | Résultats du benchmark |

## 3. Lancer la démo (Windows)

Chaque commande dans une fenêtre séparée, depuis le dossier `membre3`.

```
pip install paho-mqtt pyserial matplotlib

1) "C:\Program Files\Mosquitto\mosquitto.exe" -c mosquitto.conf -v
2) node-red                                   (puis ouvrir http://localhost:1880, importer flow_souss.json, Déployer)
3) python bridge_serial_mqtt.py --fake-stm32  (ou --port COM3 avec la carte)
4) python simulateur_souss.py --scenario chergui --interval 1 --days 3 --soil0 35
5) Dashboard : http://localhost:1880/dashboard
```

Options utiles du simulateur : `--scenario canicule|chergui|hiver`, `--interval` (secondes réelles par pas de 30 min simulées), `--days`, `--soil0` (humidité initiale), `--dry-run` (sans MQTT).

## 4. Benchmark écologique

```
python benchmark_eau.py                 # saison de 90 jours, graine 42
python benchmark_eau.py --seed 7 --days 120
```

Les deux stratégies tournent sur la même météo :

- **A, seuil fixe** : pompe ON si humidité < 30 %, OFF à partir de 40 %, à toute heure.
- **B, Edge AI** : besoin net `I_net = max(0, Kc × ET₀ − P_eff)` avec Kc = 0.85, estimé à partir de l'ET₀ de la veille ; arrosage à l'aube (03h-07h) jusqu'à un niveau qui permet de finir la journée vers 30 % ; sécurité si humidité < 20 %.

### Résultats (90 jours, graine 42)

| | A : seuil fixe | B : Edge AI |
|---|---|---|
| Eau pompée, **avec** pertes d'application | 6020 m³/ha | 5120 m³/ha |
| **Économie** | | **15.0 %** |
| Eau pompée, **sans** pertes d'application | 4940 m³/ha | 4900 m³/ha |
| **Économie** | | **0.8 %** |
| Humidité moyenne du sol | 36.5 % | 38.1 % |
| Temps en stress hydrique (< 20 %) | 0 % | 0 % |

Autres graines testées (1, 7, 123) : économie de 11.7 % à 14.9 % avec pertes, 0 % à 0.4 % sans pertes.

## 5. Hypothèses et limites (à citer dans le rapport)

- **L'économie de 15 % vient du modèle de pertes d'application** (évaporation et dérive du vent, plus fortes en plein soleil, vent sec et chaleur). Sans ces pertes, les deux stratégies consomment pratiquement la même eau : le besoin de la culture (Kc × ET₀) est identique. Ce modèle de pertes est une hypothèse du simulateur, pas une mesure.
- **L'objectif de 20 à 28 % du cahier des charges n'est pas atteint** par ce modèle (15 % au mieux, avec pertes).
- Paramètres estimés, à remplacer par des valeurs réelles si disponibles : débit de pompe 4 mm/h, 1 mm = 2 % d'humidité, 1 mm = 10 m³/ha, pas de pluie.
- **L'ET₀ est une approximation simplifiée**, pas l'ET₀ FAO-56 issue de Copernicus ERA5 (Membre 2). À remplacer quand elle est disponible.
- **Pas de carte STM32 physique** dans cette démonstration : la décision est produite par `fake_decision` du bridge (règle simple), pas par le modèle TinyML de Membre 1. Les valeurs de latence et de mémoire de la STM32 ne sont pas mesurées ici.
- Le format des messages série (`T=..,RH=..` / `PUMP=ON`) est un protocole par défaut, à confirmer avec Membre 1.

## 6. Dépendances avec les autres membres

- **Membre 1 (STM32)** : confirmer le port COM, le baud (115200 par défaut), le format des lignes reçues et de la décision renvoyée.
- **Membre 2 (Data/IA)** : fournir l'ET₀ Copernicus et le besoin net pour remplacer l'ET₀ approximative du simulateur et du benchmark.
