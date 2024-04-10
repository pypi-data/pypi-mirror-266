/*
 * cybergram - Telegram MTProto API Client Library for Python
 * Copyright (C) 2024-present rizaldevs <https://github.com/rizaldevs>
 *
 * This file is part of cybergram.
 *
 * cybergram is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * cybergram is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with cybergram.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef CBC256_H
#define CBC256_H

uint8_t *cbc256(const uint8_t in[], uint32_t length, const uint8_t key[32], uint8_t iv[16], uint8_t encrypt);

#endif  // CBC256_H
