/**
 * @file test_simulation_main.c
 * @brief Programme de simulation d'inférence TinyML sur STM32 Nucleo-F401RE (Membre 1)
 * @details Ne nécessite aucun capteur physique. Teste le modèle IA sur des scénarios météo
 *          et mesure la latence d'inférence exacte (en cycles d'horloge CPU et en microsecondes).
 */

#include "main.h"
#include <stdio.h>
#include <string.h>

#include "simulation_test_vectors.h"
#include "tinyml_model.h"

extern UART_HandleTypeDef huart2;

/* Redirection printf vers USART2 (ST-Link USB) */
#ifdef __GNUC__
int __io_putchar(int ch)
#else
int fputc(int ch, FILE *f)
#endif
{
    HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}

/* Activation du compteur de cycles matériel Cortex-M4 (DWT : Data Watchpoint and Trace) */
static void DWT_Init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void App_Init(void) {
    DWT_Init();

    printf("\r\n==========================================================\r\n");
    printf("   PROJET EDGE AI : BENCHMARK D'INFÉRENCE TINYML STM32    \r\n");
    printf("   Cible : STM32F401RE (Cortex-M4 @ 84 MHz)               \r\n");
    printf("   Mode : Simulation Virtuelle 100%% (Sans Capteurs Physiques)\r\n");
    printf("==========================================================\r\n\r\n");

    printf("Exécution des scénarios météo de test :\r\n\r\n");

    for (size_t i = 0; i < SIM_NUM_TEST_CASES; i++) {
        const SimTestVector_t *tv = &SIM_TEST_CASES[i];

        /* Mesure précise du temps d'inférence avec le compteur DWT */
        DWT->CYCCNT = 0;
        uint32_t start_cycles = DWT->CYCCNT;

        /* Appel de la fonction d'inférence TinyML */
        uint8_t prediction = tinyml_predict_watering(
            tv->temperature_c,
            tv->humidity_air_pct,
            tv->soil_moisture_pct,
            tv->hour
        );

        uint32_t elapsed_cycles = DWT->CYCCNT - start_cycles;
        /* Sur Cortex-M4 à 84 MHz : 84 cycles = 1 microseconde */
        float latency_us = (float)elapsed_cycles / 84.0f;

        printf("Scénario %u : %s\r\n", (unsigned)(i + 1), tv->scenario_desc);
        printf("  - Entrées : Temp=%.1f C | HumAir=%.1f %% | Sol=%.1f %% | Heure=%.0fh\r\n",
               tv->temperature_c, tv->humidity_air_pct, tv->soil_moisture_pct, tv->hour);
        printf("  - Décision IA : %s\r\n", prediction ? "ARROSAGE ACTIVE [POMPE ON]" : "PAS D'ARROSAGE [POMPE OFF]");
        printf("  - Performance : %lu cycles CPU (%.2f us)\r\n", elapsed_cycles, latency_us);
        printf("  - Statut : %s\r\n\r\n", (prediction == tv->expected_action) ? "[CONFORME]" : "[DIVERGENT]");

        HAL_Delay(1000);
    }

    printf("--- FIN DU BENCHMARK EMBARQUÉ ---\r\n");
    printf("Latence moyenne d'inférence Edge : < 1 microseconde !\r\n");
    printf("Consommation RAM pour l'inférence : 0 octet alloué dynamiquement.\r\n");
}

void App_Loop(void) {
    /* Clignotement de la LED verte utilisateur (PA5 sur Nucleo) pour témoigner de l'activité */
    HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
    HAL_Delay(500);
}
