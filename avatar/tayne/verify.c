/* Verify the strip decoder contract at real device and preview sizes. */
#include "muse_pixel.h"
#include "../characters.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static uint16_t full[512*512], strip[512*16+2];
int main(void)
{
    const int sizes[] = {1, 64, 128, 135, 320, 512};
    assert(muse_character_count() == 3);
    assert(!muse_character_select(-1));
    assert(!muse_character_select(3));
    unsigned hashes[3] = {0};
    for (int c=0; c<muse_character_count(); c++) {
    assert(muse_character_select(c));
    assert(muse_character_current() == c);
    for (unsigned s=0; s<sizeof(sizes)/sizeof(sizes[0]); s++) {
        int n=sizes[s];
        muse_pixel_set_size(n);
        for (int mode=0; mode<MUSE_MODE_COUNT; mode++) {
            muse_pose_t p={.mode=mode, .t=12.3f, .mode_t=0.6f, .level=0.8f, .happy=0.5f};
            muse_pixel_render(&p);
            muse_pixel_scale(full, n, 0, n-1, 0, n-1);
            if (n == 64 && mode == MUSE_MODE_IDLE) {
                for (int i=0; i<n*n; i++) hashes[c] = hashes[c] * 33u + full[i];
            }
            for (int y=0; y<n; y+=16) {
                int h=n-y < 16 ? n-y : 16;
                /* Check both full-width strips and partial-width tiles. */
                int left=n>16 ? 7 : 0;
                int right=n>16 ? n-5 : n-1;
                int w=right-left+1;
                memset(strip, 0xa5, sizeof(strip));
                muse_pixel_scale(strip+1, w, left, right, y, y+h-1);
                assert(strip[0] == 0xa5a5 && strip[w*h+1] == 0xa5a5);
                for (int row=0; row<h; row++)
                    assert(memcmp(strip+1+row*w, full+(y+row)*n+left, (size_t)w*2)==0);
            }
        }
    }
    }
    assert(hashes[0] != hashes[1] && hashes[1] != hashes[2] && hashes[0] != hashes[2]);
    puts("Three distinct characters, invalid selections rejected, seven modes and six strip sizes verified.");
    return 0;
}
