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

## Celery Man

Celery Man uses three consecutive video excerpts from the same sketch:

| Animation | Video segment | Samples | Sprite sheet |
| --- | --- | --- | --- |
| Hip sway: idle and thinking | 0:23.40–0:25.00 | 24 | [video-hip-sway.png](avatar/celery-man/video-hip-sway.png) |
| Raised-fist shuffle: listening and speaking | 0:28.03–0:29.63 | 24 | [video-raised-fists.png](avatar/celery-man/video-raised-fists.png) |
| 4d3d3: happy | 0:37.43–0:39.03 | 24 | [video-4d3d3.png](avatar/celery-man/video-4d3d3.png) |

The loops run at 15 fps, preserving source order and timing. A narrow background key retains the hand highlights. Recorded masks protect white fabric, including the two 4d3d3 frames where the shirt meets the pale background. Masks restore source pixels; they do not redraw the dancer. GIF previews use a shared palette without dithering.

[source-clips.json](avatar/celery-man/source-clips.json) records the extraction settings. With FFmpeg, Pillow, and a local 1920×1080 copy of the video:

```sh
python3 avatar/celery-man/extract_video.py /path/to/video.mp4
python3 avatar/celery-man/pack_sprites.py
python3 avatar/tayne/export_preview.py --character celery-man
```

For a trimmed source, pass `--source-start SECONDS` to the extractor. The three sheets pack into seventy-two RGB565 frames. The earlier generated [source sheet](avatar/celery-man/source.png) and [prompt](avatar/celery-man/imagegen-prompt.txt) remain as history; the firmware uses the video sheets.

## Oyster

Oyster uses four consecutive video excerpts from the same sketch:

| Animation | Video segment | Samples | Sprite sheet |
| --- | --- | --- | --- |
| Headbang: idle | 0:40.00–0:40.53 | 8 | [video-headbang.png](avatar/oyster/video-headbang.png) |
| Arms back: listening | 0:41.00–0:41.67 | 10 | [video-arms-back.png](avatar/oyster/video-arms-back.png) |
| Greeting: speaking and happy | 0:39.03–0:39.57 | 8 | [video-greeting.png](avatar/oyster/video-greeting.png) |
| Printout: thinking | 0:44.55–0:46.42 | 28 | [video-printout.png](avatar/oyster/video-printout.png) |

The loops run at 15 fps in source order. Thinking plays the whole printout, holds the finished smile for 0.6 seconds, then prints again. The printout extractor tracks the upper paper edge to remove the rear tray and room, keeping the paper, portrait, and printer lip. GIF previews use a shared palette without dithering.

[source-clips.json](avatar/oyster/source-clips.json) and [printout-source.json](avatar/oyster/printout-source.json) record the extraction settings. With FFmpeg, Pillow, NumPy, and a local 1920×1080 copy of the video:

```sh
python3 avatar/oyster/extract_video.py /path/to/video.mp4
python3 avatar/oyster/extract_print.py /path/to/video.mp4
python3 avatar/oyster/pack_sprites.py
python3 avatar/tayne/export_preview.py --character oyster
```

The four sheets pack into fifty-four RGB565 frames. The earlier generated [source sheet](avatar/oyster/source.png) and [prompt](avatar/oyster/imagegen-prompt.txt) remain as history; the firmware uses the video sheets.

The Apache license covers the code, not the source-video images or third-party character, likeness, and trademark rights. This is an unofficial fan project with no endorsement by the sketch's creators or rights holders. See [NOTICE](NOTICE).
