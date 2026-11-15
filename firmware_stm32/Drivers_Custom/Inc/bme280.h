/**
 * @file bme280.h
 * @brief Driver BME280 I2C pour STM32 (HAL)
 * @details Mesure température, humidité et pression atmosphérique
 */

#ifndef BME280_H_
#define BME280_H_

#include "stm32f4xx_hal.h"
#include <stdint.h>

/* Adresses I2C typiques (décalées de 1 bit pour HAL : 0x76 << 1 = 0xEC ou 0x77 << 1 = 0xEE) */
#define BME280_I2C_ADDRESS_LOW   (0x76 << 1)
#define BME280_I2C_ADDRESS_HIGH  (0x77 << 1)

/* Registres clés du BME280 */
#define BME280_REG_ID            0xD0
#define BME280_REG_RESET         0xE0
#define BME280_REG_CTRL_HUM      0xF2
#define BME280_REG_STATUS        0xF3
#define BME280_REG_CTRL_MEAS     0xF4
#define BME280_REG_CONFIG        0xF5
#define BME280_REG_PRESS_MSB     0xF7

#define BME280_CHIP_ID           0x60

/* Structure de données lues */
typedef struct {
    float temperature; /* en degrés Celsius */
    float humidity;    /* en pourcentage d'humidité relative (%) */
    float pressure;    /* en hPa (hectopascals) */
} BME280_Data_t;

/* Fonctions de pilotage */
HAL_StatusTypeDef BME280_Init(I2C_HandleTypeDef *hi2c, uint16_t devAddress);
HAL_StatusTypeDef BME280_ReadData(I2C_HandleTypeDef *hi2c, uint16_t devAddress, BME280_Data_t *data);

#endif /* BME280_H_ */
