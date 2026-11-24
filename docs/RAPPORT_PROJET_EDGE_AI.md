# RAPPORT TECHNIQUE DE PROJET
## Conception et Déploiement d'un Système d'Irrigation Intelligente Autonome basé sur l'Edge AI (TinyML) sur Cible STM32 dans la Région du Souss-Massa

---

**Filière / Spécialité :** Systèmes Embarqués, Intelligence Artificielle & IoT  
**Projet :** Irrigation Intelligente Edge AI (Projet Edge)  
**Zone d'Étude Géographique :** Plaine du Souss-Massa, Maroc ($30.42^\circ\text{N}, -8.87^\circ\text{W}$)  
**Plateforme Matérielle :** Carte STMicroelectronics STM32 Nucleo-F401RE (ARM Cortex-M4 @ 84 MHz)  
**Dépôt GitHub Officiel :** `https://github.com/Nouzha-hs/projet-edge-ai.git`  
**Date :** Novembre 2026  

---

## RÉSUMÉ EXÉCUTIF (ABSTRACT)

### Version Française
Face aux crises hydriques répétées et à l'épuisement des nappes phréatiques dans la région agricole stratégique du Souss-Massa au Maroc, ce projet présente la conception, l'optimisation et la validation d'un système cyber-physique d'irrigation intelligente entièrement autonome basé sur l'**Edge AI (TinyML)**. Contrairement aux approches connectées au Cloud dépendantes d'une connectivité réseau instable et coûteuse, la prise de décision est déportée au plus près des cultures sur un microcontrôleur **STM32 Nucleo-F401RE** (ARM Cortex-M4 avec FPU matériel). 

Le modèle d'arbre de décision embarqué, directement traduit en langage C ANSI sans allocation dynamique, a été entraîné sur **731 jours de relevés climatiques réels (2023-2024) issus du satellite Copernicus ERA5** couplés au calcul de l'évapotranspiration de référence ($ET_0$ Penman-Monteith FAO-56). Le firmware développé affiche une empreinte mémoire de seulement **100 octets de Flash** (0.019% de la mémoire disponible), **0 octet de RAM dynamique** (`malloc`), et une latence d'inférence ultra-rapide de **0.183 microseconde** (15.4 cycles CPU @ 84 MHz). Un coupe-circuit matériel (Watchdog 30s) garantit un risque d'inondation de 0.0% en cas de défaillance capteur. Les benchmarks simulés sur 365 jours démontrent une **réduction de la consommation d'eau de 32.3%** (1 391 litres économisés par an et par zone de culture par rapport aux minuteries traditionnelles).

### English Abstract
Addressing severe water scarcity and aquifer depletion in the Souss-Massa agricultural region (Morocco), this project delivers an autonomous, real-time smart irrigation cyber-physical system powered by **Edge AI (TinyML)** deployed on a **STM32 Nucleo-F401RE** microcontroller (ARM Cortex-M4 @ 84 MHz with hardware FPU). Bypassing fragile cloud dependency, decisions are executed strictly on-device. An optimized decision tree model synthesized in pure ANSI C was trained on **731 days of real Copernicus ERA5 climate telemetry (2023–2024)** coupled with FAO-56 Penman-Monteith Reference Evapotranspiration ($ET_0$). The firmware achieves a footprint of **100 bytes of Flash**, **0 dynamic RAM allocation**, and a benchmarked inference latency of **0.183 µs** (15.4 clock cycles). An embedded 30-second hardware-grade watchdog prevents root flooding in the event of sensor anomalies. 365-day benchmarks establish a **32.3% reduction in irrigation water consumption** (1,391 L/year saved per sector), demonstrating high resilience, extreme energy efficiency, and direct economic viability for arid-zone agriculture.

---

## 1. INTRODUCTION ET CONTEXTE

### 1.1 Contexte Régional du Souss-Massa
La région du Souss-Massa représente le premier bassin d'exportation d'agrumes et de primeurs du Royaume du Maroc. Cependant, son climat aride à semi-aride est caractérisé par une pluviométrie erratique (< 200 mm/an) et des phénomènes météorologiques extrêmes tels que le **Chergui** (vent chaud et sec du Sahara provoquant des températures supérieures à 42°C et une humidité relative inférieure à 15%). La surexploitation des nappes phréatiques impose une rationalisation drastique des volumes d'arrosage.

### 1.2 Limites des Systèmes d'Irrigation Conventionnels
1. **Minuteries aveugles (Fixed-Schedule Timers) :** La majorité des parcelles sont équipées de programmateurs horaires statiques. Ils arrosent à heures fixes, qu'il pleuve ou que le sol soit déjà saturé, générant un gaspillage moyen estimé à 30-40% des volumes d'eau pompés.
2. **Vulnérabilité des solutions 100% Cloud :** Les solutions IoT basées sur le transfert systématique des données brutes vers un serveur distant souffrent des coupures de réseau fréquentes en zone rurale (zones blanches), d'un coût récurrent prohibitif et d'une surconsommation énergétique des émetteurs radio.

### 1.3 Objectifs du Projet
* Développer une solution d'**Edge AI frugale** capable d'arbitrer localement le besoin d'arrosage sans accès Internet requis.
* Atteindre une précision de décision supérieure à 95% tout en minimisant l'empreinte mémoire et la latence sur microcontrôleur bas coût.
* Intégrer un système de sécurité matérielle (Watchdog) éliminant tout risque de noyade des cultures.
* Quantifier avec rigueur le volume d'eau préservé sur une année complète d'exploitation.

---

## 2. ARCHITECTURE GLOBALE DU SYSTÈME

Le système repose sur une architecture cyber-physique à 3 niveaux interconnectés :

```
       +-------------------------------------------------------------+
       |                  NIVEAU 3 : CLOUD & SUPERVISION             |
       |  - Visualisation multi-parcelles à l'échelle régionale      |
       |  - Sauvegarde historique long terme & tableaux de bord      |
       +------------------------------^------------------------------+
                                      | (Connexion périodique / 4G)
       +------------------------------v------------------------------+
       |                  NIVEAU 2 : FOG COMPUTING                   |
       |  - Passerelle locale de ferme (Raspberry Pi / Passerelle)   |
       |  - Broker MQTT local & passerelle LoRaWAN                   |
       |  - Agrégation télémétrique et alertes SMS / locales         |
       +------------------------------^------------------------------+
                                      | (Liaison série / LoRa P2P / GPIO)
       +------------------------------v------------------------------+
       |                  NIVEAU 1 : EDGE AI (NOTRE CŒUR)           |
       |  - Microcontrôleur STM32 Nucleo-F401RE (Cortex-M4 @ 84MHz)  |
       |  - Inférence TinyML C pur (Arbre de Décision, 0.183 µs)     |
       |  - Pilote ADC 12 bits (Capteur humidité sol sur PA0)        |
       |  - Pilote Relais Électrovanne (GPIO PA5)                    |
       |  - Coupe-circuit de sécurité Watchdog (30 secondes max)     |
       +-------------------------------------------------------------+
```

---

## 3. DÉVELOPPEMENT EMBARQUÉ ET FIRMWARE STM32 (RÉALISATION MEMBRE 1)

### 3.1 Plateforme Matérielle
* **Microcontrôleur :** STM32F401RET6 (ARM Cortex-M4 32 bits, FPU simple précision, DSP).
* **Fréquence d'Horloge :** 84 MHz (générée par PLL interne).
* **Mémoires disponibles :** 512 Ko Flash, 96 Ko SRAM.
* **Interfaces utilisées :**
  * `ADC1_IN0` sur broche **PA0** : Échantillonnage analogique du capteur capacitif de sol (résolution 12 bits, plage $0 - 4095$).
  * `GPIO_PIN_5` sur broche **PA5** : Commande logique du relais de puissance de l'électrovanne avec isolation galvanique.

### 3.2 Modèle TinyML Embarqué (`tinyml_model_souss.h`)
Pour garantir une consommation nulle de mémoire dynamique et une exécution déterministe en temps réel dur, le modèle d'intelligence artificielle a été converti en C ANSI pur sous forme d'arbre de décision binaire à branchements optimisés :

```c
#ifndef TINYML_MODEL_SOUSS_H
#define TINYML_MODEL_SOUSS_H

#include <stdint.h>

/* Inférence TinyML ultra-rapide générée pour STM32 Nucleo-F401RE */
static inline uint8_t tinyml_predict_irrigation(float temp_c, float humidity, float et0_mm, float soil_moist_raw) {
    // Seuil principal : Humidité du sol et tension d'évapotranspiration
    if (soil_moist_raw <= 2200.0f) {
        if (et0_mm > 3.2f || temp_c > 28.0f) {
            return 1; // ARROSAGE REQUIS
        }
        return (humidity < 40.0f) ? 1 : 0;
    } else {
        if (et0_mm > 7.0f && humidity < 25.0f) {
            return 1; // DÉROGATION CHERGUI EXTRÊME
        }
        return 0; // PAS D'ARROSAGE (Sol suffisamment humide)
    }
}
#endif
```

### 3.3 Métriques Matérielles Officielles (Compilateur ARM-GCC)
La compilation croisée réalisée avec la chaîne d'outils officielle `arm-none-eabi-gcc 14.3` (`-O3 -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard`) certifie les métriques suivantes :

| Grandeur Technique | Valeur Mesurée | Limite Matérielle STM32 | Taux d'Occupation |
| :--- | :---: | :---: | :---: |
| **Empreinte Flash (Code `.text`)** | **100 octets** | 512 000 octets | **0.019 %** |
| **Empreinte RAM Statique (`.data` + `.bss`)** | **0 octet** | 98 304 octets | **0.000 %** |
| **Allocation Dynamique (`malloc`)** | **0 octet** | Interdite | **Zéro risque de fuite mémoire** |
| **Latence d'Inférence Moyenne** | **0.183 µs** | < 1 000 µs | **15.4 cycles d'horloge CPU** |
| **Temps d'exécution maximum (Worst-Case)** | **0.202 µs** | - | **17 cycles d'horloge** |

### 3.4 Sécurité Industrielle : Coupe-Circuit Watchdog (Anti-Noyade)
En milieu agricole, les pannes de capteurs (arrachement de câble, oxydation, blocage à l'état sec) constituent la cause numéro un des inondations de cultures.
Le firmware intègre une machine à états surveillée par un compteur d'activité maximale :
* **Règle de sécurité :** Tout cycle d'irrigation est physiquement limité à **30 secondes consécutives**.
* **Comportement en cas de blocage :** À $t = 30\text{ s}$, le Watchdog force la broche PA5 à l'état bas (`GPIO_PIN_RESET`), incrémente le registre d'erreur et verrouille la vanne jusqu'à réinitialisation ou diagnostic.
* **Validation empirique :** Lors d'un test continu de 731 jours avec injection d'une panne bloquante au jour 200 (lecture fictive de sécheresse extrême $48^\circ\text{C}, ET_0 = 12\text{ mm/j}$), la coupure d'urgence s'est déclenchée sans faille à 30.0s, maintenant le risque d'inondation à **0.0%**.

---

## 4. MODÉLISATION IA, DATA SCIENCE ET CLIMATOLOGIE (RÉALISATION MEMBRE 2)

### 4.1 Données Satellitaires Copernicus ERA5
L'entraînement du modèle repose sur une extraction rigoureuse du produit réanalysé **Copernicus ERA5** pour la station géographique de Taroudant/Souss ($30.42^\circ\text{N}, -8.87^\circ\text{W}$) du **01/01/2023 au 31/12/2024** (731 journées complètes). Les variables intégrées sont :
* Température moyenne quotidienne ($T_{mean}$, $T_{max}$, $T_{min}$).
* Humidité relative moyenne ($RH$).
* Vitesse du vent normalisée à 2 mètres ($u_2$).
* Rayonnement solaire global incident ($R_s$).

### 4.2 Évapotranspiration de Référence FAO-56 ($ET_0$)
Pour quantifier la demande évaporative de l'atmosphère indépendamment de la culture, le standard international **FAO-56 Penman-Monteith** a été implémenté :

$$ET_0 = \frac{0.408 \Delta (R_n - G) + \gamma \frac{900}{T + 273} u_2 (e_s - e_a)}{\Delta + \gamma (1 + 0.34 u_2)}$$

Où $R_n$ est le rayonnement net, $G$ le flux de chaleur du sol, $T$ la température moyenne de l'air, $u_2$ la vitesse du vent à 2 m, $e_s - e_a$ le déficit de pression de vapeur saturante, $\Delta$ la pente de la courbe de pression de vapeur, et $\gamma$ la constante psychrométrique.

### 4.3 Étude Comparative des Algorithmes
Trois architectures supervisées ont été entraînées et évaluées en validation croisée sur le dataset du Souss (partition 75% entraînement / 25% test) :

| Modèle Testé | Précision Globale (Accuracy) | F1-Score (Classe Arrosage) | Taille Modèle Exporté | Adéquation Cible STM32 |
| :--- | :---: | :---: | :---: | :---: |
| **Forêt Aléatoire (100 arbres)** | 97.27 % | 0.98 | ~85 Ko | Trop volumineux pour ROM |
| **Réseau de Neurones MLP (2 couches)** | 97.27 % | 0.98 | ~140 Ko | Nécessite runtime TFLite Micro |
| **Arbre de Décision (Decision Tree)** | **96.72 %** | **0.98** | **0.10 Ko (100 o)** | **OPTIMAL (Sélectionné)** |

#### Matrice de Confusion de l'Arbre de Décision Embarqué :
* Vrais Négatifs (Sol humide $\rightarrow$ Pas d'arrosage) : **5 / 8** (62.5% de spécificité sur les cas de repos hydrique)
* Faux Positifs : 3
* Faux Négatifs (Manque d'eau non détecté) : **3 / 175** (Seulement 1.7% d'erreur critique)
* Vrais Positifs (Besoin hydrique détecté avec succès) : **172 / 175** (**98.3% de sensibilité**)
* **Score F1 global sur la décision d'irrigation : 0.98**.

---

## 5. FOG COMPUTING, BENCHMARK D'ÉCONOMIE D'EAU & IOT (RÉALISATION MEMBRE 3)

### 5.1 Passerelle Fog et Protocole de Télémétrie
La passerelle locale assure l'interfaçage entre le réseau de microcontrôleurs STM32 répartis sur les parcelles et le serveur de ferme via protocole MQTT. Le message compact JSON transmis après chaque cycle d'évaluation est le suivant :

```json
{
  "device_id": "STM32_F401_SOUSS_01",
  "timestamp": "2024-07-20T14:30:00Z",
  "sensors": {
    "temp_c": 38.5,
    "hum_pct": 20.0,
    "et0_mm": 7.8,
    "soil_raw": 1950
  },
  "edge_decision": {
    "pump_state": 1,
    "latency_us": 0.183,
    "cycles_cpu": 15
  },
  "diagnostics": {
    "watchdog_state": "NOMINAL",
    "flood_risk_pct": 0.0
  }
}
```

### 5.2 Benchmark Comparatif de Consommation d'Eau (365 Jours)
Une simulation comparative stricte a été exécutée sur les données météorologiques journalières réelles d'une année complète dans le Souss :
1. **Système Témoin (Minuterie Classique) :** Déclenchement automatique quotidien fixe (10 minutes/jour sous débit régulé de 1.18 L/min), soit une consommation annuelle brute de **4 305 Litres**.
2. **Système Proposé (Edge AI STM32) :** Déclenchement asservi au croisement de l'humidité du sol réelle et de l'indicateur d'évapotranspiration $ET_0$. Consommation annuelle mesurée de **2 914 Litres**.

```
BILAN D'ÉCONOMIE D'EAU SUR 365 JOURS (PARCELLE TEST) :
---------------------------------------------------------
• Volume Système Classique       : 4 305 Litres
• Volume Système Edge AI STM32   : 2 914 Litres
• ÉCONOMIE HYDRIQUE NETTE        : 1 391 Litres
• POURCENTAGE DE RÉDUCTION       : 32.3 %
```

### 5.3 Extrapolation Économique et Agronomique
À l'échelle d'une exploitation maraîchère moyenne de **10 hectares** dans la plaine de Chtouka :
* L'économie de 32.3% se traduit par une réduction de plusieurs **dizaines de milliers de mètres cubes d'eau pompée**.
* Réduction directe de la facture d'électricité liée au fonctionnement des pompes immergées de forage.
* Préservation de la santé végétale : élimination de l'asphyxie racinaire et des attaques de champignons phytopathogènes causées par l'engorgement d'eau stagnant.

---

## 6. VALIDATION ET TESTS SCÉNARISÉS

Le firmware a été soumis au banc d'épreuves des 5 conditions météorologiques critiques du Souss :

| N° | Scénario Climatique Simulé | Conditions Météo Réelles | Décision IA Attendue | Décision STM32 Mesurée | Latence | Résultat |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **1** | **Canicule d'Été à Taroudant** | $T=38.5^\circ\text{C}, H=20\%, ET_0=7.8\text{ mm/j}$ | POMPE ACTIVE | **POMPE ACTIVE** | 0.202 µs | **CONFORME** |
| **2** | **Journée d'Hiver Humide (Pluies)** | $T=16.0^\circ\text{C}, H=85\%, ET_0=1.8\text{ mm/j}$ | REPOS (OFF) | **REPOS (OFF)** | 0.155 µs | **CONFORME** |
| **3** | **Printemps Maraîcher dans la Plaine**| $T=25.0^\circ\text{C}, H=52\%, ET_0=4.6\text{ mm/j}$ | POMPE ACTIVE | **POMPE ACTIVE** | 0.202 µs | **CONFORME** |
| **4** | **Épisode Extrême de Chergui** | $T=42.0^\circ\text{C}, H=12\%, ET_0=9.2\text{ mm/j}$ | POMPE ACTIVE | **POMPE ACTIVE** | 0.202 µs | **CONFORME** |
| **5** | **Automne Tempéré (Nov.)** | $T=19.5^\circ\text{C}, H=68\%, ET_0=2.3\text{ mm/j}$ | REPOS (OFF) | **REPOS (OFF)** | 0.155 µs | **CONFORME** |

**Taux de succès du banc de validation : 5/5 (100.0%)**.

---

## 7. RÉPARTITION DU TRAVAIL DE L'ÉQUIPE

Le succès du projet repose sur une délimitation précise des responsabilités techniques :

* **Membre 1 — Systèmes Embarqués & Edge AI (Auteur Principal du Firmware) :**
  * Développement des pilotes C de l'ADC1 et du GPIO de la carte STM32 Nucleo-F401RE.
  * Synthèse du modèle TinyML C ANSI et suppression totale des allocations dynamiques.
  * Conception et validation du coupe-circuit matériel Watchdog 30 secondes.
  * Mesure des métriques matérielles (compilateur GCC, cycles d'horloge, latence 0.183 µs).

* **Membre 2 — Data Science, Climatologie & IA :**
  * Pipeline d'acquisition et de nettoyage des 731 jours de données Copernicus ERA5 Souss.
  * Implémentation mathématique de la formule FAO-56 Penman-Monteith ($ET_0$).
  * Entraînement, optimisation hyperparamétrique et benchmarking comparatif (DT vs RF vs MLP).
  * Génération des matrices de confusion et justification théorique du choix de l'arbre.

* **Membre 3 — Fog Computing, IoT & Benchmark Économie d'Eau :**
  * Architecture réseau 3-tiers (Edge, Fog, Cloud) et définition des payloads MQTT/JSON.
  * Conception du tableau de bord de supervision locale pour l'exploitant agricole.
  * Modélisation et calcul du benchmark comparatif d'arrosage sur 365 jours (-32.3% d'eau).
  * Évaluation du retour sur investissement (ROI) et de l'impact agro-écologique.

---

## 8. CONCLUSION ET PERSPECTIVES

Ce projet démontre avec succès la faisabilité et la supériorité opérationnelle de l'**Edge AI frugale** appliquée aux défis critiques de l'agriculture en zone aride. En combinant la rigueur agronomique de la formule FAO-56, la précision de relevés satellitaires Copernicus réels et l'extrême efficacité du microcontrôleur STM32 Cortex-M4, le système permet de :
1. Réduire de **32.3%** le gaspillage d'eau d'irrigation.
2. Garantir une décision locale en **0.183 microseconde** sans dépendance au réseau Internet.
3. Assurer une fiabilité industrielle totale grâce à une empreinte de **100 octets**, l'absence de RAM dynamique et un coupe-circuit Watchdog inviolable.

### Perspectives Futures :
* **Alimentation Autonome (Energy Harvesting) :** Intégration d'un mini-panneau photovoltaïque de 5W et d'un supercondensateur pour rendre le nœud STM32 indéfiniment autonome sur le plan énergétique.
* **Communication LoRa P2P longue portée :** Maillage des nœuds STM32 sur plusieurs kilomètres carrés sans passerelle 4G intermédiaire.
* **Auto-Calibration Saisonnière :** Ajustement dynamique des seuils d'arrosage en fonction du stade phénologique de la culture (germination, floraison, fructification).

---

## 9. DOCUMENTS ET RESSOURCES ASSOCIÉES DANS LE DÉPÔT

* `docs/ARTICLE_EXPLICATIF_PROJET.md` : Vulgarisation détaillée du projet en 9 chapitres accessibles.
* `docs/taches_membres_2_et_3.md` : Guide de répartition des tâches techniques pour les Membres 2 et 3.
* `docs/slides_soutenance_contenu.md` : Script complet des 12 slides pour la présentation orale.
* `docs/schemas/` : Répertoire contenant l'ensemble des graphiques officiels (comparaison modèles, matrice de confusion, benchmark eau 365 jours, métriques STM32).
* `firmware_stm32/Drivers_Custom/Inc/tinyml_model_souss.h` : Code source C du modèle TinyML optimisé pour Cortex-M4.
* `firmware_stm32/simulator/` : Scripts de simulation et bancs d'épreuve du firmware et du Watchdog.
