/**
 * @file simulation_test_vectors.h
 * @brief Vecteurs de test pour simuler les capteurs dans le STM32 sans matériel physique
 */

#ifndef SIMULATION_TEST_VECTORS_H_
#define SIMULATION_TEST_VECTORS_H_

#include <stdint.h>

typedef struct {
    float temperature_c;
    float humidity_air_pct;
    float soil_moisture_pct;
    float hour;
    uint8_t expected_action; /* 0 = Pas d'arrosage, 1 = Arrosage */
    const char *scenario_desc;
} SimTestVector_t;

static const SimTestVector_t SIM_TEST_CASES[] = {
    {18.5f, 75.0f, 62.0f,  4.0f, 0, "Nuit fraîche, sol bien hydraté"},
    {34.2f, 28.0f, 18.5f, 14.0f, 1, "Après-midi caniculaire, sol très sec (Urgence)"},
    {27.0f, 45.0f, 31.0f, 20.0f, 1, "Soirée d'été, sol modérément sec (Arrosage optimal)"},
    {32.0f, 35.0f, 42.0f, 13.0f, 0, "Plein soleil, sol encore humide (Éviter évaporation)"},
    {15.0f, 85.0f, 16.0f,  7.0f, 1, "Matinée fraîche mais sol critique (Urgence)"}
};

#define SIM_NUM_TEST_CASES (sizeof(SIM_TEST_CASES) / sizeof(SIM_TEST_CASES[0]))

#endif /* SIMULATION_TEST_VECTORS_H_ */
