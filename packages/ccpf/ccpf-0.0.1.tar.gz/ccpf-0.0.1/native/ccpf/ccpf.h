#pragma once

// 0 -> not valid
// 1 -> valid
int cpf_validate(char* cpf, int size);
// 'cpf' must have space for 11 chars
void cpf_generate(char* cpf);
// returns 2 if format is invalid
// returns 1 if there is a mask
// returns 0 if there isn't a mask
int cpf_has_mask(char* cpf, int size);
// 1 -> success, 0 -> invalid format
// if the cpf is already masked, success is returned
int cpf_mask(char* cpf, int size);
// 1 -> success, 0 -> invalid format
// if the cpf is already unmasked, success is returned
int cpf_unmask(char* cpf, int size);
