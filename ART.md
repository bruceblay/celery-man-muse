# Artwork

## Tayne's dances

Tayne's idle and happy animations use actual frames from the [supplied sketch](https://www.youtube.com/watch?v=a8K6QUPmv8Q).

| Animation | Video segment | Sprite sheet |
| --- | --- | --- |
| Idle: low, wide-legged bounce | 1:06.65–1:08.25 | [video-idle.png](avatar/tayne/video-idle.png) |
| Happy: Flarhgunnstow | 1:14.40–1:16.00 | [video-happy.png](avatar/tayne/video-happy.png) |

Each sequence contains twenty-four consecutive samples at 15 fps. The window chrome is cropped out, the pale background is removed, and the dancer is scaled onto a black 64×64 canvas. Frame order and playback speed are preserved. There are no generated dance poses, mirrored poses, or invented transitions. Clipping at the original computer-window edges remains in the samples.

[video-clips.json](avatar/tayne/video-clips.json) records the timestamps and processing settings. With FFmpeg and a local 1920×1080 copy of the video, rebuild the sheets with:

```sh
python3 avatar/tayne/extract_video.py /path/to/video.mp4
python3 avatar/tayne/pack_sprites.py
```

For an input trimmed to start at a known source timestamp, pass `--source-start SECONDS`. The video and its audio are not included in this repository.

## Generated poses

Tayne's conversation poses and the Celery Man and Oyster sheets were created with OpenAI's built-in image generator from costume references in the sketch. These are generated reinterpretations.

| Character | Original sheet | Exact generation prompt | Costume reference |
| --- | --- | --- | --- |
| Tayne | [source.png](avatar/tayne/source.png) | [prompt](avatar/tayne/imagegen-prompt.txt) | Around 0:58; fedora, sunglasses, gold shirt |
| Celery Man | [source.png](avatar/celery-man/source.png) | [prompt](avatar/celery-man/imagegen-prompt.txt) | Around 0:24; gray suit, white shirt, dark tie |
| Oyster | [source.png](avatar/oyster/source.png) | [prompt](avatar/oyster/imagegen-prompt.txt) | Around 0:41–0:46; red hoodie and beanie, black tee and trousers |

The original sheets contain sixteen frames each. All frames are packed as RGB565 in `sprites.h`; no image-generation service is needed to build or run the firmware. GIF previews come from the native renderer.

The Apache license covers the code, not the source-video images or third-party character, likeness, and trademark rights. This is an unofficial fan project with no endorsement by the sketch's creators or rights holders. See [NOTICE](NOTICE).
