from tap import Tap
from typing import Optional, List
import moviepy.editor as mp
import pathlib
import math
from video_montage.utils import create_video_clips, datetime_str, overlay_text_on_clip


class ArgumentParser(Tap):
    input_video_folder_path: pathlib.Path
    output_video_folder_path: pathlib.Path = pathlib.Path(".")
    output_video_filename: Optional[str] = None
    max_n_videos: Optional[int] = None
    max_duration_seconds: Optional[int] = None
    fps: Optional[int] = None
    num_per_row: Optional[int] = None
    overlay_filename: bool = False

    @property
    def output_video_filepath(self) -> pathlib.Path:
        if self.output_video_filename is None:
            filename = f"{self.input_video_folder_path.name}_{datetime_str()}_video_grid_montage.mp4"
        else:
            filename = self.output_video_filename
        return self.output_video_folder_path / filename


def trim_video_clips(
    video_clips: List[mp.VideoFileClip], max_duration_seconds: Optional[int] = None
) -> List[mp.VideoFileClip]:
    shortest_duration_seconds = min([video_clip.duration for video_clip in video_clips])
    montage_duration_seconds = (
        min(shortest_duration_seconds, max_duration_seconds)
        if max_duration_seconds is not None
        else shortest_duration_seconds
    )
    video_clips = [
        video_clip.subclip(0, montage_duration_seconds) for video_clip in video_clips
    ]
    return video_clips


def main() -> None:
    args: ArgumentParser = ArgumentParser().parse_args()
    assert (
        args.input_video_folder_path.exists()
    ), f"Input video folder path {args.input_video_folder_path} does not exist."

    if not args.output_video_folder_path.exists():
        print(f"Creating output folder {args.output_video_folder_path}")
        args.output_video_folder_path.mkdir(parents=True)

    video_clips = create_video_clips(
        args.input_video_folder_path, max_n_videos=args.max_n_videos
    )
    video_clips = trim_video_clips(
        video_clips, max_duration_seconds=args.max_duration_seconds
    )
    num_videos = len(video_clips)

    if args.overlay_filename:
        video_clips = [
            overlay_text_on_clip(
                clip=video_clip, text=pathlib.Path(video_clip.filename).name
            )
            for video_clip in video_clips
        ]

    DEFAULT_NUM_PER_ROW = math.ceil(math.sqrt(num_videos))
    num_per_row = (
        args.num_per_row if args.num_per_row is not None else DEFAULT_NUM_PER_ROW
    )
    num_rows = math.ceil(num_videos / num_per_row)

    num_slots = num_per_row * num_rows
    num_empty_slots = num_slots - num_videos
    BLACK = (0, 0, 0)
    video_clips += [
        mp.ColorClip(
            size=video_clips[0].size,
            color=BLACK,
            duration=video_clips[0].duration,
        )
        for _ in range(num_empty_slots)
    ]
    assert len(video_clips) == num_slots, f"{len(video_clips)} != {num_slots}"

    video_grid = mp.clips_array(
        [video_clips[i * num_per_row : (i + 1) * num_per_row] for i in range(num_rows)]
    )

    fps = args.fps if args.fps is not None else video_clips[0].fps
    video_grid.write_videofile(
        str(args.output_video_filepath),
        fps=fps,
    )


if __name__ == "__main__":
    main()
