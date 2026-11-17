# Zone d'Étude & Données Copernicus : Région du Souss-Massa (Maroc)

## 1. Contexte Géographique & Agronomique de la Zone d'Étude

La **région du Souss-Massa** (plaine du Souss, reliant Agadir, Taroudant et Oulad Teima) est le cas d'application idéal pour un projet d'Edge AI :
- **Rôle agricole stratégique** : C'est le premier bassin de production maraîchère (tomates, agrumes) et d'exportation agricole du Maroc.
- **Problématique hydrique critique** : Climat aride à semi-aride (précipitations faibles < 200 mm/an, fortes températures estivales > 40°C, déficit hydrique structurel).
- **Enjeu pour l'IA** : L'eau est pompée dans des nappes phréatiques surexploitées. Réduire l'irrigation de 20 à 30% grâce au calcul temps réel de l'évapotranspiration a un impact économique et environnemental majeur.

### Coordonnées Géographiques Retenues :
- **Point central (Plaine agricole du Souss / Taroudant - Oulad Teima)** :
  - **Latitude** : `30.42° N`
  - **Longitude** : `-8.87° W`
  - **Altitude moyenne** : ~250 m
- **Bounding Box Souss-Massa** :
  - Nord : `31.0° N`, Sud : `29.5° N`
  - Ouest : `-9.9° W`, Est : `-8.0° W`

---

## 2. Paramètres Climatiques Copernicus (ERA5 / AgERA5 / FAO-56)

L'évapotranspiration de référence ($ET_0$) représente la quantité d'eau évaporée par le sol et transpirée par un couvert végétal de référence (gazon bien arrosé).

Les variables climatiques d'entrée (Features de l'IA) sont :
1. **$T_{mean}$, $T_{max}$, $T_{min}$ (°C)** : Température de l'air à 2 mètres.
2. **$RH$ (%)** : Humidité relative moyenne de l'air.
3. **$u_2$ (m/s)** : Vitesse du vent à 2m (ou 10m ramenée à 2m).
4. **$R_s$ ($MJ/m^2$ ou $W/m^2$)** : Rayonnement solaire global incident (Shortwave Radiation).
5. **$P$ (mm)** : Précipitations journalières cumulées.
6. **$ET_0$ (mm/jour)** : Évapotranspiration de référence calculée selon la formule officielle **FAO-56 Penman-Monteith** :

$$ET_0 = \frac{0.408 \Delta (R_n - G) + \gamma \frac{900}{T + 273} u_2 (e_s - e_a)}{\Delta + \gamma (1 + 0.34 u_2)}$$

---

## 3. Logique de Décision : Calcul du Besoin en Irrigation ($I_{net}$)

Pour une culture type du Souss (ex: Agrumes ou Tomates sous serre/plein champ) :
- **Coefficient cultural ($K_c$)** : ~ 0.70 à 1.05 selon le stade végétatif.
- **Évapotranspiration de la culture** : $ET_c = K_c \times ET_0$ (mm/jour).
- **Précipitations efficaces ($P_{eff}$)** : Pluie réellement absorbée par le sol.
- **Besoin net d'irrigation journalier** : 
  $$I_{net} = \max(0, ET_c - P_{eff})$$

### Variable Cible (Label pour l'IA) :
- **Mode Classification (Recommandé pour STM32)** :
  - `0` : Pas d'arrosage nécessaire (sol suffisant ou pluie récente).
  - `1` : Arrosage requis (déficit hydrique $I_{net} > 2.5$ mm/jour).
- **Mode Régression (Optionnel)** :
  - Prédiction de la dose exacte d'eau ($mm/jour$ ou durée d'activation de la vanne en minutes).

---

## 4. Adaptation Immédiate des Rôles (Sprint 3 Semaines)

| Rôle | Nouvelles Tâches Adaptées au Souss & Copernicus |
| :--- | :--- |
| **👤 Membre 2 (Data / IA)** | • Télécharge les données Copernicus ERA5 du Souss (2022-2024).<br>• Vérifie les colonnes ($T, RH, Wind, Radiation, ET_0, Pluie$).<br>• Entraîne l'arbre de décision TinyML sur ce climat réel aride.<br>• Exporte `tinyml_model.h` pour la STM32. |
| **👤 Membre 1 (Toi - STM32)** | • Met à jour la signature de la fonction C :<br>`tinyml_predict_watering(temp, humidity, wind, radiation, et0)`.<br>• Simule l'inférence Cortex-M4 sur les journées types du Souss.<br>• Mesure la latence ($< 1$ µs) et garantit la sécurité. |
| **👤 Membre 3 (Fog / Benchmark)** | • Simule l'irrigation sur une année complète dans le Souss.<br>• Compare le modèle IA vs les pratiques fixes traditionnelles.<br>• Démontre l'économie d'eau en $m^3/ha$ pour la région du Souss. |
