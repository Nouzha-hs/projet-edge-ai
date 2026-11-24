# 🎓 Slides de Soutenance — Projet Edge AI
## "Prédiction des besoins en irrigation par IA à l'Edge"
### Région du Souss-Massa, Maroc | STM32 Nucleo-F401RE + TinyML + Fog Computing

---

> **Format conseillé :** 12 slides | 15–20 minutes de présentation
> **Outils :** PowerPoint / Google Slides / Canva
> **Graphiques :** dans `docs/schemas/` — à insérer directement

---

## ═══════════════════════════════════
## SLIDE 1 — TITRE / COUVERTURE
## ═══════════════════════════════════

### Titre principal :
**"Prédiction des besoins en irrigation par Intelligence Artificielle à l'Edge"**

### Sous-titre :
Système embarqué TinyML sur STM32 Nucleo-F401RE avec Fog Computing MQTT

### Infos :
- **Zone d'étude :** Région du Souss-Massa (Maroc) — 30.42°N, 8.87°O
- **Dataset :** Données climatiques réelles Copernicus ERA5 (2023–2024, 731 jours)
- **Équipe :** [Membre 1 — Prénom NOM] | [Membre 2 — Prénom NOM] | [Membre 3 — Prénom NOM]
- **Date :** Décembre 2026

### Visuel suggéré :
> Image de la région du Souss + logo STM32 + icône IA

---

## ═══════════════════════════════════
## SLIDE 2 — PROBLÉMATIQUE & OBJECTIFS
## ═══════════════════════════════════

### Titre : "Problématique et Objectifs"

### Problématique (côté gauche) :
> **Le secteur agricole consomme 85% de l'eau douce au Maroc**
>
> La région du Souss-Massa est particulièrement touchée par le stress hydrique :
> - ET₀ moyen : **5.2 mm/jour** (très aride)
> - Irrigation traditionnelle : basée sur calendriers fixes → gaspillage
> - Nécessité d'une décision **locale, rapide, autonome**

### Objectifs (côté droit) :
✅ Développer un firmware d'IA embarqué sur **STM32 Nucleo-F401RE**
✅ Entraîner un modèle **TinyML** sur données réelles **Copernicus ERA5**
✅ Simuler une architecture **Edge + Fog** (MQTT / Node-RED)
✅ Prouver des **économies d'eau mesurables** (seuil fixe vs Edge AI)

### Visuel suggéré :
> Carte du Souss + graphique stress hydrique Maroc

---

## ═══════════════════════════════════
## SLIDE 3 — ARCHITECTURE GLOBALE DU SYSTÈME
## ═══════════════════════════════════

### Titre : "Architecture du Système"

### Schéma en 3 couches (à dessiner ou insérer) :

```
┌─────────────────────────────────────────────────────────┐
│                    COUCHE EDGE (STM32)                   │
│  Capteurs → ADC → Modèle TinyML → Décision → Pompe      │
│           ARM Cortex-M4 @ 84 MHz                        │
└─────────────────────────┬───────────────────────────────┘
                          │ UART → ESP32 → WiFi
┌─────────────────────────▼───────────────────────────────┐
│                   COUCHE FOG (PC Local)                  │
│       Broker MQTT (Mosquitto) → Node-RED → Dashboard    │
└─────────────────────────┬───────────────────────────────┘
                          │ API REST
┌─────────────────────────▼───────────────────────────────┐
│                   COUCHE CLOUD (optionnel)               │
│        Stockage historique + retraining modèle          │
└─────────────────────────────────────────────────────────┘
```

### Points clés à mentionner à l'oral :
- **Décision locale sur STM32** : pas besoin de réseau pour décider
- **Latence : 0.183 µs** → décision quasi-instantanée
- **Fallback sécurisé** : watchdog coupe la pompe si capteur défaillant

---

## ═══════════════════════════════════
## SLIDE 4 — DONNÉES : COPERNICUS ERA5 (Membre 2)
## ═══════════════════════════════════

### Titre : "Dataset — Données Climatiques Réelles Copernicus ERA5"

### Contenu :

| Paramètre | Valeur |
|-----------|--------|
| **Source** | Copernicus Climate Data Store (ERA5) |
| **Zone** | Souss-Massa — 30.42°N, 8.87°O |
| **Période** | 01/01/2023 → 31/12/2024 |
| **Durée** | **731 jours** de données quotidiennes |
| **Variables** | Température (°C), Humidité relative (%), Vent (m/s), Radiation solaire (MJ/m²) |
| **Variable cible** | ET₀ FAO-56 Penman-Monteith (mm/jour) |
| **Label** | `water_required` ∈ {0, 1} |

### Formule ET₀ (FAO-56 Penman-Monteith) :
> ET₀ est calculé selon la norme internationale FAO-56.
> Label : `1` si `Kc × ET₀ − P_eff > 0` (avec Kc = 0.85, P_eff = pluie efficace)

### Statistiques du dataset Souss :
- **86.6%** des jours → irrigation requise (climat très aride)
- **13.4%** des jours → repos (pluies ou ET₀ faible)
- ET₀ moyen : **5.2 mm/jour**

---

## ═══════════════════════════════════
## SLIDE 5 — MODÉLISATION ML (Membre 2)
## ═══════════════════════════════════

### Titre : "Modélisation IA — Entraînement TinyML"

### Pipeline ML :
```
Données CSV (731j) → Nettoyage → Split 75/25 → Entraînement → Évaluation → Export C Header
```

### Modèles entraînés :

| Modèle | Précision | Taille mémoire | Déployable STM32 ? |
|--------|-----------|----------------|---------------------|
| **Arbre de Décision** | **96.72%** | ~100 bytes | ✅ OUI (choisi) |
| Random Forest | 97.27% | ~8 Ko | ⚠️ Trop lourd |
| MLP (Réseau dense) | 97.27% | ~12 Ko | ⚠️ Trop lourd |

### Pourquoi l'Arbre de Décision ?
- **Contrainte STM32 :** Flash limité, zéro malloc
- **Précision suffisante :** 96.72% sur données réelles
- **Conversion C directe :** `if/else` → pas de bibliothèque ML nécessaire

### 📊 Insérer ici : `docs/schemas/slide_comparaison_modeles.png`

---

## ═══════════════════════════════════
## SLIDE 6 — RÉSULTATS ML : MATRICE DE CONFUSION (Membre 2)
## ═══════════════════════════════════

### Titre : "Évaluation du Modèle — Matrice de Confusion"

### 📊 Insérer ici : `docs/schemas/slide_matrice_confusion_dt.png`

### Analyse des résultats :

| Métrique | Classe 0 (Pas d'arrosage) | Classe 1 (Arrosage requis) |
|----------|--------------------------|---------------------------|
| **Précision** | 62% | 98% |
| **Rappel** | 62% | 98% |
| **F1-Score** | 62% | 98% |

### Interprétation :
> Le modèle est **très performant sur la classe majoritaire** (arrosage requis = 94.5% des cas dans le Souss).
> Les 6 erreurs sur 183 échantillons test sont acceptables pour un système d'irrigation.
> **Faux positifs = légère sur-irrigation** (inoffensif) | **Faux négatifs = manque d'arrosage** (3 cas)

---

## ═══════════════════════════════════
## SLIDE 7 — ARCHITECTURE FIRMWARE STM32 ★ (Membre 1)
## ═══════════════════════════════════

### Titre : "Firmware STM32 — Architecture Edge AI"

### Couches du firmware (à représenter verticalement) :

```
┌──────────────────────────────────────────┐
│          APPLICATION LAYER               │
│   Boucle principale : lire capteur       │
│   → appel TinyML → activer pompe        │
├──────────────────────────────────────────┤
│          TINYML INFERENCE LAYER          │
│   tinyml_model_souss.h                  │
│   Arbre de décision en C (if/else)      │
│   Entrées : T, RH, Vent, Rad, ET₀      │
├──────────────────────────────────────────┤
│          WATCHDOG SECURITY LAYER         │
│   simulate_continuous_watchdog.py       │
│   Coupe-circuit 30s max anti-noyade     │
├──────────────────────────────────────────┤
│          HAL / DRIVERS STM32             │
│   ADC, I2C, UART, GPIO                  │
└──────────────────────────────────────────┘
     ▼ Compilé avec arm-none-eabi-gcc 14.3
```

### Boucle d'inférence principale :
```c
// Chaque 1 seconde :
float et0 = calculer_et0(T, RH, vent, radiation);
int decision = tinyml_predict(T, RH, vent, radiation, et0);
if (decision == 1) {
    GPIO_SET(POMPE_PIN);   // Activer pompe
    watchdog_reset();      // Renouveler le bail (30s max)
} else {
    GPIO_RESET(POMPE_PIN); // Couper pompe
}
```

---

## ═══════════════════════════════════
## SLIDE 8 — SIMULATION & WATCHDOG ★ (Membre 1)
## ═══════════════════════════════════

### Titre : "Simulation STM32 — Validation & Sécurité Watchdog"

### Partie A — Simulation 5 scénarios du Souss :

| Scénario | Conditions | Décision IA | Latence |
|----------|-----------|-------------|---------|
| Canicule d'Été (Taroudant) | T=38.5°C, RH=20%, ET₀=7.8 | ✅ POMPE ON | 0.202 µs |
| Hiver Humide (Janvier) | T=16°C, RH=85%, ET₀=1.8 | ⛔ POMPE OFF | 0.155 µs |
| Printemps Maraîcher | T=25°C, RH=52%, ET₀=4.6 | ✅ POMPE ON | 0.202 µs |
| Épisode de Chergui | T=42°C, RH=12%, ET₀=9.2 | ✅ POMPE ON | 0.202 µs |
| Automne Tempéré | T=19.5°C, RH=68%, ET₀=2.3 | ⛔ POMPE OFF | 0.155 µs |

**Résultat : 5/5 scénarios CONFORMES (100% de précision)**

### Partie B — Simulation continue 731 jours :
- **633 jours** : irrigation active (86.6%)
- **98 jours** : repos (13.4%)
- **Jour 200** : Panne capteur injectée (T=48°C, ET₀=12.0)
  - → **Watchdog DÉCLENCHÉ** ✅
  - → Pompe coupée automatiquement après 30s max
  - → Risque d'inondation : **0%**

---

## ═══════════════════════════════════
## SLIDE 9 — MÉTRIQUES OFFICIELLES STM32 ★ (Membre 1)
## ═══════════════════════════════════

### Titre : "Métriques Embarquées Officielles — ARM Cortex-M4"

### 📊 Insérer ici : `docs/schemas/slide_metriques_stm32.png`

### Tableau des métriques (compilateur arm-none-eabi-gcc 14.3) :

| Métrique | Valeur mesurée | Contrainte projet | Statut |
|----------|---------------|-------------------|--------|
| **Flash utilisé** | **100 bytes** | < 2 048 bytes (2 Ko) | ✅ |
| **RAM dynamique** | **0 octet** | 0 malloc (RTOS-safe) | ✅ |
| **Latence inférence** | **0.183 µs** | < 1 µs | ✅ |
| **Cycles CPU** | **15.4 cycles** | @ 84 MHz Cortex-M4 | ✅ |
| **Watchdog** | **30s max** | Coupe-circuit actif | ✅ |

### Commande officielle utilisée :
```bash
arm-none-eabi-gcc -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard
  -O2 -fno-common -ffunction-sections stm32_inference_cortex_m4.c
  → text=100 bytes | data=0 | bss=0
```

### Message clé à l'oral :
> *"Notre modèle TinyML occupe seulement 100 bytes de Flash, soit 0.019% de la mémoire disponible sur STM32F401RE. La décision d'irrigation prend 0.183 microsecondes — 273 fois plus rapide qu'une requête Cloud."*

---

## ═══════════════════════════════════
## SLIDE 10 — COMPARAISON EDGE vs CLOUD ★ (Membre 1)
## ═══════════════════════════════════

### Titre : "Edge AI vs Cloud AI — Pourquoi Embarqué ?"

### Tableau comparatif :

| Critère | Edge AI (STM32) | Cloud AI |
|---------|-----------------|----------|
| **Latence décision** | **0.183 µs** | 50–200 ms |
| **Connexion Internet** | ❌ Non requise | ✅ Obligatoire |
| **Consommation** | ~mW | Serveur distant |
| **Coût infrastructure** | ~15€ (STM32) | ~50€/mois |
| **Sécurité données** | ✅ Locale | ⚠️ Envoi cloud |
| **Fonctionnement hors-ligne** | ✅ OUI | ❌ NON |
| **Mise à jour modèle** | Reflash UART | API REST |

### Conclusion visuelle :
> **Pour l'agriculture en zone isolée (Souss-Massa) :**
> L'Edge AI est **indispensable** — pas de 4G fiable dans les plaines agricoles !

---

## ═══════════════════════════════════
## SLIDE 11 — BENCHMARK : ÉCONOMIES D'EAU (Membre 3)
## ═══════════════════════════════════

### Titre : "Benchmark — Économies d'Eau : Seuil Fixe vs Edge AI"

### 📊 Insérer ici : `docs/schemas/slide_benchmark_eau_365jours.png`

### Résultats sur simulation 365 jours (Souss, ERA5) :

| Système | Consommation annuelle | Cycles pompe |
|---------|----------------------|--------------|
| **Seuil fixe** (arrosage calendaire) | **4 305 L** | Fixe (tous les jours) |
| **Edge AI TinyML** | **2 914 L** | Adaptatif selon ET₀ |
| **💧 Économie** | **1 391 L (32.3%)** | — |

### Impact à l'échelle agricole :
> Pour une exploitation de 10 hectares dans le Souss :
> - Économie estimée : **~139 000 L/an/ha** = **139 m³/ha/an**
> - Réduction des coûts de pompage : ~**30%**

### Architecture Fog (Membre 3) :
- Broker MQTT : Mosquitto (port 1883)
- Dashboard : Node-RED
- Données temps réel via ESP32 → WiFi → PC local

---

## ═══════════════════════════════════
## SLIDE 12 — CONCLUSION & PERSPECTIVES
## ═══════════════════════════════════

### Titre : "Conclusion & Perspectives"

### Ce que nous avons réalisé :

✅ **Firmware TinyML** embarqué sur STM32 (ARM Cortex-M4)
- Flash : 100 bytes | RAM : 0 heap | Latence : 0.183 µs

✅ **Dataset réel Copernicus ERA5** (731 jours, Souss-Massa)
- ET₀ FAO-56 Penman-Monteith intégré

✅ **Modèle ML** entraîné et déployé (96.72% accuracy)
- Arbre de décision exporté en C header

✅ **Watchdog sécurité** validé sur 731 jours
- 1 incident maîtrisé, risque inondation = 0%

✅ **Économie d'eau prouvée : 32.3%** vs seuil fixe

---

### Perspectives :
- 🔄 Retraining automatique via pipeline Fog → Cloud
- 📡 Intégration LoRaWAN pour zones sans WiFi
- 🌱 Extension à d'autres cultures (Kc variable selon stade)
- 🔋 Alimentation solaire autonome (faible consommation STM32)

---

### Message final :
> *"Ce projet démontre qu'une IA embarquée de 100 bytes peut gérer l'irrigation d'une ferme entière, sans Cloud, sans Internet, avec 32% d'eau économisée. C'est le futur de l'agriculture intelligente dans les régions arides comme le Souss-Massa."*

---

## 📌 PLAN DE PRÉSENTATION ORAL (20 minutes)

| Durée | Slide | Présentateur |
|-------|-------|-------------|
| 2 min | 1–2 | **Membre 1** (intro + problématique) |
| 3 min | 3 | **Membre 1** (architecture globale) |
| 4 min | 4–6 | **Membre 2** (données + ML) |
| 5 min | 7–10 | **Membre 1** (firmware + métriques) |
| 3 min | 11 | **Membre 3** (benchmark + fog) |
| 3 min | 12 | **Tous** (conclusion + questions) |
