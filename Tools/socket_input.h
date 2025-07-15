#pragma once
#include <cstddef>   // size_t
#include <vector>

double get_socket_sample(int index);
/* Optional helper if you need more than one channel
   void fill_socket_buffer(double t, double* out, size_t n_channels); */

void cleanup_sockets();
