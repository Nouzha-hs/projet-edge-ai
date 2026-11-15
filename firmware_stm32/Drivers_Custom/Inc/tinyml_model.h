/**
 * @file tinyml_model.h
 * @brief Modèle TinyML généré automatiquement (Arbre de décision)
 */
#ifndef TINYML_MODEL_H_
#define TINYML_MODEL_H_

#include <stdint.h>

/**
 * Prédit le besoin d'arrosage (0 = NON, 1 = OUI)
 * @param temperature_c
 * @param humidity_air_pct
 * @param soil_moisture_pct
 * @param hour
 * @return uint8_t 1 si arrosage nécessaire, 0 sinon
 */
static inline uint8_t tinyml_predict_watering(float temperature_c, float humidity_air_pct, float soil_moisture_pct, float hour) {
    if (soil_moisture_pct <= 22.0400f) {
        return 1; /* Classe 1 (échantillons: 0 non / 1 oui) */
    } else {
        if (soil_moisture_pct <= 29.1650f) {
            if (temperature_c <= 29.4950f) {
                if (temperature_c <= 26.0350f) {
                    if (temperature_c <= 22.5650f) {
                        return 0; /* Classe 0 (échantillons: 1 non / 0 oui) */
                    } else {
                        return 0; /* Classe 0 (échantillons: 0 non / 0 oui) */
                    }
                } else {
                    if (hour <= 11.5000f) {
                        return 0; /* Classe 0 (échantillons: 0 non / 0 oui) */
                    } else {
                        return 0; /* Classe 0 (échantillons: 1 non / 0 oui) */
                    }
                }
            } else {
                if (soil_moisture_pct <= 25.4550f) {
                    return 1; /* Classe 1 (échantillons: 0 non / 1 oui) */
                } else {
                    return 0; /* Classe 0 (échantillons: 0 non / 0 oui) */
                }
            }
        } else {
            if (soil_moisture_pct <= 33.8950f) {
                if (temperature_c <= 24.8150f) {
                    return 0; /* Classe 0 (échantillons: 1 non / 0 oui) */
                } else {
                    if (hour <= 10.5000f) {
                        return 0; /* Classe 0 (échantillons: 0 non / 0 oui) */
                    } else {
                        return 0; /* Classe 0 (échantillons: 1 non / 0 oui) */
                    }
                }
            } else {
                return 0; /* Classe 0 (échantillons: 1 non / 0 oui) */
            }
        }
    }
}

#endif /* TINYML_MODEL_H_ */
