/**
 * @file stm32_inference_cortex_m4.c
 * @brief Module d'inférence TinyML compilé spécifiquement pour ARM Cortex-M4 (STM32F401RE)
 */

#include <stdint.h>
#include "Drivers_Custom/Inc/tinyml_model_souss.h"
#include "Drivers_Custom/Inc/souss_test_vectors.h"

/* Fonction d'entrée appelée par le firmware embarqué */
uint8_t stm32_run_souss_inference(float temp, float humidity, float wind, float radiation, float et0) {
    return tinyml_predict_souss_irrigation(temp, humidity, wind, radiation, et0);
}

/* Fonction de benchmark sur l'ensemble des scénarios du Souss */
void stm32_benchmark_all_scenarios(uint8_t *results) {
    for (uint32_t i = 0; i < SOUSS_NUM_SCENARIOS; i++) {
        const SoussScenario_t *sc = &SOUSS_SCENARIOS[i];
        results[i] = tinyml_predict_souss_irrigation(
            sc->temp_mean_c,
            sc->humidity_mean_pct,
            sc->wind_speed_max_ms,
            sc->solar_radiation_mj,
            sc->et0_fao_mm
        );
    }
}
