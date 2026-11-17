/**
 * @file tinyml_model_souss.h
 * @brief Modèle d'Inférence TinyML pour la région du Souss (Maroc)
 * @details Conçu pour STM32 Nucleo-F401RE (Cortex-M4 @ 84 MHz)
 *          Variables d'entrée Copernicus : Température, Humidité, Vent, Rayonnement, ET0
 */

#ifndef TINYML_MODEL_SOUSS_H_
#define TINYML_MODEL_SOUSS_H_

#include <stdint.h>

/**
 * @brief Prédit si l'irrigation est requise dans le Souss
 * @param temp_mean_c Température moyenne (°C)
 * @param humidity_mean_pct Humidité relative moyenne (%)
 * @param wind_speed_max_ms Vitesse max du vent (m/s)
 * @param solar_radiation_mj Rayonnement solaire incident (MJ/m²)
 * @param et0_fao_mm Évapotranspiration de référence FAO-56 (mm/jour)
 * @return uint8_t 1 = Activer l'arrosage, 0 = Pas d'arrosage
 */
static inline uint8_t tinyml_predict_souss_irrigation(
    float temp_mean_c,
    float humidity_mean_pct,
    float wind_speed_max_ms,
    float solar_radiation_mj,
    float et0_fao_mm
) {
    /* 1. Faible demande évaporative (Hiver / Temps pluvieux) */
    if (et0_fao_mm <= 2.35f) {
        return 0; /* Pas d'arrosage nécessaire */
    }

    /* 2. Forte demande évaporative (Été / Chaleur / Chergui) */
    if (et0_fao_mm >= 3.80f) {
        return 1; /* Arrosage indispensable */
    }

    /* 3. Zone intermédiaire (Printemps / Automne : ET0 entre 2.35 et 3.80 mm/j) */
    if (humidity_mean_pct <= 55.0f || temp_mean_c >= 22.0f) {
        return 1; /* Air sec ou température montante : arrosage d'appoint */
    }

    return 0; /* Humidité suffisante pour temporiser */
}

#endif /* TINYML_MODEL_SOUSS_H_ */
