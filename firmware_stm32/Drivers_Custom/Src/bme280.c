/**
 * @file bme280.c
 * @brief Implémentation du driver BME280 avec compensation entière Bosch
 */

#include "bme280.h"

/* Structure interne des paramètres d'étalonnage stockés en ROM du BME280 */
typedef struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;

    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;

    uint8_t  dig_H1;
    int16_t  dig_H2;
    uint8_t  dig_H3;
    int16_t  dig_H4;
    int16_t  dig_H5;
    int8_t   dig_H6;
} BME280_CalibData_t;

static BME280_CalibData_t calib;
static int32_t t_fine = 0;

static HAL_StatusTypeDef BME280_ReadCalib(I2C_HandleTypeDef *hi2c, uint16_t devAddress) {
    uint8_t buff1[26];
    uint8_t buff2[7];

    /* Lecture des registres 0x88 à 0xA1 (Température & Pression) */
    if (HAL_I2C_Mem_Read(hi2c, devAddress, 0x88, I2C_MEMADD_SIZE_8BIT, buff1, 24, HAL_MAX_DELAY) != HAL_OK) return HAL_ERROR;
    calib.dig_T1 = (uint16_t)(buff1[1] << 8 | buff1[0]);
    calib.dig_T2 = (int16_t)(buff1[3] << 8 | buff1[2]);
    calib.dig_T3 = (int16_t)(buff1[5] << 8 | buff1[4]);

    calib.dig_P1 = (uint16_t)(buff1[7] << 8 | buff1[6]);
    calib.dig_P2 = (int16_t)(buff1[9] << 8 | buff1[8]);
    calib.dig_P3 = (int16_t)(buff1[11] << 8 | buff1[10]);
    calib.dig_P4 = (int16_t)(buff1[13] << 8 | buff1[12]);
    calib.dig_P5 = (int16_t)(buff1[15] << 8 | buff1[14]);
    calib.dig_P6 = (int16_t)(buff1[17] << 8 | buff1[16]);
    calib.dig_P7 = (int16_t)(buff1[19] << 8 | buff1[18]);
    calib.dig_P8 = (int16_t)(buff1[21] << 8 | buff1[20]);
    calib.dig_P9 = (int16_t)(buff1[23] << 8 | buff1[22]);

    /* Lecture dig_H1 à 0xA1 */
    if (HAL_I2C_Mem_Read(hi2c, devAddress, 0xA1, I2C_MEMADD_SIZE_8BIT, &calib.dig_H1, 1, HAL_MAX_DELAY) != HAL_OK) return HAL_ERROR;

    /* Lecture dig_H2 à dig_H6 de 0xE1 à 0xE7 */
    if (HAL_I2C_Mem_Read(hi2c, devAddress, 0xE1, I2C_MEMADD_SIZE_8BIT, buff2, 7, HAL_MAX_DELAY) != HAL_OK) return HAL_ERROR;
    calib.dig_H2 = (int16_t)(buff2[1] << 8 | buff2[0]);
    calib.dig_H3 = buff2[2];
    calib.dig_H4 = (int16_t)((buff2[3] << 4) | (buff2[4] & 0x0F));
    calib.dig_H5 = (int16_t)((buff2[5] << 4) | (buff2[4] >> 4));
    calib.dig_H6 = (int8_t)buff2[6];

    return HAL_OK;
}

HAL_StatusTypeDef BME280_Init(I2C_HandleTypeDef *hi2c, uint16_t devAddress) {
    uint8_t chip_id = 0;
    
    /* 1. Vérification du Chip ID */
    if (HAL_I2C_Mem_Read(hi2c, devAddress, BME280_REG_ID, I2C_MEMADD_SIZE_8BIT, &chip_id, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    if (chip_id != BME280_CHIP_ID) {
        return HAL_ERROR; /* Mauvais composant ou problème d'adresse I2C */
    }

    /* 2. Lecture des coefficients d'étalonnage usine */
    if (BME280_ReadCalib(hi2c, devAddress) != HAL_OK) {
        return HAL_ERROR;
    }

    /* 3. Configuration de l'humidité : Oversampling x1 */
    uint8_t ctrl_hum = 0x01;
    HAL_I2C_Mem_Write(hi2c, devAddress, BME280_REG_CTRL_HUM, I2C_MEMADD_SIZE_8BIT, &ctrl_hum, 1, HAL_MAX_DELAY);

    /* 4. Configuration Mesure : Temp x1, Press x1, Normal Mode (0x27) */
    uint8_t ctrl_meas = (0x01 << 5) | (0x01 << 2) | 0x03;
    HAL_I2C_Mem_Write(hi2c, devAddress, BME280_REG_CTRL_MEAS, I2C_MEMADD_SIZE_8BIT, &ctrl_meas, 1, HAL_MAX_DELAY);

    /* 5. Configuration Filtre & Standby (Standby 500ms, Filter off) */
    uint8_t config = (0x04 << 5);
    HAL_I2C_Mem_Write(hi2c, devAddress, BME280_REG_CONFIG, I2C_MEMADD_SIZE_8BIT, &config, 1, HAL_MAX_DELAY);

    return HAL_OK;
}

HAL_StatusTypeDef BME280_ReadData(I2C_HandleTypeDef *hi2c, uint16_t devAddress, BME280_Data_t *data) {
    uint8_t raw[8];
    if (HAL_I2C_Mem_Read(hi2c, devAddress, BME280_REG_PRESS_MSB, I2C_MEMADD_SIZE_8BIT, raw, 8, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }

    int32_t adc_P = (int32_t)((raw[0] << 12) | (raw[1] << 4) | (raw[2] >> 4));
    int32_t adc_T = (int32_t)((raw[3] << 12) | (raw[4] << 4) | (raw[5] >> 4));
    int32_t adc_H = (int32_t)((raw[6] << 8)  | raw[7]);

    /* --- Compensation Température --- */
    int32_t var1_T = ((((adc_T >> 3) - ((int32_t)calib.dig_T1 << 1))) * ((int32_t)calib.dig_T2)) >> 11;
    int32_t var2_T = (((((adc_T >> 4) - ((int32_t)calib.dig_T1)) * ((adc_T >> 4) - ((int32_t)calib.dig_T1))) >> 12) * ((int32_t)calib.dig_T3)) >> 14;
    t_fine = var1_T + var2_T;
    data->temperature = (float)((t_fine * 5 + 128) >> 8) / 100.0f;

    /* --- Compensation Pression --- */
    int64_t var1_P = ((int64_t)t_fine) - 128000;
    int64_t var2_P = var1_P * var1_P * (int64_t)calib.dig_P6;
    var2_P = var2_P + ((var1_P * (int64_t)calib.dig_P5) << 17);
    var2_P = var2_P + (((int64_t)calib.dig_P4) << 35);
    var1_P = ((var1_P * var1_P * (int64_t)calib.dig_P3) >> 8) + ((var1_P * (int64_t)calib.dig_P2) << 12);
    var1_P = (((((int64_t)1) << 47) + var1_P)) * ((int64_t)calib.dig_P1) >> 33;
    if (var1_P == 0) {
        data->pressure = 0.0f;
    } else {
        int64_t p = 1048576 - adc_P;
        p = (((p << 31) - var2_P) * 3125) / var1_P;
        var1_P = (((int64_t)calib.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
        var2_P = (((int64_t)calib.dig_P8) * p) >> 19;
        p = ((p + var1_P + var2_P) >> 8) + (((int64_t)calib.dig_P7) << 4);
        data->pressure = (float)p / 256.0f / 100.0f; /* en hPa */
    }

    /* --- Compensation Humidité --- */
    int32_t v_x1_u32r = (t_fine - ((int32_t)76800));
    v_x1_u32r = (((((adc_H << 14) - (((int32_t)calib.dig_H4) << 20) - (((int32_t)calib.dig_H5) * v_x1_u32r)) + ((int32_t)16384)) >> 15) *
                 (((((((v_x1_u32r * ((int32_t)calib.dig_H6)) >> 10) * (((v_x1_u32r * ((int32_t)calib.dig_H3)) >> 11) + ((int32_t)32768))) >> 10) +
                    ((int32_t)2097152)) * ((int32_t)calib.dig_H2) + 8192) >> 14));
    v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * ((int32_t)calib.dig_H1)) >> 4));
    v_x1_u32r = (v_x1_u32r < 0 ? 0 : v_x1_u32r);
    v_x1_u32r = (v_x1_u32r > 419430400 ? 419430400 : v_x1_u32r);
    data->humidity = (float)(v_x1_u32r >> 12) / 1024.0f;

    return HAL_OK;
}
