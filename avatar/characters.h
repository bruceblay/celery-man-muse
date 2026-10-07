#pragma once
#include <stdbool.h>

/* Keep existing saved character indices stable; the default pet is appended. */
enum { MUSE_CHARACTER_DEFAULT = 3 };

/* Optional custom-avatar roster. Menu and renderer call these on the UI task. */
int muse_character_count(void);
int muse_character_current(void);
const char *muse_character_name(int index);
bool muse_character_select(int index);
