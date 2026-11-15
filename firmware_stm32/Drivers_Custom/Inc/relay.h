/**
 * @file relay.h
 * @brief Gestion sécurisée du relais de commande de pompe
 */

#ifndef RELAY_H_
#define RELAY_H_

#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

/* Sécurité : Durée d'arrosage maximale absolue (en ms) pour éviter tout risque de noyade de la plante */
#define RELAY_MAX_ACTIVE_DURATION_MS  (30 * 1000) /* 30 secondes max */

typedef struct {
    GPIO_TypeDef *port;
    uint16_t pin;
    bool active_low;          /* true pour la majorité des modules relais chinois 5V */
    bool is_on;
    uint32_t start_time_ms;
} Relay_t;

void Relay_Init(Relay_t *relay, GPIO_TypeDef *port, uint16_t pin, bool active_low);
void Relay_TurnOn(Relay_t *relay);
void Relay_TurnOff(Relay_t *relay);
void Relay_UpdateSecurityWatchdog(Relay_t *relay); /* À appeler régulièrement dans la boucle */
bool Relay_IsActive(Relay_t *relay);

#endif /* RELAY_H_ */
