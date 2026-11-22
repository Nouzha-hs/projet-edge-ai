/**
 * @file tinyml_model_souss.h
 * @brief Modèle TinyML pour la région du SOUSS (Données Copernicus ERA5 / FAO-56)
 * @details Généré pour STM32 Nucleo-F401RE (0 allocation dynamique, exécution < 1 µs)
 */

#ifndef TINYML_MODEL_SOUSS_H_
#define TINYML_MODEL_SOUSS_H_

#include <stdint.h>

/**
 * Prédit le besoin d'arrosage dans la région du Souss
 * @param temp_mean_c
 * @param humidity_mean_pct
 * @param wind_speed_max_ms
 * @param solar_radiation_mj
 * @param et0_fao_mm
 * @return uint8_t 1 = Arrosage Requis, 0 = Pas d'arrosage
 */
static inline uint8_t tinyml_predict_souss_irrigation(float temp_mean_c, float humidity_mean_pct, float wind_speed_max_ms, float solar_radiation_mj, float et0_fao_mm) {
    if (et0_fao_mm <= 2.5950f) {
        if (humidity_mean_pct <= 71.5000f) {
            return 1;
        } else {
            return 0;
        }
    } else {
        if (wind_speed_max_ms <= 28.3500f) {
            if (humidity_mean_pct <= 76.0000f) {
                if (temp_mean_c <= 16.0500f) {
                    return 1;
                } else {
                    return 1;
                }
            } else {
                return 1;
            }
        } else {
            if (et0_fao_mm <= 4.6300f) {
                return 0;
            } else {
                if (wind_speed_max_ms <= 31.8500f) {
                    return 1;
                } else {
                    return 1;
                }
            }
        }
    }
}

#endif /* TINYML_MODEL_SOUSS_H_ */
