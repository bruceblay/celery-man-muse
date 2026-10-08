# Artwork

## Tayne

All of Tayne's poses use actual frames from the [supplied sketch](https://www.youtube.com/watch?v=a8K6QUPmv8Q).

| Animation | Video segment | Samples | Sprite sheet |
| --- | --- | --- | --- |
| Idle: low, wide-legged bounce | 1:06.65–1:08.25 | 24 | [video-idle.png](avatar/tayne/video-idle.png) |
| Happy: Flarhgunnstow | 1:14.40–1:16.00 | 24 | [video-happy.png](avatar/tayne/video-happy.png) |
| Listening: sideways arm swing | 1:02.03–1:02.83 | 12 | [video-listening.png](avatar/tayne/video-listening.png) |
| Thinking: raised-arm kicks | 1:12.80–1:13.47 | 10 | [video-thinking.png](avatar/tayne/video-thinking.png) |
| Speaking: frontal greeting | 0:56.50–0:57.30 | 12 | [video-front.png](avatar/tayne/video-front.png) |

Each sequence uses consecutive samples at 15 fps. Backgrounds are removed before scaling onto a black 64×64 canvas. Recorded masks remove the old window edges around the extended hands and boots. The portrait mask preserves enclosed highlights such as reflections in the sunglasses. The approved idle and happy sheets are unchanged.

Frame order and cadence follow the footage, with no generated dance poses, added mirroring, or invented transitions. These short excerpts repeat as loops; their ends are not blended. Clipping already present in the source remains. Speaking loops while Muse is in speaking mode, independently of the audio meter. It does not track individual phonemes. Boot, error, and off use a filmed neutral frame.

[video-clips.json](avatar/tayne/video-clips.json) records timestamps, crops, keys, and masks. With FFmpeg, Pillow, and a local 1920×1080 copy of the video, rebuild the sheets with:

```sh
python3 avatar/tayne/extract_video.py /path/to/video.mp4
python3 avatar/tayne/pack_sprites.py
```

For an input trimmed to start at a known source timestamp, pass `--source-start SECONDS`. Use `--clip listening` to rebuild one sequence. The video and its audio are not included in this repository.

## Generated poses

The Celery Man and Oyster sheets were created with OpenAI's built-in image generator from costume references in the sketch. These are generated reinterpretations.

| Character | Original sheet | Exact generation prompt | Costume reference |
| --- | --- | --- | --- |
| Celery Man | [source.png](avatar/celery-man/source.png) | [prompt](avatar/celery-man/imagegen-prompt.txt) | Around 0:24; gray suit, white shirt, dark tie |
| Oyster | [source.png](avatar/oyster/source.png) | [prompt](avatar/oyster/imagegen-prompt.txt) | Around 0:41–0:46; red hoodie and beanie, black tee and trousers |

The original sheets contain sixteen frames each. All frames are packed as RGB565 in `sprites.h`; no image-generation service is needed to build or run the firmware. GIF previews come from the native renderer.

The Apache license covers the code, not the source-video images or third-party character, likeness, and trademark rights. This is an unofficial fan project with no endorsement by the sketch's creators or rights holders. See [NOTICE](NOTICE).
