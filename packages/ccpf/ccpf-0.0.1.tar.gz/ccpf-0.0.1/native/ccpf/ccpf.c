#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include "ccpf.h"

int cpf_validate(char* cpf, int size) {
    int res = cpf_unmask(cpf, size);
    if(res == 2) return 0;
    uint16_t second_sum = 0;
    uint16_t first_sum = 0;
    for(uint8_t i = 0; i < 9; i++) {
        const uint8_t current_digit = (cpf[i] - '0');
        const uint8_t current_value = current_digit * i;
        second_sum += current_value;
        first_sum += current_value + current_digit;
    }
    uint16_t verificator_digit = first_sum % 11;
    verificator_digit = verificator_digit == 10 ? 0 : verificator_digit;
    uint8_t real_first_verificator_digit = (cpf[9] - '0');
    if(verificator_digit != real_first_verificator_digit) return 0;

    second_sum += real_first_verificator_digit * 9;
    verificator_digit = second_sum % 11;
    verificator_digit = verificator_digit == 10 ? 0 : verificator_digit;
    return verificator_digit == (cpf[10] - '0');
}

void cpf_generate(char* cpf) {
    srand(time(0));
    uint16_t second_sum = 0;
    uint16_t first_sum = 0;
    for(uint8_t i = 0; i < 9; i++) {
        cpf[i] = (rand() % 10);
        const uint8_t current_value = cpf[i] * i;
        second_sum += current_value;
        first_sum += current_value + cpf[i];
        cpf[i] += '0';
    }
    uint16_t verificator_digit = first_sum % 11;
    if(verificator_digit == 10) verificator_digit = 0;
    cpf[9] = verificator_digit + '0';
    second_sum += verificator_digit * 9;
    verificator_digit = second_sum % 11;
    if(verificator_digit == 10) verificator_digit = 0;
    cpf[10] = verificator_digit + '0';
}

#include <stdio.h>
int cpf_has_mask(char* cpf, int size) {
    if(size < 11) return 2;
    if(size == 11) {
        // check for first format
        uint8_t is_first_format = 1;
        for(uint8_t i = 0; i < 11; i++) {
            if(cpf[i] > '9' || cpf[i] < '0') {
                is_first_format = 0;
                break;
            }
        }
        if(is_first_format) return 0;
    }
    if(size != 14) return 2;
    if(cpf[3] != '.' && cpf[7] != '.' && cpf[11] != '-') return 2;
    for(uint8_t i = 0; i < 3; i++) {
        if(cpf[i] > '9' || cpf[i] < '0') return 2;
        if(cpf[i+4] > '9' || cpf[i+4] < '0') return 2;
        if(cpf[i+8] > '9' || cpf[i+8] < '0') return 2;
    }
    if(cpf[12] > '9' || cpf[13] < '0') return 2;
    return 1;
}

int cpf_mask(char* cpf, int size) {
    int res = cpf_has_mask(cpf, size-3);
    if(res == 2) return 0;
    if(res == 1) return 1;

    for(unsigned int i = 10; i >= 9; i--) cpf[i+3] = cpf[i];
    for(unsigned int i = 8; i >= 6; i--) cpf[i+2] = cpf[i];
    for(unsigned int i = 5; i >= 3; i--) cpf[i+1] = cpf[i];
    cpf[11] = '-';
    cpf[3] = '.';
    cpf[7] = '.';
    return 1;
}

int cpf_unmask(char* cpf, int size) {
    int res = cpf_has_mask(cpf, size);
    if(res == 2) return 0;
    if(res == 0) return 1;

    for(unsigned int i = 3; i < 6; i++) cpf[i] = cpf[i+1];
    for(unsigned int i = 6; i < 9; i++) cpf[i] = cpf[i+2];
    for(unsigned int i = 9; i < 11; i++) cpf[i] = cpf[i+3];
    cpf[11] = '\0';
    return 1;
}
