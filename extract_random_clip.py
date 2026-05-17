import ffmpeg
import random
import sys
import os
import math
import datetime

def get_video_duration(input_filepath):
    """Gets the duration of a video file using ffprobe."""
    try:
        # ffprobe is part of the ffmpeg package
        probe = ffmpeg.probe(input_filepath)
        # The duration is in the 'format' section
        duration_str = probe['format']['duration']
        return float(duration_str)
    except ffmpeg.Error as e:
        print(f"Error probing video: {e.stderr.decode()}")
        return None
    except FileNotFoundError:
        print("Error: ffprobe command not found. Make sure FFmpeg is installed and in your system's PATH.")
        return None
    except KeyError:
        # Handle cases where duration might not be in the expected location (less common)
        # print(f"Could not find duration information in probe results for {input_filepath}")
        # return None # Or try another key if known
        pass # Let probe error message handle it if it's really missing format data
    except ValueError:
        # print(f"Could not parse duration '{duration_str}' as a number.")
        pass # Let probe error message handle it


def extract_and_convert_portrait_clip(input_filepath, output_filepath, clip_duration_seconds, target_width, target_height):
    """
    Extracts a random clip of specified duration and converts it to a portrait aspect ratio.
    """

    total_duration = get_video_duration(input_filepath)

    if total_duration is None:
        print("Could not get video duration. Skipping extraction.")
        return False

    print(f"Total video duration: {total_duration:.2f} seconds")

    # Calculate the maximum possible start time
    max_start_time = total_duration - clip_duration_seconds

    if max_start_time < 0:
        print(f"Error: Video ({total_duration:.2f}s) is shorter than the requested clip duration ({clip_duration_seconds}s). Cannot extract.")
        return False

    # Generate a random start time
    random_start_time = random.uniform(0, max_start_time)

    # Ensure the start time is within valid bounds
    random_start_time = max(0, min(random_start_time, max_start_time))

    print(f"Random start time selected: {random_start_time:.2f} seconds")

    # --- FFmpeg Filter for Portrait Conversion ---
    # Scale the video so its height matches the target height, maintaining aspect ratio.
    # '-2' means FFmpeg calculates the value to maintain aspect ratio and ensure it's divisible by 2.
    # Then, crop the center part to the target width and height.
    # This assumes the input is landscape and you want to crop the sides for portrait.
    # If input is already portrait or square, this might behave differently.
    video_filter = f"scale=-2:{target_height},crop={target_width}:{target_height}"

    # Use FFmpeg to extract, filter, and re-encode the clip
    try:
        print(f"Attempting to extract clip from {random_start_time:.2f}s for {clip_duration_seconds}s and convert to {target_width}x{target_height} to {output_filepath}...")
        print("Note: This requires video re-encoding and will take longer than copying.")

        (
            ffmpeg
            .input(input_filepath, ss=random_start_time)
            .output(
                output_filepath,
                t=clip_duration_seconds, # Duration of the output clip
                vf=video_filter,       # Apply the video filter
                acodec='copy',         # Copy the audio stream without re-encoding (faster)
                crf=23,                # Constant Rate Factor for video quality (lower=higher quality/larger file)
                preset='medium'        # Encoding speed vs compression efficiency (ultrafast, superfast, fast, medium, slow, etc.)
            )
            # .global_args('-loglevel', 'info') # Uncomment for more FFmpeg output
            .run(overwrite_output=True, capture_stderr=True)
        )
        print(f"Successfully extracted and converted clip to {output_filepath}")
        return True

    except ffmpeg.Error as e:
        print(f"Error during FFmpeg execution for {output_filepath}:\n{e.stderr.decode()}")
        # Check if the error might be due to the input video being too short for the filter?
        # Or input resolution too small for scaling? The scale filter should handle this
        # gracefully, but it's a possibility.
        return False
    except FileNotFoundError:
        print("Error: FFmpeg command not found. Make sure FFmpeg is installed and in your system's PATH.")
        return False

# --- Script Usage ---
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python extract_timed_portrait_clips.py <input_video_path> <output_base_directory> <number_of_clips>")
        print("Example: python extract_timed_portrait_clips.py \"C:\\expi2\\bg video\\my_footage.mp4\" \"C:\\expi2\\generated_shorts\" 5")
        sys.exit(1)

    input_video_path = sys.argv[1]
    output_base_directory = sys.argv[2]
    num_clips_str = sys.argv[3]

    desired_clip_duration = 60  # seconds
    target_portrait_width = 1080
    target_portrait_height = 1920 # Standard 9:16 HD portrait

    # --- Validation ---
    # Check if input file exists
    if not os.path.exists(input_video_path):
        print(f"Error: Input file not found at {input_video_path}")
        sys.exit(1)

    # Validate number of clips
    try:
        num_clips = int(num_clips_str)
        if num_clips <= 0:
            print("Error: Number of clips must be a positive integer.")
            sys.exit(1)
    except ValueError:
        print("Error: Number of clips must be an integer.")
        sys.exit(1)

    # Ensure output base directory exists
    if not os.path.exists(output_base_directory):
        try:
            os.makedirs(output_base_directory)
            print(f"Created output base directory: {output_base_directory}")
        except OSError as e:
            print(f"Error creating output base directory {output_base_directory}: {e}")
            sys.exit(1)
    elif not os.path.isdir(output_base_directory):
         print(f"Error: Output base path '{output_base_directory}' exists but is not a directory.")
         sys.exit(1)

    # --- Create Timestamped Output Subdirectory ---
    # Get current time and format it into a string for a directory name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # e.g., 20231027_143005
    # Add target resolution to the folder name for clarity
    timestamped_output_directory = os.path.join(output_base_directory, f"clips_{timestamp}_{target_portrait_width}x{target_portrait_height}")

    # Create the timestamped directory
    try:
        os.makedirs(timestamped_output_directory, exist_ok=True)
        print(f"Created timestamped output directory: {timestamped_output_directory}")
    except OSError as e:
        print(f"Error creating timestamped output directory {timestamped_output_directory}: {e}")
        sys.exit(1)

    # Get base filename and extension for naming clips
    input_basename = os.path.basename(input_video_path)
    name_without_ext, file_extension = os.path.splitext(input_basename)
    # Clean up potential leading dot from extension if present (e.g., '.mp4' -> 'mp4')
    if file_extension.startswith('.'):
        file_extension = file_extension[1:]


    print(f"\nExtracting and converting {num_clips} random {desired_clip_duration}-second clips from '{input_basename}' to {target_portrait_width}x{target_portrait_height} portrait.")
    print(f"Saving clips to unique directory: '{timestamped_output_directory}'")
    print("-" * 30)
    print(">>> WARNING: Video re-encoding is required for this conversion.")
    print(">>> This will take significant time and CPU resources.")
    print("-" * 30)


    # --- Loop and Extract ---
    successful_extractions = 0
    for i in range(1, num_clips + 1):
        # Generate output filename using counter and original extension
        output_filename = f"{name_without_ext}_clip_{i}.{file_extension}" # e.g., my_footage_clip_1.mp4

        # Build the full output path (directory + filename)
        output_filepath = os.path.join(timestamped_output_directory, output_filename)

        print(f"\n--- Processing clip {i} of {num_clips} ---")
        # Call the extraction and conversion function
        if extract_and_convert_portrait_clip(
            input_video_path,
            output_filepath,
            desired_clip_duration,
            target_portrait_width,
            target_portrait_height
        ):
             successful_extractions += 1
        else:
             print(f"Processing of clip {i} failed.")


    print("\n--- Process Summary ---")
    print(f"Attempted to process {num_clips} clips.")
    print(f"Successfully processed {successful_extractions} clips.")
    if successful_extractions < num_clips:
        print("Some extractions failed. Check the error messages above.")
        sys.exit(1) # Exit with a non-zero code to indicate partial failure
    else:
        sys.exit(0) # Exit with zero to indicate success