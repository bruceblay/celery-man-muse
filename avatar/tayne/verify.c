/* Verify the strip decoder contract at real device and preview sizes. */
#include "muse_pixel.h"
#include "../characters.h"
#include "../muse_default.h"
#include "sprites.h"
#include "../celery-man/sprites.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static uint16_t full[512*512], strip[512*16+2];
int main(void)
{
    /* Native avatar sizes: AIPI 96, sticks 128, Watcher 256, Waveshare 320.
     * Panel sizes and odd widths also exercise non-integer scaling. */
    const int sizes[] = {1, 64, 96, 128, 135, 192, 240, 256, 320, 368, 412, 448, 466, 512};
    assert(muse_character_count() == 4);
    assert(!muse_character_select(-1));
    assert(!muse_character_select(4));
    unsigned hashes[4] = {0};
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
            if (c == MUSE_CHARACTER_DEFAULT) {
                uint16_t direct[512];
                for (int y=0; y<n; y++) {
                    muse_default_scale(direct, n, 0, n-1, y, y);
                    assert(memcmp(direct, full+y*n, (size_t)n*2)==0);
                }
                assert(muse_pixel_accent(mode) == muse_default_accent(mode));
            }
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
    for (int i=0; i<4; i++) for (int j=i+1; j<4; j++) assert(hashes[i] != hashes[j]);
    /* Walk complete animation cycles, including every sampled Tayne video frame.
     * The one-pose strip checks above cannot catch a bad sprite index later. */
    muse_pixel_set_size(64);
    unsigned dance_hashes[24] = {0};
    for (int c=0; c<3; c++) {
        assert(muse_character_select(c));
        for (int mode=0; mode<MUSE_MODE_COUNT; mode++) {
            for (int happy=0; happy<2; happy++) {
                for (int tick=0; tick<160; tick++) {
                    float seconds=tick/15.0f;
                    muse_pose_t p={.mode=mode, .t=seconds, .mode_t=seconds,
                                  .level=(tick%11)*0.1f, .happy=(float)happy};
                    muse_pixel_render(&p);
                    muse_pixel_scale(full, 64, 0, 63, 0, 63);
                    if (c==0 && mode==MUSE_MODE_IDLE && !happy) {
                        assert(memcmp(full, tayne_sprites[TAYNE_IDLE_FIRST+tick%24], 4096*sizeof(uint16_t))==0);
                        unsigned hash=0;
                        for (int i=0; i<4096; i++) hash=hash*33u+full[i];
                        if (tick<24) dance_hashes[tick]=hash;
                        else assert(hash==dance_hashes[tick%24]);
                    }
                }
            }
        }
    }
    int unique=0;
    for (int i=0; i<24; i++) {
        bool seen=false;
        for (int j=0; j<i; j++) if (dance_hashes[i]==dance_hashes[j]) seen=true;
        if (!seen) unique++;
    }
    assert(unique>16);
    /* Microphone levels do not interrupt the filmed listening dance. */
    assert(muse_character_select(0));
    for (int tick=0; tick<48; tick++) {
        muse_pose_t p={.mode=MUSE_MODE_LISTENING, .t=tick/15.0f, .mode_t=tick/15.0f,
                      .level=(tick%2) ? 1 : 0};
        muse_pixel_render(&p);
        muse_pixel_scale(full, 64, 0, 63, 0, 63);
        assert(memcmp(full, tayne_sprites[TAYNE_LISTENING_FIRST+tick%TAYNE_LISTENING_COUNT], 4096*2)==0);
    }
    /* Speaking advances even when the device's audio meter stays at zero.
     * Use a nonzero device uptime and verify two separate entries into the mode. */
    const float speech_levels[]={0, 0.01f, 0.08f, 0.8f};
    for (unsigned level=0; level<sizeof(speech_levels)/sizeof(speech_levels[0]); level++) {
        for (int entry=0; entry<2; entry++) {
            muse_pose_t idle={.mode=MUSE_MODE_IDLE, .t=100+entry*5};
            muse_pixel_render(&idle);
            unsigned first_hash=0;
            int changed=0;
            for (int tick=0; tick<48; tick++) {
                muse_pose_t p={.mode=MUSE_MODE_SPEAKING, .t=100+entry*5+tick/15.0f,
                              .mode_t=tick/15.0f, .level=speech_levels[level]};
                muse_pixel_render(&p);
                muse_pixel_scale(full, 64, 0, 63, 0, 63);
                assert(memcmp(full, tayne_sprites[TAYNE_FRONT_FIRST+tick%TAYNE_FRONT_COUNT], 4096*2)==0);
                unsigned hash=0;
                for (int i=0; i<4096; i++) hash=hash*33u+full[i];
                if (!tick) first_hash=hash;
                else if (hash!=first_hash) changed++;
            }
            assert(changed>24);
            idle.t+=4; idle.mode_t=0;
            muse_pixel_render(&idle);
            muse_pixel_scale(full, 64, 0, 63, 0, 63);
            assert(memcmp(full, tayne_sprites[TAYNE_IDLE_FIRST],4096*2)==0);
        }
    }
    /* Thinking follows the second filmed dance, with dots below his boots. */
    for (int tick=0; tick<40; tick++) {
        muse_pose_t p={.mode=MUSE_MODE_THINKING, .t=tick/15.0f, .mode_t=tick/15.0f};
        muse_pixel_render(&p);
        muse_pixel_scale(full, 64, 0, 63, 0, 63);
        assert(memcmp(full, tayne_sprites[TAYNE_THINKING_FIRST+tick%TAYNE_THINKING_COUNT], 64*62*2)==0);
        for (int x=0; x<64; x++) for (int y=62; y<64; y++) {
            assert((full[y*64+x] != 0) == (x==26 || x==31 || x==36));
        }
    }
    /* Celery Man uses the approved consecutive video frames in every active
     * state, even at zero audio level and after re-entering a state. */
    assert(muse_character_select(1));
    for (int entry=0; entry<2; entry++) {
        for (int mode=MUSE_MODE_IDLE; mode<=MUSE_MODE_SPEAKING; mode++) {
            for (int tick=0; tick<72; tick++) {
                muse_pose_t p={.mode=mode, .t=500+entry*20+tick/15.0f,
                              .mode_t=tick/15.0f, .level=entry ? 0.8f : 0};
                muse_pixel_render(&p);
                muse_pixel_scale(full,64,0,63,0,63);
                int first=(mode==MUSE_MODE_LISTENING || mode==MUSE_MODE_SPEAKING)
                    ? CELERY_MAN_SHUFFLE_FIRST : CELERY_MAN_IDLE_FIRST;
                int rows=mode==MUSE_MODE_THINKING ? 62 : 64;
                assert(memcmp(full,celery_man_sprites[first+tick%24],64*rows*2)==0);
            }
        }
    }
    for (int entry=0; entry<2; entry++) {
        muse_pose_t p={.mode=MUSE_MODE_IDLE,.t=1000+entry*10};
        muse_pixel_render(&p);
        for (int tick=0; tick<48; tick++) {
            /* Sample inside each frame: uptime subtraction loses precision. */
            p.t=1000+entry*10+(tick ? tick+0.25f : 0)/15.0f; p.mode_t=tick/15.0f; p.happy=1;
            muse_pixel_render(&p);
            muse_pixel_scale(full,64,0,63,0,63);
            for (int y=0; y<64; y++) for (int x=0; x<64; x++) {
                if ((x>=12 && x<=14 && y>=13 && y<=21) ||
                    (x>=50 && x<=52 && y>=19 && y<=27)) continue;
                assert(full[y*64+x]==celery_man_sprites[CELERY_MAN_HAPPY_FIRST+tick%24][y*64+x]);
            }
        }
        p.happy=0; p.mode_t=0;
        muse_pixel_render(&p);
        muse_pixel_scale(full,64,0,63,0,63);
        assert(memcmp(full,celery_man_sprites[CELERY_MAN_IDLE_FIRST],4096*2)==0);
    }
    /* Return to the default repeatedly after rendering each custom character. */
    muse_pixel_set_size(64);
    for (int i=0; i<3; i++) {
        muse_pose_t p={.mode=MUSE_MODE_IDLE, .t=12, .mode_t=1};
        assert(muse_character_select(i));
        muse_pixel_render(&p);
        assert(muse_character_select(MUSE_CHARACTER_DEFAULT));
        assert(muse_character_current() == MUSE_CHARACTER_DEFAULT);
        muse_pixel_render(&p);
        muse_pixel_scale(full, 64, 0, 63, 0, 63);
        muse_default_scale(strip, 64, 0, 63, 0, 15);
        assert(memcmp(full, strip, 64*16*2)==0);
    }
    puts("Four avatars, default-renderer equivalence, switching, seven modes and fourteen strip sizes verified.");
    return 0;
}
