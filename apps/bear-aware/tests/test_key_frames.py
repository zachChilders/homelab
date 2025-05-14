import os

import pytest

from src.video_processor import extract_key_frames


def test_extract_key_frames():
    # Test video path
    video_path = "tests/files/bear.mov"
    output_dir = "tests/output/key_frames"

    # Clean up any existing output directory
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))
        os.rmdir(output_dir)

    # Extract key frames
    num_frames = extract_key_frames(
        video_path=video_path,
        output_dir=output_dir,
        rel_threshold=1.5,
        abs_threshold=0.5,
        min_time_diff=0.5
    )

    # Verify that frames were extracted
    assert num_frames == 4, "No frames were extracted"
    assert os.path.exists(output_dir), "Output directory was not created"

    # Verify the number of output files matches the number of frames
    output_files = sorted(os.listdir(output_dir))
    assert len(output_files) == num_frames, "Number of output files doesn't match returned frame count"

def test_extract_key_frames_invalid_path():
    # Test with invalid video path
    with pytest.raises(ValueError):
        extract_key_frames("nonexistent.mp4")
