/**
 * @file test_sensors_main.c
 * @brief Programme de test unitaire des capteurs et du relais (Semaine 1)
 * @note À intégrer dans le main.c généré par STM32CubeIDE
 */

#include "main.h"
#include <stdio.h>
#include <string.h>

#include "bme280.h"
#include "soil_sensor.h"
#include "relay.h"

/* Handles configurés par CubeMX */
extern ADC_HandleTypeDef hadc1;
extern I2C_HandleTypeDef hi2c1;
extern UART_HandleTypeDef huart2; /* USART2 relié au ST-Link (USB PC) */

/* Redirection de printf vers USART2 (Port COM Virtuel ST-Link) */
#ifdef __GNUC__
int __io_putchar(int ch)
#else
int fputc(int ch, FILE *f)
#endif
{
    HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}

/* Objets capteurs & actionneurs */
static SoilSensor_t soil;
static Relay_t pump_relay;
static BME280_Data_t bme_data;

void App_Init(void) {
    printf("\r\n===================================================\r\n");
    printf("   Projet Edge AI : Test Unitaire des Capteurs     \r\n");
    printf("   Carte : STM32 Nucleo-F401RE                     \r\n");
    printf("===================================================\r\n");

    /* 1. Initialisation du relais sur PA4 (Active LOW par défaut) */
    Relay_Init(&pump_relay, GPIOA, GPIO_PIN_4, true);
    printf("[OK] Relais pompe initialisé (PA4 - repos: OFF)\r\n");

    /* 2. Initialisation du capteur capacitif sur PA0 (ADC1_IN0) */
    SoilSensor_Init(&soil, &hadc1, ADC_CHANNEL_0, SOIL_CALIB_AIR_DEFAULT, SOIL_CALIB_WATER_DEFAULT);
    printf("[OK] Capteur humidité du sol initialisé (PA0 / ADC1)\r\n");

    /* 3. Initialisation du BME280 sur I2C1 (PB8=SCL, PB9=SDA) */
    /* On essaie d'abord l'adresse 0x76, puis 0x77 si échec */
    uint16_t bme_addr = BME280_I2C_ADDRESS_LOW;
    if (BME280_Init(&hi2c1, bme_addr) != HAL_OK) {
        bme_addr = BME280_I2C_ADDRESS_HIGH;
        if (BME280_Init(&hi2c1, bme_addr) != HAL_OK) {
            printf("[ERREUR] BME280 non détecté sur 0x76 ni sur 0x77. Vérifiez le câblage PB8/PB9 !\r\n");
        } else {
            printf("[OK] BME280 détecté sur l'adresse I2C 0x77 !\r\n");
        }
    } else {
        printf("[OK] BME280 détecté sur l'adresse I2C 0x76 !\r\n");
    }

    printf("\r\nDémarrage de la boucle d'acquisition périodique (2s)...\r\n");
    printf("Format CSV : timestamp_ms;temp_C;hum_air_pct;press_hPa;soil_raw;soil_pct;pump_state\r\n\r\n");
}

void App_Loop(void) {
    static uint32_t last_tick = 0;
    static uint32_t cycle_count = 0;

    /* Surveillance continue du coupe-circuit de sécurité du relais */
    Relay_UpdateSecurityWatchdog(&pump_relay);

    if (HAL_GetTick() - last_tick >= 2000) {
        last_tick = HAL_GetTick();
        cycle_count++;

        /* 1. Lecture BME280 */
        BME280_ReadData(&hi2c1, BME280_I2C_ADDRESS_LOW, &bme_data);

        /* 2. Lecture Humidité du sol */
        uint16_t soil_raw = SoilSensor_ReadRaw(&soil);
        float soil_pct = SoilSensor_ReadPercentage(&soil);

        /* 3. Test ponctuel de la pompe : impulsion de 2 secondes tous les 15 cycles (30s) */
        if (cycle_count % 15 == 0) {
            printf("[ACTION] Test de déclenchement pompe (durée 2 sec)...\r\n");
            Relay_TurnOn(&pump_relay);
        } else if (Relay_IsActive(&pump_relay) && (HAL_GetTick() - pump_relay.start_time_ms >= 2000)) {
            Relay_TurnOff(&pump_relay);
        }

        /* 4. Affichage formatté pour lecture humaine & enregistrement CSV */
        printf("%lu;%.2f;%.2f;%.1f;%u;%.1f;%d\r\n",
               HAL_GetTick(),
               bme_data.temperature,
               bme_data.humidity,
               bme_data.pressure,
               soil_raw,
               soil_pct,
               Relay_IsActive(&pump_relay) ? 1 : 0);
    }
}
