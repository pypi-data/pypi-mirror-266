import os
from PIL import Image, UnidentifiedImageError
import imagehash
from prusek_spheroid import file_management as fm


def count_bmp_files(directory):
    """Count the number of .bmp files in directory and its subdirectories."""
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.bmp'):
                count += 1
    return count


def copy_and_rename_bmp_files(root_dir, output_dir, progress_callback):
    # Prepare the output directory
    fm.create_directory(output_dir, delete=True)

    # Count total .bmp files to process for progress tracking
    total_files = count_bmp_files(root_dir)
    processed_files = 0

    # Dictionary to store image hash values
    hash_dict = {}

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.bmp'):
                processed_files += 1
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, root_dir)
                new_file_name = relative_path.replace(os.path.sep, '_') + '_' + file
                output_file_path = os.path.join(output_dir, new_file_name.replace(".bmp", ".png"))

                try:
                    # Open and resize the image
                    with Image.open(file_path) as img:
                        img_resized = img.resize((1000, 1000), Image.LANCZOS)  # High-quality resize
                        image_hash = imagehash.average_hash(img_resized, hash_size=32)

                        # Check if the hash already exists in hash_dict
                        if image_hash not in hash_dict:
                            try:
                                img_resized.save(output_file_path)
                                print(output_file_path)# Attempt to save resized image
                                hash_dict[image_hash] = output_file_path
                                save_status = 'Saved successfully.'
                            except IOError as save_error:
                                save_status = f'Failed to save: {save_error}'
                            progress_msg = save_status
                        else:
                            progress_msg = f'Duplicate found, not copying {file}.'

                except UnidentifiedImageError as e:
                    progress_msg = f'Error opening {file_path}: {e}. File skipped.'

                # Update progress
                if progress_callback:
                    progress_callback(processed_files, total_files, progress_msg)

