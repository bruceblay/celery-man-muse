/* Compile the default pet directly from the user's SDK checkout.
 * The upstream avatar retains its original copyright and is not copied here.
 * Host tools supply an absolute MUSE_DEFAULT_SOURCE; firmware uses this path
 * relative to esp32/components/muse/avatar/ after installation. */
#include "muse_default.h"
#define muse_pixel_render muse_default_render
#define muse_pixel_accent muse_default_accent
#define muse_pixel_set_size muse_default_set_size
#define muse_pixel_scale muse_default_scale
#ifndef MUSE_DEFAULT_SOURCE
#define MUSE_DEFAULT_SOURCE "../../../avatar/muse_pixel.c"
#endif
#include MUSE_DEFAULT_SOURCE
