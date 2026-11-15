/**
 * @file soil_sensor.c
 * @brief Implémentation de la lecture et conversion du capteur capacitif
 */

#include "soil_sensor.h"

void SoilSensor_Init(SoilSensor_t *sensor, ADC_HandleTypeDef *hadc, uint32_t channel, uint16_t calib_air, uint16_t calib_water) {
    sensor->hadc = hadc;
    sensor->adc_channel = channel;
    sensor->calib_air = (calib_air > 0) ? calib_air : SOIL_CALIB_AIR_DEFAULT;
    sensor->calib_water = (calib_water > 0) ? calib_water : SOIL_CALIB_WATER_DEFAULT;
}

uint16_t SoilSensor_ReadRaw(SoilSensor_t *sensor) {
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = sensor->adc_channel;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_84CYCLES;
    
    HAL_ADC_ConfigChannel(sensor->hadc, &sConfig);

    uint32_t sum = 0;
    const uint8_t samples = 8; /* Moyennage sur 8 mesures pour stabiliser la lecture */

    for (uint8_t i = 0; i < samples; i++) {
        HAL_ADC_Start(sensor->hadc);
        if (HAL_ADC_PollForConversion(sensor->hadc, 10) == HAL_OK) {
            sum += HAL_ADC_GetValue(sensor->hadc);
        }
        HAL_ADC_Stop(sensor->hadc);
    }

    return (uint16_t)(sum / samples);
}

float SoilSensor_ReadPercentage(SoilSensor_t *sensor) {
    uint16_t raw = SoilSensor_ReadRaw(sensor);

    /* Dans un capteur capacitif, la tension est INVERSEMENT proportionnelle à l'humidité :
       - Forte humidité = capacité élevée = tension basse (proche de calib_water)
       - Faible humidité = capacité faible = tension haute (proche de calib_air) */
    if (raw >= sensor->calib_air) {
        return 0.0f;
    }
    if (raw <= sensor->calib_water) {
        return 100.0f;
    }

    float percentage = (float)(sensor->calib_air - raw) / (float)(sensor->calib_air - sensor->calib_water) * 100.0f;
    return percentage;
}
