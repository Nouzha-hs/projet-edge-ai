/**
 * @file soil_sensor.h
 * @brief Driver pour capteur d'humidité du sol capacitif v1.2 (ADC STM32)
 */

#ifndef SOIL_SENSOR_H_
#define SOIL_SENSOR_H_

#include "stm32f4xx_hal.h"
#include <stdint.h>

/* Valeurs d'étalonnage par défaut (ADC 12 bits : 0 - 4095) */
#define SOIL_CALIB_AIR_DEFAULT    3200  /* Valeur à l'air libre (Terre totalement sèche = 0%) */
#define SOIL_CALIB_WATER_DEFAULT  1500  /* Valeur immergé dans l'eau (Saturé = 100%) */

typedef struct {
    ADC_HandleTypeDef *hadc;
    uint32_t adc_channel;
    uint16_t calib_air;    /* Seuil sol sec */
    uint16_t calib_water;  /* Seuil sol saturé */
} SoilSensor_t;

void SoilSensor_Init(SoilSensor_t *sensor, ADC_HandleTypeDef *hadc, uint32_t channel, uint16_t calib_air, uint16_t calib_water);
uint16_t SoilSensor_ReadRaw(SoilSensor_t *sensor);
float SoilSensor_ReadPercentage(SoilSensor_t *sensor);

#endif /* SOIL_SENSOR_H_ */
