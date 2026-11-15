/**
 * @file relay.c
 * @brief Implémentation du contrôle de relais avec coupe-circuit automatique
 */

#include "relay.h"

void Relay_Init(Relay_t *relay, GPIO_TypeDef *port, uint16_t pin, bool active_low) {
    relay->port = port;
    relay->pin = pin;
    relay->active_low = active_low;
    relay->is_on = false;
    relay->start_time_ms = 0;

    /* Éteindre le relais dès l'initialisation */
    Relay_TurnOff(relay);
}

void Relay_TurnOn(Relay_t *relay) {
    if (!relay->is_on) {
        GPIO_PinState state = relay->active_low ? GPIO_PIN_RESET : GPIO_PIN_SET;
        HAL_GPIO_WritePin(relay->port, relay->pin, state);
        relay->is_on = true;
        relay->start_time_ms = HAL_GetTick();
    }
}

void Relay_TurnOff(Relay_t *relay) {
    GPIO_PinState state = relay->active_low ? GPIO_PIN_SET : GPIO_PIN_RESET;
    HAL_GPIO_WritePin(relay->port, relay->pin, state);
    relay->is_on = false;
    relay->start_time_ms = 0;
}

void Relay_UpdateSecurityWatchdog(Relay_t *relay) {
    if (relay->is_on) {
        uint32_t now = HAL_GetTick();
        if ((now - relay->start_time_ms) >= RELAY_MAX_ACTIVE_DURATION_MS) {
            /* Sécurité déclenchée : couper la pompe immédiatement ! */
            Relay_TurnOff(relay);
        }
    }
}

bool Relay_IsActive(Relay_t *relay) {
    return relay->is_on;
}
