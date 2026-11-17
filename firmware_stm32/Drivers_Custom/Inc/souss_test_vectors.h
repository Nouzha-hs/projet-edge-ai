/**
 * @file souss_test_vectors.h
 * @brief Scénarios climatiques réels de la région du Souss (Maroc) pour simulation STM32
 */

#ifndef SOUSS_TEST_VECTORS_H_
#define SOUSS_TEST_VECTORS_H_

#include <stdint.h>

typedef struct {
    float temp_mean_c;
    float humidity_mean_pct;
    float wind_speed_max_ms;
    float solar_radiation_mj;
    float et0_fao_mm;
    uint8_t expected_action; /* 1 = Arrosage, 0 = Pas d'arrosage */
    const char *scenario_name;
    const char *agronomic_context;
} SoussScenario_t;

static const SoussScenario_t SOUSS_SCENARIOS[] = {
    {
        38.5f, 20.0f, 6.5f, 28.5f, 7.8f, 1,
        "Canicule d'Été à Taroudant (Juillet)",
        "Déficit hydrique extrême, ET0 très élevée -> Arrosage impératif"
    },
    {
        16.0f, 85.0f, 3.2f, 11.5f, 1.8f, 0,
        "Journée d'Hiver Humide (Janvier)",
        "Faible évapotranspiration, pluies résiduelles -> Pas d'arrosage"
    },
    {
        25.0f, 52.0f, 4.0f, 22.0f, 4.6f, 1,
        "Printemps Maraîcher dans le Souss (Avril)",
        "Besoins normaux pour la croissance des cultures -> Arrosage d'appoint"
    },
    {
        42.0f, 12.0f, 9.5f, 31.0f, 9.2f, 1,
        "Épisode de Chergui (Vent chaud et sec du désert)",
        "Évapotranspiration maximale (9.2 mm/j) -> Arrosage critique"
    },
    {
        19.5f, 68.0f, 2.5f, 14.0f, 2.3f, 0,
        "Automne Tempéré (Novembre)",
        "Conditions modérées, pas de stress hydrique immédiat"
    }
};

#define SOUSS_NUM_SCENARIOS (sizeof(SOUSS_SCENARIOS) / sizeof(SOUSS_SCENARIOS[0]))

#endif /* SOUSS_TEST_VECTORS_H_ */
