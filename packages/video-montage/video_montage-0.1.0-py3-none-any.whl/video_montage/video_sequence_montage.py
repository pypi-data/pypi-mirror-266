from tap import Tap
from typing import Optional
import moviepy.editor as mp
import pathlib
from video_montage.utils import create_video_clips, datetime_str, overlay_text_on_clip


class ArgumentParser(Tap):
    input_video_folder_path: pathlib.Path
    output_video_folder_path: pathlib.Path = pathlib.Path(".")
    output_video_filename: Optional[str] = None
    max_n_videos: Optional[int] = None
    fps: Optional[int] = None
    overlay_filename: bool = False

    @property
    def output_video_filepath(self) -> pathlib.Path:
        if self.output_video_filename is None:
            filename = f"{self.input_video_folder_path.name}_{datetime_str()}_video_sequence_montage.mp4"
        else:
            filename = self.output_video_filename
        return self.output_video_folder_path / filename


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

    if args.overlay_filename:
        video_clips = [
            overlay_text_on_clip(
                clip=video_clip, text=pathlib.Path(video_clip.filename).name
            )
            for video_clip in video_clips
        ]

    video_sequence = mp.concatenate_videoclips(video_clips, method="compose")

    fps = args.fps if args.fps is not None else video_clips[0].fps
    video_sequence.write_videofile(
        str(args.output_video_filepath),
        fps=fps,
    )


if __name__ == "__main__":
    main()
