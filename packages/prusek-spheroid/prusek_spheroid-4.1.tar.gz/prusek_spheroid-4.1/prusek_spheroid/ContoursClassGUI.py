import os
import cv2 as cv
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import json
import pandas as pd
from prusek_spheroid import file_management as fm
from prusek_spheroid import selection_dialog as sd
from prusek_spheroid import metrics as metric
from prusek_spheroid.methods import BaseImageProcessing
from prusek_spheroid import characteristic_functions as cf
from prusek_spheroid import image_processing as ip
import joblib


class Contours(BaseImageProcessing):

    def __init__(self, master, adresaDatasetu, adresa_output, projekt, algorithm, parameters, show_img, function,
                 contours_state, detect_corrupted, create_json, calculate_properties,
                 progress_window=None):
        super().__init__()
        self.counter = None
        self.master = master
        self.user_decision_lock = Lock()
        self.adresaDatasetu = adresaDatasetu
        self.output_json_path = f"{adresa_output}/{projekt}/CVAT/{algorithm}/annotations/instances_default.json"
        self.output_images_path = f"{adresa_output}/{projekt}/CVAT/{algorithm}/images"
        self.output_segmented_path = f"{adresa_output}/{projekt}/segmented_images/{algorithm}"
        self.zipfile_address = f"{adresa_output}/{projekt}/CVAT/{algorithm}"
        self.excel_address = f"{adresa_output}/{projekt}"
        self.coco_data = fm.initialize_coco_data()
        self.show_img = show_img
        self.projekt = projekt
        self.algorithm = algorithm
        self.parameters = parameters
        self.contours_state = contours_state
        self.detect_corrupted = detect_corrupted
        self.create_json = create_json
        self.calculate_properties = calculate_properties
        self.f = function
        self.progress_window = progress_window
        self.min_area = self.parameters["min_area"]
        self.model = joblib.load("gradient_boosting_classifier.joblib")
        self.scaler = joblib.load("scaler.joblib")

        fm.create_directory(os.path.dirname(self.output_json_path), delete=True)
        fm.create_directory(self.output_images_path, delete=True)
        fm.create_directory(f"{self.output_segmented_path}/masks", delete=True)
        fm.create_directory(f"{self.output_segmented_path}/results", delete=True)

    def evaluate(self, contour):
        hu_moments = ip.compute_hu_moments(contour)
        hu_moments_scaled = self.scaler.transform([hu_moments])
        contour_class = self.model.predict(hu_moments_scaled)[0]
        return contour_class

    def run(self):
        dialog = None
        self.counter = 1
        filenames = [f for f in os.listdir(self.adresaDatasetu) if
                     f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'))]
        total_files = len(filenames)
        print(f"loaded {total_files} dataset images")

        all_contour_data = []
        if self.contours_state == "select":
            dialog = sd.SelectionDialog(self.master, self.counter, total_files, self.user_decision_lock)

        for filename in os.listdir(self.adresaDatasetu):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')):
                if self.contours_state == "select":
                    self.user_decision_lock.acquire()

                img_path = os.path.join(self.adresaDatasetu, filename)
                img = cv.imread(img_path)

                if img is None:
                    print(f"FAILED to load image: {img_path}")
                    continue  # Skip to the next image

                img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                img_gray = cv.resize(img_gray, (1000, 1000), interpolation=cv.INTER_LANCZOS4)

                img_binary, inner_contours_mask = self.apply_segmentation_algorithm(self.algorithm, self.parameters,
                                                                                    img_gray,
                                                                                    self.contours_state)

                outer_contours, _ = cv.findContours(img_binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                if self.contours_state == "all" or self.contours_state == "select":
                    inner_contours, _ = cv.findContours(inner_contours_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                    inner_contours = ip.remove_small_contours(inner_contours)

                height, width = np.shape(img_binary)

                outer_contours = ip.filter_contours_on_frame(outer_contours, (height, width), self.min_area,
                                                                  self.detect_corrupted)
                outer_contours = ip.remove_small_contours(outer_contours)


                if self.create_json:
                    if not cv.imwrite(f"{self.output_images_path}/{filename}", img):
                        print(f"FAILED to save image: {self.output_images_path}/{filename}")

                img_with = img.copy()
                if len(outer_contours) == 0:
                    if self.create_json:
                        self.coco_data = fm.convert_contours_to_coco([], [], height, width,
                                                                     filename,
                                                                     self.counter,
                                                                     self.coco_data)
                    cv.line(img_with, (0, 0), (width - 1, height - 1), (0, 0, 255), 5)
                    cv.line(img_with, (0, height - 1), (width - 1, 0), (0, 0, 255), 5)
                    if not cv.imwrite(
                            f"{self.output_segmented_path}/results/{filename.replace('.bmp', '.png')}",
                            img_with):
                        print(
                            f"FAILED to save image: {self.output_segmented_path}/results/{filename.replace('.bmp', '.png')}")

                else:
                    img_without = img.copy()
                    mask_without = np.zeros_like(img_gray)

                    for contour in outer_contours:
                        contour = np.array(contour, dtype=np.int32)
                        cv.fillPoly(mask_without, [contour], 255)

                    if self.contours_state == "all" or self.contours_state == "select":
                        inner_mask = np.zeros_like(img_gray)
                        for contour in inner_contours:
                            contour = np.array(contour, dtype=np.int32)
                            cv.fillPoly(inner_mask, [contour], 255)

                        # Find intersection between outer and inner masks
                        intersection = mask_without & inner_mask
                        inner_contours, _ = cv.findContours(intersection, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                        inner_contours = ip.remove_small_contours(inner_contours)


                        # Subtract intersection from the outer contours mask
                        mask_with = mask_without - intersection

                        for contour in inner_contours:
                            cv.drawContours(img_with, [contour], -1, (255,0,0), 2)


                    for index, contour in enumerate(outer_contours):
                        contour_budding = self.evaluate(contour)

                        if not contour_budding == "no_split":
                            color = (0,255,0)
                        else:
                            color = (0,0,255)

                        if self.contours_state == "all":
                            cv.drawContours(img_with, [contour], -1, color, 2)
                        elif self.contours_state == "no":
                            cv.drawContours(img_without, [contour], -1, color, 2)
                        else:
                            cv.drawContours(img_without, [contour], -1, color, 2)
                            cv.drawContours(img_with, [contour], -1, color, 2)

                        if self.contours_state == "select" and dialog:
                            dialog.update_selection_dialog(img_without, img_with, mask_without, mask_with,
                                                           f"{self.output_segmented_path}/results/{filename.replace('.bmp', '.png')}",
                                                           f"{self.output_segmented_path}/masks/{filename.replace('.bmp', '.png')}",
                                                           self.counter)
                        elif self.contours_state == "all":
                            if not cv.imwrite(f"{self.output_segmented_path}/masks/{filename.replace('.bmp', '.png')}",
                                              mask_with):
                                print(
                                    f"FAILED to save mask: {self.output_segmented_path}/masks/{filename.replace('.bmp', '.png')}")
                            if not cv.imwrite(
                                    f"{self.output_segmented_path}/results/{filename.replace('.bmp', '.png')}",
                                    img_with):
                                print(
                                    f"FAILED to save image: {self.output_segmented_path}/results/{filename.replace('.bmp', '.png')}")
                        else:
                            if not cv.imwrite(f"{self.output_segmented_path}/masks/{filename.replace('.bmp', '.png')}",
                                              mask_without):
                                print(
                                    f"FAILED to save mask: {self.output_segmented_path}/masks/{filename.replace('.bmp', '.png')}")
                            if not cv.imwrite(
                                    f"{self.output_segmented_path}/results/{filename.replace('.bmp', '.png')}",
                                    img_without):
                                print(
                                    f"FAILED to save image: {self.output_segmented_path}/results/{filename.replace('.bmp', '.png')}")

                        if self.calculate_properties:
                            contour_data = {
                                'MaskName': os.path.basename(filename),
                                'ContourOrder': index + 1
                            }

                            additional_data = cf.calculate_all(contour)
                            contour_data.update(additional_data)

                            all_contour_data.append(contour_data)

                    if self.create_json:
                        self.coco_data = fm.convert_contours_to_coco(outer_contours, inner_contours, height, width,
                                                                     filename,
                                                                     self.counter,
                                                                     self.coco_data)

                if self.progress_window:
                    progress_text = f"{self.counter}/{total_files}"
                    self.progress_window.update_progress(progress_text)

                self.counter += 1

        if dialog:
            dialog.destroy_dialog()

        if self.progress_window:
            self.progress_window.update_progress("dumping...")

        if self.calculate_properties:
            all_contour_data.sort(key=lambda x: x['MaskName'])
            df = pd.DataFrame(all_contour_data, columns=[
                'MaskName', 'ContourOrder', 'Area', 'Circularity', 'Compactness', 'Convexity',
                'EquivalentDiameter', 'FeretAspectRatio', 'FeretDiameterMax',
                'FeretDiameterMaxOrthogonalDistance', 'FeretDiameterMin',
                'LengthMajorDiameterThroughCentroid', 'LengthMinorDiameterThroughCentroid',
                'Perimeter', 'Solidity', 'Sphericity'
            ])
            df.to_excel(f"{self.excel_address}/contour_properties.xlsx")

        if self.create_json:
            with open(self.output_json_path, "w") as json_file:
                json.dump(self.coco_data, json_file)
            if self.progress_window:
                self.progress_window.update_progress("zipping folder...")
            fm.zip_folder(self.zipfile_address, f"{self.zipfile_address}.zip")

        if self.progress_window:
            self.progress_window.update_progress("FINISHED")


class IoU(BaseImageProcessing):
    def __init__(self, adresa_output, project, algorithm, contours_state,
                 detect_corrupted):
        super().__init__()
        self.project = project
        self.algorithm = algorithm
        self.contours_state = contours_state
        self.detect_corrupted = detect_corrupted
        self.adresa_output = f"{adresa_output}/{project}/IoU"
        self.adresa_plots = f"{adresa_output}/{project}/IoU/plots/{self.algorithm}"

        fm.create_directory(self.adresa_output)

        # for mask, name in zip(self.masks, self.img_names):
        #    cv.imwrite(f"img_print/{name}",mask)

    def process_and_compute_iou(self, ref_mask, img, img_name, parameters, save, lock):
        # Convert the mask tensor and image tensor to numpy arrays
        ref_mask = ref_mask.numpy()
        img = img.numpy()

        # Convert image to grayscale (assuming img is in BGR format)
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Apply the segmentation algorithm
        img_binary, inner_contours_mask = self.apply_segmentation_algorithm(
            self.algorithm, parameters, img_gray, self.contours_state)

        # Further processing and IoU, TPR, PPV computation
        if self.contours_state == "all" or self.contours_state == "select":
            intersection = inner_contours_mask & img_binary
            img_binary = img_binary - intersection

        contours, _ = cv.findContours(img_binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)


        mask = np.zeros_like(img_binary, dtype=np.uint8)
        if not contours:
            # If no contours are found, draw a default contour
            contour = np.array([[0, 0]], dtype=np.int32)
            cv.drawContours(mask, [contour], 0, color=255, thickness=-1)
        else:
            # Draw contours on the mask
            for contour in contours:
                cv.drawContours(mask, [contour], 0, color=255, thickness=-1)

        # Thread-safe operations start here
        lock.acquire()
        try:
            iou, tpr, ppv = metric.IoU(ref_mask, mask)
        finally:
            lock.release()

        return iou, tpr, ppv

    def run(self, batch, parameters, save_txt):
        IoUbuffer = []
        ratesBuffer = []

        lock = Lock()  # Create a Lock for thread-safe IoU calculations
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.process_and_compute_iou, ref_mask, img, img_name, parameters, save_txt, lock)
                for ref_mask, img, img_name in zip(*batch)]
            for future in futures:
                iou, tpr, ppv = future.result()
                IoUbuffer.append(iou)
                ratesBuffer.append([tpr, ppv])

        averageIoU = np.average(IoUbuffer)

        if save_txt:
            rounded_parameters = {key: round(value, 2) for key, value in parameters.items()}
            TPRs = [entry[0] for entry in ratesBuffer]
            PPVs = [entry[1] for entry in ratesBuffer]
            averageTPR = np.average(TPRs)
            averagePPV = np.average(PPVs)

            # Uložení do JSON souboru
            json_data = {
                "method": self.algorithm,
                "parameters": rounded_parameters,
                "averageIoU": round(averageIoU * 100, 2),
                "averageTPR": round(averageTPR * 100, 2),
                "averagePPV": round(averagePPV * 100, 2),
                "contours_state": self.contours_state,
                "detect_corrupted": self.detect_corrupted
            }

            return json_data
        return averageIoU

    def save_parameters_json(self, averageIoU, json_data_list):
        json_data = average_json_data(json_data_list)
        json_data.update({
            "method": self.algorithm,
            "contours_state": self.contours_state,
            "detect_corrupted": self.detect_corrupted
        })

        # NumpyEncoder pro správné uložení numpy dat
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                else:
                    return super(NumpyEncoder, self).default(obj)

        # Název souboru s výsledky
        if self.contours_state == "no":
            contours_state_string = "NO_HOLES"
        elif self.contours_state == "all":
            contours_state_string = "WITH_HOLES"
        else:
            contours_state_string = "SELECT_HOLES"

        detect_corrupted_string = "WITH_detecting_corrupted" if self.detect_corrupted else "WITHOUT_detecting_corrupted"

        with open(
                f"{self.adresa_output}/results_{self.project}_{self.algorithm}_IoU_{round(averageIoU * 100, 2)}_{contours_state_string}_{detect_corrupted_string}.json",
                "w") as json_file:
            json.dump(json_data, json_file, indent=4, cls=NumpyEncoder)


def average_json_data(json_data_list):
    # Inicializujeme prázdné seznamy pro jednotlivé hodnoty
    parameters_list = []

    # Projdeme všechny JSON data a přidáme jejich hodnoty do příslušných seznamů
    for json_data in json_data_list:
        if json_data:
            # Kontrola, zda jsou hodnoty v json_data ve správném formátu
            if isinstance(json_data["parameters"], dict):
                parameters_list.append(json_data["parameters"])

    # Pokud jsou všechna json_data prázdná nebo neobsahují správné hodnoty, vrátíme None
    if not parameters_list:
        return None

    # Zprůměrujeme hodnoty v seznamech
    averaged_parameters = {}
    for key in parameters_list[0].keys():
        averaged_parameters[key] = np.mean([param[key] for param in parameters_list])

    # Vytvoříme nový JSON objekt se zprůměrovanými hodnotami
    averaged_json_data = {
        "parameters": averaged_parameters,
    }

    return averaged_json_data
