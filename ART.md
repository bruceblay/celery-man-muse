# Artwork

The three source sheets were created with OpenAI's built-in image generator
from costume references viewed in the [supplied sketch](https://www.youtube.com/watch?v=a8K6QUPmv8Q).
They are generated reinterpretations, not extracted video frames. Reference
screenshots, audio, and video are not included in this repository.

| Character | Original sheet | Exact generation prompt | Costume reference |
| --- | --- | --- | --- |
| Tayne | [source.png](avatar/tayne/source.png) | [prompt](avatar/tayne/imagegen-prompt.txt) | Around 0:58; fedora, sunglasses, gold shirt |
| Tayne dance | [dance.png](avatar/tayne/dance.png) | [prompt](avatar/tayne/dance-prompt.txt) | Original Tayne sheet; shuffle and turning poses |
| Celery Man | [source.png](avatar/celery-man/source.png) | [prompt](avatar/celery-man/imagegen-prompt.txt) | Around 0:24; gray suit, white shirt, dark tie |
| Oyster | [source.png](avatar/oyster/source.png) | [prompt](avatar/oyster/imagegen-prompt.txt) | Around 0:41–0:46; red hoodie and beanie, black tee and trousers |

Each 4×4 sheet supplies sixteen frames, downsampled to 64×64 and converted
to RGB565 for the display. Tayne combines his original poses with the new dance sheet.
`sprites.h` files contain the ready-to-build
pixels. No image-generation service is needed to build or run the firmware.

The original sheets and prompts are kept so the visual design is inspectable.
GIFs are exported from the native renderer rather than independently animated.

The Apache code license does not grant rights to third-party characters,
likenesses, or trademarks depicted in the fan art. This is an unofficial
fan project, with no endorsement by the sketch's creators or rights holders.
