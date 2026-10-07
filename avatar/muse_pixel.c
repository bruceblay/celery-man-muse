/* Celery Man character pack for Muse. Custom artwork with native Muse poses.
 * Source sheets and prompts live in the sibling character directories.
 */
#include "muse_pixel.h"
#include <math.h>
#include <string.h>
#include "tayne/sprites.h"
#include "celery-man/sprites.h"
#include "oyster/sprites.h"
#include "characters.h"
#ifdef ESP_PLATFORM
#include "nvs.h"
#include "esp_log.h"
#endif

static const int hat_wobble[] = {8,9,8,10,8,11,0,11};
static const int celebration[] = {8,9,10,9,10,11,8,11};
static const struct {
    const char *id, *name;
    const uint16_t (*frames)[4096];
    const int *happy;
    float period;
    uint32_t accent;
} characters[] = {
    {"tayne", "Tayne", tayne_sprites, hat_wobble, 2.0f, 0xf3c971},
    {"celery-man", "Celery Man", celery_man_sprites, celebration, 2.4f, 0xb6d9e9},
    {"oyster", "Oyster", oyster_sprites, celebration, 1.6f, 0xf17d79},
};
static int character;
static bool loaded;
#ifdef ESP_PLATFORM
static nvs_handle_t character_nvs;
static bool nvs_ready;
#endif

static uint16_t pixels[MUSE_PX_W * MUSE_PX_H];
static int size = MUSE_PX_W * 2;
static float pet_started;
static float last_t;
static bool was_happy;

int muse_character_count(void) { return (int)(sizeof(characters)/sizeof(characters[0])); }
const char *muse_character_name(int index)
{
    return index >= 0 && index < muse_character_count() ? characters[index].name : "Unknown";
}
int muse_character_current(void)
{
    if (!loaded) {
        loaded = true;
#ifdef ESP_PLATFORM
        nvs_ready = nvs_open("muse_avatar", NVS_READWRITE, &character_nvs) == ESP_OK;
        if (nvs_ready) {
            char id[32];
            size_t size = sizeof(id);
            if (nvs_get_str(character_nvs, "character", id, &size) == ESP_OK) {
                for (int i=0; i<muse_character_count(); i++) {
                    if (!strcmp(id, characters[i].id)) { character = i; break; }
                }
            }
        }
        ESP_LOGI("muse_avatar", "loaded %s", characters[character].name);
#endif
    }
    return character;
}
bool muse_character_select(int index)
{
    if (index < 0 || index >= muse_character_count()) return false;
    if (index == muse_character_current()) return true;
#ifdef ESP_PLATFORM
    if (!nvs_ready) nvs_ready = nvs_open("muse_avatar", NVS_READWRITE, &character_nvs) == ESP_OK;
    if (!nvs_ready || nvs_set_str(character_nvs, "character", characters[index].id) != ESP_OK ||
        nvs_commit(character_nvs) != ESP_OK) {
        ESP_LOGE("muse_avatar", "could not save character selection");
        return false;
    }
    ESP_LOGI("muse_avatar", "selected %s", characters[index].name);
#endif
    character = index;
    was_happy = false;
    return true;
}

static float clamp01(float v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
static uint16_t rgb565(uint32_t c)
{
    return (uint16_t)(((c >> 8) & 0xf800) | ((c >> 5) & 0x07e0) | ((c >> 3) & 31));
}
static void dot(int x, int y, uint16_t color)
{
    if (x >= 0 && x < MUSE_PX_W && y >= 0 && y < MUSE_PX_H)
        pixels[y * MUSE_PX_W + x] = color;
}
static void sparkle(int x, int y, uint16_t c)
{
    dot(x, y, c); dot(x-1, y, c); dot(x+1, y, c);
    dot(x, y-1, c); dot(x, y+1, c);
}
static uint16_t dim(uint16_t c, float amount)
{
    return (uint16_t)(((int)(((c >> 11) & 31) * amount) << 11) |
                     ((int)(((c >> 5) & 63) * amount) << 5) |
                     (int)((c & 31) * amount));
}

uint32_t muse_pixel_accent(muse_mode_t mode)
{
    switch (mode) {
    case MUSE_MODE_LISTENING: return 0x67daca;
    case MUSE_MODE_THINKING: return 0xc2a1ff;
    case MUSE_MODE_SPEAKING: return characters[muse_character_current()].accent;
    case MUSE_MODE_ERROR: return 0xf17d79;
    case MUSE_MODE_OFF: return 0x8791a5;
    default: return characters[muse_character_current()].accent;
    }
}

void muse_pixel_render(const muse_pose_t *p)
{
    if (!p) return;
    int selected = muse_character_current();
    float t = fmaxf(0, p->t), mt = fmaxf(0, p->mode_t);
    float level = clamp01(p->level);
    bool happy = p->happy > 0 && p->mode != MUSE_MODE_OFF && p->mode != MUSE_MODE_ERROR;
    if (t < last_t) was_happy = false;
    if (happy && !was_happy) pet_started = t;
    was_happy = happy;
    last_t = t;
    int frame = 0, dy = 0;
    float light = 1;
    switch (p->mode) {
    case MUSE_MODE_BOOT:
        frame = 15;
        dy = (int)(12 * (1 - clamp01(mt / 0.8f)));
        light = clamp01(mt / 0.6f);
        break;
    case MUSE_MODE_IDLE:
        frame = (int)(fmodf(t, characters[selected].period) * 8 / characters[selected].period) % 8;
        break;
    case MUSE_MODE_LISTENING:
        frame = level > 0.35f ? 13 : 12;
        break;
    case MUSE_MODE_THINKING:
        frame = 15;
        break;
    case MUSE_MODE_SPEAKING:
        frame = level > 0.13f ? 14 : 15;
        dy = level > 0.7f ? -1 : 0;
        break;
    case MUSE_MODE_ERROR:
        frame = 15;
        light = 0.65f;
        break;
    case MUSE_MODE_OFF:
        frame = 8;
        light = 1 - clamp01(mt / 1.2f);
        dy = (int)(clamp01(mt / 1.2f) * 5);
        break;
    default: frame = 15; break;
    }
    if (happy) {
        int step = (int)(fmodf(fmaxf(0, t-pet_started), 1.6f) * 5);
        frame = characters[selected].happy[step < 8 ? step : 7];
    }
    memset(pixels, 0, sizeof(pixels));
    for (int y = 0; y < MUSE_PX_H; y++) {
        int sy = y - dy;
        if (sy < 0 || sy >= MUSE_PX_H) continue;
        for (int x = 0; x < MUSE_PX_W; x++) {
            uint16_t c = characters[selected].frames[frame][sy * MUSE_PX_W + x];
            pixels[y * MUSE_PX_W + x] = light < 1 ? dim(c, light) : c;
        }
    }
    uint16_t accent = rgb565(muse_pixel_accent(p->mode));
    if (p->mode == MUSE_MODE_THINKING && !happy) {
        int phase = (int)(fmodf(mt, 1.2f) / 0.4f);
        for (int i = 0; i < 3; i++) {
            uint16_t c = i == phase ? accent : dim(accent, 0.25f);
            dot(46+i*4, 12, c); dot(46+i*4, 13, c);
        }
    }
    if (p->mode == MUSE_MODE_ERROR) {
        for (int y=12; y<17; y++) dot(51, y, accent);
        dot(51, 19, accent);
    }
    if (happy) {
        float age = fmaxf(0, t - pet_started);
        int lift = (int)(fmodf(age, 0.8f) * 7);
        sparkle(13, 20-lift, rgb565(0xf3c971));
        sparkle(51, 26-lift, rgb565(0xf3c971));
    }
}

void muse_pixel_set_size(int px) { size = px < 1 ? 1 : px > 512 ? 512 : px; }

void muse_pixel_scale(uint16_t *dst, int stride_px, int x0, int x1, int y0, int y1)
{
    if (!dst || stride_px < x1-x0+1 || x0 > x1 || y0 > y1) return;
    for (int y=y0; y<=y1; y++) {
        for (int x=x0; x<=x1; x++) {
            uint16_t c = 0;
            if (x >= 0 && x < size && y >= 0 && y < size)
                c = pixels[(y * MUSE_PX_H / size) * MUSE_PX_W + x * MUSE_PX_W / size];
            dst[(y-y0)*stride_px + x-x0] = c;
        }
    }
}
