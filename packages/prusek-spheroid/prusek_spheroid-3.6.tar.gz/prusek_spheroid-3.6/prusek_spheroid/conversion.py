import os
import shutil
import cv2 as cv
import json as js
import numpy as np
from prusek_spheroid import file_management as fm

def create_directory(directory_path, delete=False):
    """Create or clear a directory."""
    if delete and os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    os.makedirs(directory_path, exist_ok=True)


def load_annotations_and_save(annotations_address, images_address, masks_output_path, images_output_path):
    with open(os.path.join(annotations_address, "instances_default.json")) as f:
        data = js.load(f)

    masks_per_image = {}  # Track masks to avoid recreating for each annotation

    # Prepare output directories
    create_directory(masks_output_path, delete=True)
    create_directory(images_output_path, delete=True)

    for annotation in data["annotations"]:
        img_id = annotation["image_id"]
        img_info = next((item for item in data["images"] if item["id"] == img_id), None)

        if img_info is not None:
            img_name = img_info["file_name"]
            img_width = img_info["width"]
            img_height = img_info["height"]

            img_path = os.path.join(images_address, img_name)
            img = cv.imread(img_path)

            # Initialize a mask for each image if not already done
            if img_name not in masks_per_image:
                masks_per_image[img_name] = np.zeros((img_height, img_width), dtype=np.uint8)

            # Create contours for each segmentation and apply them to the mask
            for segmentation in annotation["segmentation"]:
                polygon = np.array(segmentation, np.int32).reshape((-1, 1, 2))
                cv.fillPoly(masks_per_image[img_name], [polygon], 255)

            # Save the image and its mask once all annotations for the image are processed
            mask_path = os.path.join(masks_output_path, img_name)
            img_save_path = os.path.join(images_output_path, img_name)

            cv.imwrite(mask_path, masks_per_image[img_name])
            cv.imwrite(img_save_path, img)  # Save the image

            print(f"Saved {img_name} and its mask.")


def find_contours(mask):
    """
    Extracts outer and inner contours from a binary mask.
    Outer contours are found outside the objects, and inner contours inside the holes.
    """
    contours, hierarchy = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    outer_contours = []
    inner_contours = []

    # If no hierarchy is returned, return empty lists
    if hierarchy is None:
        return outer_contours, inner_contours

    # Hierarchy: [Next, Previous, First_Child, Parent]
    for idx, contour_info in enumerate(hierarchy[0]):
        if contour_info[3] == -1:  # No parent, outer contour
            outer_contours.append(contours[idx])
        else:  # Has parent, inner contour
            inner_contours.append(contours[idx])

    return outer_contours, inner_contours


def process_masks_to_coco(mask_address, images_address, output_folder):
    """
    Process masks to generate COCO annotations and save them to a file, and copy images to the output folder.
    """
    coco_data = fm.initialize_coco_data()
    masks_and_images = fm.load_masks_from_images(mask_address, images_address)
    annotation_id_start = 1

    # Create directories for annotations and images within the output folder
    annotations_output_path = os.path.join(output_folder, 'annotations')
    images_output_path = os.path.join(output_folder, 'images')
    create_directory(annotations_output_path, delete=True)
    create_directory(images_output_path, delete=True)

    for mask, img, filename in masks_and_images:
        height, width = img.shape[:2]
        outer_contours, inner_contours = find_contours(mask)
        coco_data = fm.convert_contours_to_coco(outer_contours, inner_contours, height, width, filename,
                                             annotation_id_start, coco_data)
        annotation_id_start += len(outer_contours) + len(inner_contours)  # Update start ID for next image

        # Copy each image to the images_output_path
        img_output_path = os.path.join(images_output_path, filename)
        shutil.copy(os.path.join(images_address, filename), img_output_path)

    # Save coco_data to a JSON file named instances_default.json within annotations directory
    coco_json_path = os.path.join(annotations_output_path, 'instances_default.json')
    with open(coco_json_path, 'w') as f:
        js.dump(coco_data, f)

    fm.zip_folder(output_folder, f"{output_folder}.zip")

    print(f"COCO annotations saved to {coco_json_path}")
    print(f"Images copied to {images_output_path}")