/*
 * Doki: Quantum Computer simulator, using state vectors. QSimov core.
 * Copyright (C) 2021  Hernán Indíbil de la Cruz Calvo
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include "arraylist.h"
#include "platform.h"

unsigned char
alist_init (struct array_list_e *this, NATURAL_TYPE size)
{
  size_t i, offset, errored_chunk;
  _Bool errored;

  this->size = size;
  this->num_chunks = this->size / NATURAL_ARRAY_SIZE;
  offset = this->size % NATURAL_ARRAY_SIZE;
  if (offset > 0)
    {
      this->num_chunks++;
    }
  else
    {
      offset = NATURAL_ARRAY_SIZE;
    }
  this->vector = MALLOC_TYPE (this->num_chunks, NATURAL_TYPE *);
  if (this->vector == NULL)
    {
      return 1;
    }
  errored = 0;
  for (i = 0; i < this->num_chunks - 1; i++)
    {
      this->vector[i] = MALLOC_TYPE (NATURAL_ARRAY_SIZE, NATURAL_TYPE);
      if (this->vector[i] == NULL)
        {
          errored = 1;
          errored_chunk = i;
          break;
        }
    }
  if (!errored)
    {
      this->vector[this->num_chunks - 1] = MALLOC_TYPE (offset, NATURAL_TYPE);
      if (this->vector[this->num_chunks - 1] == NULL)
        {
          errored = 1;
          errored_chunk = this->num_chunks - 1;
        }
    }
  if (errored)
    {
      for (i = 0; i < errored_chunk; i++)
        {
          free (this->vector[i]);
        }
      free (this->vector);
      return 2;
    }

  return 0;
}

void
alist_clear (struct array_list_e *this)
{
  size_t i;
  if (this->vector != NULL)
    {
      for (i = 0; i < this->num_chunks; i++)
        {
          free (this->vector[i]);
        }
      free (this->vector);
    }
  this->vector = NULL;
  this->num_chunks = 0;
  this->size = 0;
}

void
alist_set (struct array_list_e *this, NATURAL_TYPE i, NATURAL_TYPE value)
{
  this->vector[i / COMPLEX_ARRAY_SIZE][i % COMPLEX_ARRAY_SIZE] = value;
}

NATURAL_TYPE
alist_get (struct array_list_e *this, NATURAL_TYPE i)
{
  return this->vector[i / COMPLEX_ARRAY_SIZE][i % COMPLEX_ARRAY_SIZE];
}
