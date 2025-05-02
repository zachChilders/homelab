import os

import cv2
import numpy as np


def extract_key_frames(video_path: str, output_dir: str = "key_frames", abs_threshold: float = 0.85, rel_threshold: float = 1.5, min_time_diff: float = 0.5, window_size: int = 10):
    """
    Extract key frames from a video file using perceptual hash comparison with both absolute and relative thresholds.
    
    Args:
        video_path (str): Path to the input video file
        output_dir (str): Directory to save the extracted frames
        abs_threshold (float): Absolute similarity threshold (0-1). Lower values mean more key frames
        rel_threshold (float): Relative threshold multiplier for detecting significant changes
        min_time_diff (float): Minimum time difference between key frames in seconds
        window_size (int): Number of recent frames to consider for relative threshold calculation
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    min_frames_diff = int(fps * min_time_diff)

    frame_count = 0
    saved_count = 0
    prev_frame = None
    prev_hash = None
    last_key_frame = -min_frames_diff  # Initialize to allow first frame

    # Initialize sliding window for recent similarities
    recent_similarities = []

    def compute_phash(image):
        """Compute perceptual hash of an image."""
        # Convert to grayscale and resize to 32x32
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (32, 32))

        # Compute DCT transform
        dct = cv2.dct(np.float32(resized))
        dct_low = dct[:8, :8]

        # Compute average value (excluding first term)
        avg = (dct_low[0, 1:].sum() + dct_low[1:].sum()) / 63

        # Create binary hash
        return dct_low >= avg

    def hash_similarity(hash1, hash2):
        """Compute similarity between two perceptual hashes."""
        return 1 - np.count_nonzero(hash1 != hash2) / hash1.size

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # For the first frame, save it and continue
        if prev_frame is None:
            output_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            prev_frame = frame
            prev_hash = compute_phash(frame)
            last_key_frame = frame_count
            frame_count += 1
            continue

        # Compute hash of current frame
        curr_hash = compute_phash(frame)

        # Compare hashes
        similarity = hash_similarity(curr_hash, prev_hash)

        # Update sliding window
        recent_similarities.append(similarity)
        if len(recent_similarities) > window_size:
            recent_similarities.pop(0)

        # Calculate mean and standard deviation of recent similarities
        if len(recent_similarities) >= 2:
            mean_sim = np.mean(recent_similarities)
            std_sim = np.std(recent_similarities)
            z_score = (similarity - mean_sim) / std_sim if std_sim > 0 else 0
        else:
            mean_sim = similarity
            std_sim = 0
            z_score = 0

        # Determine if this is a key frame based on both thresholds
        is_key_frame = False

        # Check absolute threshold
        if similarity < abs_threshold:
            is_key_frame = True

        # Check relative threshold (if we have enough history)
        if len(recent_similarities) >= 2 and z_score < -rel_threshold:
            is_key_frame = True

        # Save frame if it's a key frame and enough time has passed
        if is_key_frame and (frame_count - last_key_frame) >= min_frames_diff:
            output_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            last_key_frame = frame_count

        # Always update previous frame and hash
        prev_frame = frame
        prev_hash = curr_hash
        frame_count += 1

    cap.release()
    return saved_count
