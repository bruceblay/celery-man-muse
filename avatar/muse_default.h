#pragma once
#include "muse_pixel.h"

/* The SDK's original renderer, compiled with separate public symbol names. */
void muse_default_render(const muse_pose_t *pose);
uint32_t muse_default_accent(muse_mode_t mode);
void muse_default_set_size(int px);
void muse_default_scale(uint16_t *dst, int stride_px, int x0, int x1, int y0, int y1);
