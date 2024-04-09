import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from prusek_spheroid import GradientDescentGUI as g
from prusek_spheroid import ContoursClassGUI as F
import threading
import time
import json
import os
from prusek_spheroid import characteristic_functions as cf
from prusek_spheroid import file_management as fm
from prusek_spheroid import conversion as c
from prusek_spheroid import merge_directories as md
import pandas as pd
import cv2 as cv
from tkinter import Toplevel, Label
from tkinter import ttk


class SelectionDialog:
    def __init__(self, root):
        self.root = root
        self.dialog = tk.Toplevel(root)
        self.dialog.title("Software Selection")
        self.dialog.geometry("600x200")

        self.main_section_label = tk.Label(self.dialog, text="Main software", font=("Helvetica", 12, "bold"))
        self.main_section_label.pack()

        seg_button = tk.Button(self.dialog, text="Spheroids Segmentation", command=self.open_segmentation_gui)
        seg_button.pack(pady=10)

        quant_button = tk.Button(self.dialog, text="Spheroids Quantification", command=self.open_quantification_gui)
        quant_button.pack(pady=10)

        self.address_separator = tk.Frame(self.dialog, height=2, bd=1, relief=tk.SUNKEN)
        self.address_separator.pack(fill=tk.X, padx=5, pady=5)

        self.utils_section_label = tk.Label(self.dialog, text="Utils", font=("Helvetica", 12, "bold"))
        self.utils_section_label.pack()

        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)

        convert_button = tk.Button(button_frame, text="Convert between COCO 1.0 and Masks",
                                   command=self.open_conversion_gui)
        image_processing_btn = tk.Button(button_frame, text="Create dataset folder (merge directories)",
                                         command=self.open_image_processing_dialog)

        # Place buttons in the frame using grid
        convert_button.grid(row=0, column=0, padx=(0, 10))  # Padding to the right
        image_processing_btn.grid(row=0, column=1, padx=(10, 0))  # Padding to the left

        # Adjust the frame's column configuration to center the buttons
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)

    def show(self):
        self.dialog.deiconify()

    def hide(self):
        self.dialog.withdraw()

    def open_segmentation_gui(self):
        self.hide()
        SpheroidSegmentationGUI(self)

    def open_quantification_gui(self):
        self.hide()
        SpheroidQuantificationGUI(self)

    def open_conversion_gui(self):
        self.hide()
        ConversionDialog(self)

    def open_image_processing_dialog(self):
        self.hide()  # Optionally hide the selection dialog
        ImageProcessingDialog(self)

    def on_close(self):
        self.root.quit()


class ImageProcessingDialog:
    def __init__(self, selection_dialog):
        self.done_dialog = None
        self.progress_label = None
        self.progress_dialog = None
        self.output_dir_label = None
        self.root_dir_label = None
        self.output_dir_path = None
        self.root_dir_path = None
        self.selection_dialog = selection_dialog
        self.dialog = tk.Toplevel(selection_dialog.root)
        self.dialog.title("Image Processing")
        self.setup_dialog()

    def setup_dialog(self):
        back_button = tk.Button(self.dialog, text="Back", command=self.go_back)
        back_button.pack(anchor='nw', padx=10, pady=5)
        self.root_dir_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        self.dialog.geometry("600x200")

        # Browse root directory button and label
        browse_root_btn = tk.Button(self.dialog, text="Browse Root Directory",
                                    command=lambda: browse_directory(self.root_dir_path, "Root Directory",
                                                                     self.root_dir_label))
        browse_root_btn.pack()
        self.root_dir_label = tk.Label(self.dialog, text="Root Directory: Not selected")
        self.root_dir_label.pack()

        # Browse output directory button and label
        browse_output_btn = tk.Button(self.dialog, text="Browse Output Directory",
                                      command=lambda: browse_directory(self.output_dir_path, "Output Directory",
                                                                       self.output_dir_label))
        browse_output_btn.pack()
        self.output_dir_label = tk.Label(self.dialog, text="Output Directory: Not selected")
        self.output_dir_label.pack()

        # Run button
        run_btn = tk.Button(self.dialog, text="Run", command=self.run_image_processing)
        run_btn.pack()

        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_progress_dialog(self):
        self.progress_dialog = tk.Toplevel(self.dialog)
        self.progress_dialog.title("Processing")
        self.progress_dialog.geometry("300x100")
        self.progress_label = tk.Label(self.progress_dialog, text="Starting...")
        self.progress_label.pack(pady=20)

        # Prevent closing the progress dialog manually
        self.progress_dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    def update_progress(self, processed, total, msg):
        self.progress_label.config(text=f"Progress: {processed}/{total} - {msg}.")

    def show_done_dialog(self):
        # Close the progress dialog first
        self.progress_dialog.destroy()

        self.done_dialog = tk.Toplevel(self.dialog)
        self.done_dialog.title("Done")
        self.done_dialog.geometry("300x100")
        tk.Label(self.done_dialog, text="DONE", pady=20).pack()

        ok_button = tk.Button(self.done_dialog, text="OK", command=self.done_dialog.destroy)
        ok_button.pack(pady=10)

    def run_image_processing(self):
        root_dir = self.root_dir_path.get()
        output_dir = self.output_dir_path.get()
        if not root_dir or not output_dir:
            messagebox.showerror("Error", "Both directories must be selected.")
            return

        self.show_progress_dialog()

        # Start the long-running task in a separate thread
        thread = threading.Thread(target=md.copy_and_rename_bmp_files,
                                  args=(root_dir, output_dir, self.update_progress_ui))
        thread.start()

    def update_progress_ui(self, processed, total, msg):
        # Update the progress in the UI, ensuring the update is done in the main thread
        self.progress_dialog.after(0, lambda: self.update_progress(processed, total, msg))
        if processed == total:
            # Once processing is complete, show the "DONE" dialog
            self.progress_dialog.after(0, self.show_done_dialog)

    def go_back(self):
        self.dialog.destroy()
        self.selection_dialog.show()

    def on_close(self):
        self.dialog.quit()


class ConversionDialog:
    def __init__(self, selection_dialog):
        self.wait_dialog = None
        self.output_folder_label_masks = None
        self.images_folder_label = None
        self.coco_address_label = None
        self.output_folder_label_coco = None
        self.masks_folder_label = None
        self.selection_dialog = selection_dialog
        # Define the StringVar attributes here before calling setup_dialog
        self.coco_annotation_path = tk.StringVar()
        self.output_folder_path_coco = tk.StringVar()
        self.masks_folder_path = tk.StringVar()
        self.images_folder_path = tk.StringVar()
        self.output_folder_path_masks = tk.StringVar()

        self.dialog = tk.Toplevel(selection_dialog.root)
        self.dialog.title("Conversion dialog")
        self.setup_dialog()  # Now all necessary attributes are defined before setup_dialog is called

    def setup_dialog(self):
        back_button = tk.Button(self.dialog, text="Back", command=self.go_back)
        back_button.pack(anchor='nw', padx=10, pady=5)

        notebook = ttk.Notebook(self.dialog)
        coco_to_masks_tab = ttk.Frame(notebook)
        masks_to_coco_tab = ttk.Frame(notebook)
        notebook.add(coco_to_masks_tab, text='COCO 1.0 to Masks')
        notebook.add(masks_to_coco_tab, text='Masks to COCO 1.0')
        notebook.pack(expand=True, fill='both')

        # COCO to Masks tab components
        coco_annotation_button = tk.Button(coco_to_masks_tab, text="Load COCO 1.0 Annotations ZIP",
                                           command=lambda: browse_file(self.coco_annotation_path,
                                                                       "COCO Annotations ZIP", self.coco_address_label))
        self.coco_address_label = tk.Label(coco_to_masks_tab, text="COCO annotations Directory: Not selected")
        coco_annotation_button.pack(pady=10)
        self.coco_address_label.pack()

        output_folder_button_coco = tk.Button(coco_to_masks_tab, text="Select Output Folder",
                                              command=lambda: browse_directory(self.output_folder_path_coco,
                                                                               "Output Folder for COCO to Masks",
                                                                               self.output_folder_label_coco))
        self.output_folder_label_coco = tk.Label(coco_to_masks_tab, text="Output Directory: Not selected")
        output_folder_button_coco.pack(pady=10)
        self.output_folder_label_coco.pack()

        # Masks to COCO tab components
        masks_folder_button = tk.Button(masks_to_coco_tab, text="Load Masks Folder",
                                        command=lambda: browse_directory(self.masks_folder_path, "Masks Folder",
                                                                         self.masks_folder_label))
        self.masks_folder_label = tk.Label(masks_to_coco_tab, text="Masks Directory: Not selected")
        masks_folder_button.pack(pady=10)
        self.masks_folder_label.pack()

        images_folder_button = tk.Button(masks_to_coco_tab, text="Load Images Folder",
                                         command=lambda: browse_directory(self.images_folder_path, "Images Folder",
                                                                          self.images_folder_label))
        self.images_folder_label = tk.Label(masks_to_coco_tab, text="Images Directory: Not selected")
        images_folder_button.pack(pady=10)
        self.images_folder_label.pack()

        output_folder_button_masks = tk.Button(masks_to_coco_tab, text="Select Output Folder",
                                               command=lambda: browse_directory(self.output_folder_path_masks,
                                                                                "Output Folder for Masks to COCO",
                                                                                self.output_folder_label_masks))
        self.output_folder_label_masks = tk.Label(masks_to_coco_tab, text="Output Directory: Not selected")
        output_folder_button_masks.pack(pady=10)
        self.output_folder_label_masks.pack()

        # Inside the setup_dialog method of ConversionDialog class

        run_button = tk.Button(self.dialog, text="Run Conversion",
                               command=lambda: self.run_conversion(notebook.index(notebook.select())))
        run_button.pack(pady=20)

        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)

    @staticmethod
    def show_done_dialog(message):
        # Create a top-level window
        done_dialog = tk.Toplevel()
        done_dialog.title("Conversion Completed")

        # Set the window size and make it non-resizable
        done_dialog.geometry("300x100")
        done_dialog.resizable(False, False)

        # Message Label
        tk.Label(done_dialog, text=message, pady=10).pack()

        # OK Button
        ok_button = tk.Button(done_dialog, text="OK", command=done_dialog.destroy, width=10)
        ok_button.pack(pady=10)

    def show_wait_dialog(self):
        self.wait_dialog = tk.Toplevel()  # Create a new top-level window
        self.wait_dialog.title("Processing")

        # Set the window size and make it non-resizable
        self.wait_dialog.geometry("200x100")
        self.wait_dialog.resizable(False, False)

        # Message Label
        tk.Label(self.wait_dialog, text="Wait...", pady=20).pack()

        self.wait_dialog.grab_set()  # Make it modal
        self.wait_dialog.lift()  # Bring it to front
        self.wait_dialog.focus_set()  # Set focus to this window

        # This window should not be closed manually; it will be closed programmatically
        self.wait_dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable the close button

    def go_back(self):
        self.dialog.destroy()
        self.selection_dialog.show()

    def run_conversion(self, active_tab_index):
        self.show_wait_dialog()
        if active_tab_index == 0:  # COCO 1.0 to Masks
            coco_zip_path = self.coco_annotation_path.get()
            output_folder_path = self.output_folder_path_coco.get()

            if not coco_zip_path or not output_folder_path:
                messagebox.showerror("Error", "Both COCO ZIP file and output folder addresses must be filled.")
                return

            try:
                annotation_address = fm.unzip(
                    coco_zip_path)
                annotations_address, images_address = update_addresses(annotation_address)
                c.load_annotations_and_save(annotations_address, images_address,
                                            os.path.join(output_folder_path, "masks"),
                                            os.path.join(output_folder_path, "images"))
                self.wait_dialog.destroy()  # Close the wait dialog on success
                self.show_done_dialog("Conversion to masks completed successfully.")
            except Exception as e:
                self.wait_dialog.destroy()
                messagebox.showerror("Error", f"Failed to process COCO annotations. Error: {str(e)}")

        elif active_tab_index == 1:  # Masks to COCO 1.0
            masks_folder_path = self.masks_folder_path.get()
            images_folder_path = self.images_folder_path.get()
            output_folder_path = self.output_folder_path_masks.get()

            if not masks_folder_path or not images_folder_path or not output_folder_path:
                messagebox.showerror("Error",
                                     "Masks folder, images folder, and output folder addresses must be filled.")
                return

            try:
                c.process_masks_to_coco(masks_folder_path, images_folder_path, output_folder_path)
                self.wait_dialog.destroy()
                self.show_done_dialog("Conversion to COCO completed successfully.")
            except Exception as e:
                self.wait_dialog.destroy()
                messagebox.showerror("Error", f"Failed to process masks. Error: {str(e)}")

    def on_close(self):
        self.dialog.quit()

    @staticmethod
    def shorten_path(path, max_length=40):
        if len(path) > max_length:
            return '...' + path[-max_length + 3:]
        return path


def update_addresses(annotationsAddress):
    annotation_address = os.path.join(annotationsAddress, "annotations")
    images_address = os.path.join(annotationsAddress, "images")

    return annotation_address, images_address


class ProcessingProgressWindow(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title("Processing Progress")

        self.geometry("500x250")
        self.resizable(width=False, height=False)

        # Frame pro centrování obsahu
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)

        # Label ve frame pro centrování
        self.label_progress = tk.Label(center_frame, text="Progress: ")
        self.label_progress.pack()

    def update_progress(self, progress):
        self.label_progress.config(text=f"Progress: {progress}")


class OptimizationProgressWindow(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title("Optimization Progress")

        self.geometry("500x250")  # Šířka x Výška
        self.resizable(width=False, height=False)

        # Frame pro centrování obsahu
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)

        # Labely ve frame pro centrování
        self.label_project = tk.Label(center_frame, text="Project: ")
        self.label_project.pack()

        self.label_algorithm = tk.Label(center_frame, text="Algorithm: ")
        self.label_algorithm.pack()

        self.label_iteration = tk.Label(center_frame, text="Iteration: ")
        self.label_iteration.pack()

        self.label_iou = tk.Label(center_frame, text="IoU: ")
        self.label_iou.pack()

        self.label_parameters = tk.Label(center_frame, text="Estimated time remaining: ")
        self.label_parameters.pack()

        self.label_batch_num = tk.Label(center_frame, text="Batch number: ")
        self.label_batch_num.pack()

    def update_info(self, project, algorithm, iteration, IoU, time_rem, batch_info):
        self.label_project.config(text=f"Project: {project}")
        self.label_algorithm.config(text=f"Algorithm: {algorithm}")
        self.label_iteration.config(text=f"Iteration: {iteration}")
        self.label_iou.config(text=f"IoU: {IoU}%")
        self.label_parameters.config(text=f"Estimated time remaining: {time_rem} seconds")
        self.label_batch_num.config(text=f"Batch number: {batch_info}")


class ParameterEntryDialog(tk.Toplevel):
    def __init__(self, master, algorithm, parameters):
        tk.Toplevel.__init__(self, master)
        self.title("Enter Parameters")

        self.algorithm = algorithm
        self.parameters = parameters  # Store loaded parameters from JSON
        self.result = None

        # Create labels and entry widgets for each parameter with descriptions and ranges
        self.entries = {}
        for param, value in self.parameters.items():
            label = tk.Label(self, text=f"{param}:")
            label.pack()
            entry = tk.Entry(self)
            entry.insert(0, str(value))
            entry.pack()
            self.entries[param] = entry

        # OK button to confirm parameter values
        ok_button = tk.Button(self, text="OK", command=self.confirm_parameters)
        ok_button.pack()

    def confirm_parameters(self):
        # Retrieve parameter values from entry widgets and update self.parameters
        for param, entry in self.entries.items():
            value = entry.get()
            try:
                value = float(value)
                self.parameters[param] = value
            except ValueError:
                # Handle invalid input, e.g., non-numeric values
                pass
        self.result = self.parameters  # Set the result to the updated parameters
        self.destroy()  # Close the dialog

    def close_dialog(self):
        self.result = None
        self.destroy()

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, parameters):
        for param, value in parameters.items():
            if param in self.entries:
                self.entries[param].delete(0, tk.END)
                self.entries[param].insert(0, str(value))

    def update_parameters(self, new_parameters):
        # Update parameters in the main application when entering them manually
        self.parameters = new_parameters


def shorten_path(path, max_length=40):
    if len(path) > max_length:
        return '...' + path[-max_length + 3:]
    return path


def browse_file(var, title, label):
    file_path = filedialog.askopenfilename()
    var.set(file_path)
    shortened_path = shorten_path(file_path)
    label.config(text=f"{title}: {shortened_path}")


def browse_directory(var, title, label):
    directory_path = filedialog.askdirectory()
    var.set(directory_path)
    shortened_path = shorten_path(directory_path)
    label.config(text=f"{title}: {shortened_path}")


class SpheroidQuantificationGUI:
    def __init__(self, selection_dialog):
        self.selection_dialog = selection_dialog
        self.dialog = tk.Toplevel(selection_dialog.root)
        self.dialog.title("Spheroid Quantification")

        back_button = tk.Button(self.dialog, text="Back", command=self.go_back)
        back_button.pack(anchor='nw', padx=10, pady=5)

        # Sekce pro kvantifikaci sféroidů
        # Implementace funkcí a GUI prvků pro kvantifikaci sféroidů

        # Button to retrieve the folder address of masks of annotated spheroids
        self.retrieve_masks_button_quantification = tk.Button(self.dialog,
                                                              text="Retrieve the folder address of masks of annotated spheroids",
                                                              command=lambda: browse_directory(
                                                                  self.masks_annotation_path_quantification,
                                                                  "Selected masks folder",
                                                                  self.masks_address_label_quantification))
        self.retrieve_masks_button_quantification.pack()

        self.masks_annotation_path_quantification = tk.StringVar()
        self.masks_address_label_quantification = tk.Label(self.dialog, text="Masks Directory: Not selected")
        self.masks_address_label_quantification.pack()

        # Button to retrieve the output folder address
        self.retrieve_output_button_quantification = tk.Button(self.dialog,
                                                               text="Retrieve the output folder address",
                                                               command=lambda: browse_directory(
                                                                   self.output_path_quantification,
                                                                   "Selected output folder",
                                                                   self.output_address_label_quantification))
        self.retrieve_output_button_quantification.pack()

        self.output_path_quantification = tk.StringVar()
        self.output_address_label_quantification = tk.Label(self.dialog, text="Output Directory: Not selected")
        self.output_address_label_quantification.pack()

        # Button to calculate spheroid properties
        self.calculate_properties_button = tk.Button(self.dialog, text="Calculate spheroid properties",
                                                     command=self.calculate_spheroid_properties)
        self.calculate_properties_button.pack()

        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)

    def go_back(self):
        self.dialog.destroy()
        self.selection_dialog.show()

    def on_close(self):
        self.dialog.quit()  # Toto ukončí celý program

    def calculate_spheroid_properties(self):
        if not self.masks_annotation_path_quantification.get() or not self.output_path_quantification.get():
            messagebox.showerror("Error", "Both mask folder and output folder addresses must be filled.")
            return

        masks_data = fm.load_masks(self.masks_annotation_path_quantification.get())
        total_masks = len(masks_data)

        # Dialog for progress
        # Dialog for progress
        progress_dialog = Toplevel(self.dialog)
        progress_dialog.title("Processing Progress")
        progress_dialog.geometry("400x100")  # Nastaví rozměry okna na 400x100 pixelů
        Label(progress_dialog, text=f"Total images: {total_masks}").pack()
        progress_label = Label(progress_dialog, text="Starting...")
        progress_label.pack()

        all_contour_data = []

        for index, (mask, name) in enumerate(masks_data, start=1):
            progress_label.config(text=f"Processing image {index} of {total_masks}")
            progress_dialog.update()

            contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv.contourArea, reverse=True)

            for order, contour in enumerate(contours, start=1):
                # Your contour processing and feature calculation goes here
                additional_data = cf.calculate_all(contour)  # Toto je vaše vlastní funkce pro výpočet
                contour_data = {
                    'MaskName': os.path.basename(name),
                    'ContourOrder': order,
                    **additional_data
                }
                all_contour_data.append(contour_data)

        columns = [
            'MaskName', 'ContourOrder', 'Area', 'Circularity', 'Compactness', 'Convexity',
            'EquivalentDiameter', 'FeretAspectRatio', 'FeretDiameterMax',
            'FeretDiameterMaxOrthogonalDistance', 'FeretDiameterMin',
            'LengthMajorDiameterThroughCentroid', 'LengthMinorDiameterThroughCentroid',
            'Perimeter', 'Solidity', 'Sphericity'
        ]
        df = pd.DataFrame(all_contour_data, columns=columns)
        output_path = self.output_path_quantification.get()
        df.to_excel(f"{output_path}/contour_properties.xlsx")

        # Close the progress dialog
        progress_dialog.destroy()

        # Show completion message
        messagebox.showinfo("Completed", f"Spheroid properties calculated and saved.\nOutput path: {output_path}")
        print("Spheroid properties calculated and saved.")


class SpheroidSegmentationGUI:
    def __init__(self, selection_dialog):
        self.selection_dialog = selection_dialog
        self.dialog = tk.Toplevel(selection_dialog.root)
        self.dialog.title("Spheroid Quantification")

        back_button = tk.Button(self.dialog, text="Back", command=self.go_back)
        back_button.pack(anchor='nw', padx=10, pady=5)
        self.loaded_parameters = None
        self.loaded_method = None

        # Adresní sekce
        self.address_section_label = tk.Label(self.dialog, text="Address Settings", font=("Helvetica", 12, "bold"))
        self.address_section_label.pack()

        self.notebook = ttk.Notebook(self.dialog)
        self.coco_tab = ttk.Frame(self.notebook)  # První záložka pro COCO
        self.mask_tab = ttk.Frame(self.notebook)  # Druhá záložka pro masky

        self.notebook.add(self.coco_tab, text='Load COCO Annotations')
        self.notebook.add(self.mask_tab, text='Load MASK Annotations')
        self.notebook.pack(expand=True, fill='both')

        # COCO Annotations tab
        self.coco_annotation_button = tk.Button(self.coco_tab,
                                                text="Retrieve the COCO 1.0 ZIP file address downloaded from CVAT",
                                                command=lambda: browse_file(self.coco_annotation_path,
                                                                            "Selected ZIP file address",
                                                                            self.coco_address_label))
        self.coco_annotation_button.pack(side=tk.TOP)

        self.coco_address_label = tk.Label(self.coco_tab, text="COCO Annotations Directory: Not selected")
        self.coco_address_label.pack()

        self.coco_annotation_path = tk.StringVar()

        # Mask Annotations tab
        self.retrieve_mask_button = tk.Button(self.mask_tab,
                                              text="Retrieve the annotated spheroid MASK FOLDER address",
                                              command=lambda: browse_directory(self.masks_annotation_path,
                                                                               "Selected mask address",
                                                                               self.mask_address_label))
        self.retrieve_mask_button.pack(side=tk.TOP)

        self.mask_address_label = tk.Label(self.mask_tab, text="Masks Directory: Not selected")
        self.mask_address_label.pack()

        self.retrieve_images_button = tk.Button(self.mask_tab,
                                                text="Retrieve the spheroid IMAGE FOLDER address",
                                                command=lambda: browse_directory(self.image_dataset_path,
                                                                                 "Selected spheroid images address",
                                                                                 self.images_address_label))
        self.retrieve_images_button.pack(side=tk.TOP)

        self.images_address_label = tk.Label(self.mask_tab, text="Images Directory: Not selected")
        self.images_address_label.pack()

        self.masks_annotation_path = tk.StringVar()
        self.image_dataset_path = tk.StringVar()

        # File Dialog pro výsledné segmentované obrázky (změna na askdirectory)
        self.dataset_address_button = tk.Button(self.dialog,
                                                text="Dataset of all images address (folder of images you want to segment)",
                                                command=lambda: browse_directory(self.dataset_path,
                                                                                 "Selected dataset path",
                                                                                 self.dataset_address_label))
        self.dataset_address_button.pack(side=tk.TOP)

        self.dataset_path = tk.StringVar()

        # Indikátor pro vyplnění adresy
        self.dataset_address_label = tk.Label(self.dialog, text="Dataset Directory: Not selected")
        self.dataset_address_label.pack()

        # File Dialog pro výsledné segmentované obrázky (změna na askdirectory)
        self.output_address_button = tk.Button(self.dialog,
                                               text="Output address (folder where to save the output)",
                                               command=lambda: browse_directory(self.output_path,
                                                                                "Selected output path",
                                                                                self.output_address_label))
        self.output_address_button.pack(side=tk.TOP)

        self.output_path = tk.StringVar()

        # Indikátor pro vyplnění adresy
        self.output_address_label = tk.Label(self.dialog, text="Output Directory: Not selected")
        self.output_address_label.pack()

        # Oddělovací čára mezi adresní a metody sekce
        self.address_separator = tk.Frame(self.dialog, height=2, bd=1, relief=tk.SUNKEN)
        self.address_separator.pack(fill=tk.X, padx=5, pady=5)

        # Metodická sekce
        self.method_section_label = tk.Label(self.dialog, text="Method Settings", font=("Helvetica", 12, "bold"))
        self.method_section_label.pack()

        # Textbox pro název projektu
        self.project_name_label = tk.Label(self.dialog, text="Project Name:")
        self.project_name_label.pack()
        self.project_name_entry = tk.Entry(self.dialog)
        self.project_name_entry.pack()

        # Tlačítko pro načtení parametrů z JSON souboru
        self.load_parameters_button = tk.Button(self.dialog,
                                                text="I already know the parameters (load JSON file with parameters)",
                                                command=self.load_and_run_parameters)
        self.load_parameters_button.pack()

        # Create a frame to contain the label and button
        self.parameters_frame = tk.Frame(self.dialog)
        self.parameters_frame.pack()

        # Initially disable the "Parameters loaded" label and the "Cancel" button
        self.parameters_loaded_label = tk.Label(self.parameters_frame, text="Parameters loaded", state=tk.DISABLED)
        self.parameters_loaded_label.pack(side=tk.LEFT)

        self.cancel_button = tk.Button(self.parameters_frame, text="Cancel", command=self.cancel_parameters_loaded,
                                       state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)

        # Checkboxy pro výběr metod
        self.methods_frame = tk.Frame(self.dialog)
        self.methods_frame.pack()
        self.method_labels = ["Sauvola", "Niblack", "Gaussian"]

        self.methods_checkboxes = []

        for i, method_label in enumerate(self.method_labels):
            method_var = tk.IntVar()
            method_checkbox = tk.Checkbutton(self.methods_frame, text=method_label, variable=method_var)
            method_checkbox.grid(row=0, column=i, padx=5, pady=5)

            self.methods_checkboxes.append((method_checkbox, method_var))

        # Textová pole pro zadání parametrů
        self.parameters_frame = tk.Frame(self.dialog)
        self.parameters_frame.pack()
        self.learning_rate_label = tk.Label(self.parameters_frame, text="Learning Rate:")
        self.learning_rate_label.grid(row=0, column=0, padx=5, pady=5)
        self.learning_rate_entry = tk.Entry(self.parameters_frame)
        self.learning_rate_entry.grid(row=0, column=1, padx=5, pady=5)

        self.iterations_label = tk.Label(self.parameters_frame, text="Number of Iterations:")
        self.iterations_label.grid(row=1, column=0, padx=5, pady=5)
        self.iterations_entry = tk.Entry(self.parameters_frame)
        self.iterations_entry.grid(row=1, column=1, padx=5, pady=5)

        self.batch_size_label = tk.Label(self.parameters_frame, text="Batch Size:")
        self.batch_size_label.grid(row=3, column=0, padx=5, pady=5)
        self.batch_size_entry = tk.Entry(self.parameters_frame)
        self.batch_size_entry.grid(row=3, column=1, padx=5, pady=5)

        # Přednastavení hodnot parametrů
        self.learning_rate_entry.insert(0, "0.01")
        self.iterations_entry.insert(0, "50")
        self.batch_size_entry.insert(0, "10")

        # Oddělovací čára mezi adresní a metody sekce
        self.method_separator = tk.Frame(self.dialog, height=2, bd=1, relief=tk.SUNKEN)
        self.method_separator.pack(fill=tk.X, padx=5, pady=5)

        # Hole Finding Settings Section
        self.hole_finding_section_label = tk.Label(self.dialog, text="Hole Finding Settings",
                                                   font=("Helvetica", 12, "bold"))
        self.hole_finding_section_label.pack()

        # Frame for the checkboxes
        self.hole_finding_frame = tk.Frame(self.dialog)
        self.hole_finding_frame.pack()

        # Variables for the checkboxes
        self.detect_outer_var = tk.IntVar(value=0)
        self.detect_all_var = tk.IntVar(value=0)
        self.view_select_var = tk.IntVar(value=0)

        # Function to enforce only one checkbox can be checked
        def update_hole_finding_checkboxes(selected_var):
            vars = [self.detect_outer_var, self.detect_all_var, self.view_select_var]
            for var in vars:
                if var != selected_var:
                    var.set(0)

        # Checkboxes
        self.detect_outer_checkbox = tk.Checkbutton(self.hole_finding_frame,
                                                    text="Detect outer contours (spheroids with no holes)",
                                                    variable=self.detect_outer_var,
                                                    command=lambda: update_hole_finding_checkboxes(
                                                        self.detect_outer_var))

        self.detect_all_checkbox = tk.Checkbutton(self.hole_finding_frame,
                                                  text="Detect all contours (spheroids with holes)",
                                                  variable=self.detect_all_var,
                                                  command=lambda: update_hole_finding_checkboxes(self.detect_all_var))

        self.view_select_checkbox = tk.Checkbutton(self.hole_finding_frame,
                                                   text="View results for 'all holes' and 'no holes' and select",
                                                   variable=self.view_select_var,
                                                   command=lambda: update_hole_finding_checkboxes(self.view_select_var))

        self.detect_outer_checkbox.pack(anchor='w')  # Aligns to the west (left) of the frame
        self.detect_all_checkbox.pack(anchor='w')  # Consistent with the first checkbox
        self.view_select_checkbox.pack(anchor='w')

        # Oddělovací čára mezi adresní a metody sekce
        self.settings_separator = tk.Frame(self.dialog, height=2, bd=1, relief=tk.SUNKEN)
        self.settings_separator.pack(fill=tk.X, padx=5, pady=5)

        self.other_section_label = tk.Label(self.dialog, text="Other Settings", font=("Helvetica", 12, "bold"))
        self.other_section_label.pack()

        checkbox_frame = tk.Frame(self.dialog)
        checkbox_frame.pack()

        self.detect_corrupted_var = tk.BooleanVar()
        self.checkbox_detect_corrupted = tk.Checkbutton(checkbox_frame, text="Detect and discard corrupted images",
                                                        variable=self.detect_corrupted_var, onvalue=True,
                                                        offvalue=False)
        self.checkbox_detect_corrupted.pack(side=tk.LEFT)

        # Checkbox pro 'Create JSON file for export to CVAT'
        self.create_json_var = tk.BooleanVar()
        self.checkbox_create_json = tk.Checkbutton(checkbox_frame, text="Create JSON file for export to CVAT",
                                                   variable=self.create_json_var,
                                                   onvalue=True, offvalue=False)
        self.checkbox_create_json.pack(side=tk.LEFT)

        # Checkbox pro 'Calculate contour properties'
        self.calculate_contours_var = tk.BooleanVar()
        self.checkbox_calculate_contours = tk.Checkbutton(checkbox_frame, text="Calculate spheroid properties",
                                                          variable=self.calculate_contours_var,
                                                          onvalue=True, offvalue=False)
        self.checkbox_calculate_contours.pack(side=tk.LEFT)

        # Tlačítko pro spuštění
        self.run_button = tk.Button(self.dialog, text="Run", command=self.run_method)
        self.run_button.pack()

        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        self.stop_event = threading.Event()

    def go_back(self):
        self.dialog.destroy()
        self.selection_dialog.show()

    def on_close(self):
        self.dialog.quit()

    def get_contours_state(self):
        if self.detect_outer_var.get() == 1:
            return "no"
        elif self.detect_all_var.get() == 1:
            return "all"
        else:
            return "select"

    def show_completion_dialog(self, time_taken, output_folder):
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Segmentation Completed")

        message = f"DONE.\nSegmentation took {time_taken:.2f} seconds.\nOutput stored in a folder: {output_folder}"
        tk.Label(dialog, text=message).pack(padx=20, pady=10)

        ok_button = tk.Button(dialog, text="OK", command=lambda: [dialog.destroy(), self.reset_gui()])
        ok_button.pack(pady=10)

    def cancel_parameters_loaded(self):
        # Clear the loaded parameters
        self.loaded_parameters = {}

        # Reset the method selection
        for method_checkbox, _ in self.methods_checkboxes:
            method_checkbox.config(state=tk.NORMAL)

        # Unlock learning rate, number of iterations, and stop condition text fields
        self.learning_rate_entry.config(state=tk.NORMAL)
        self.iterations_entry.config(state=tk.NORMAL)
        self.batch_size_entry.config(state=tk.NORMAL)

        self.parameters_loaded_label.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def enable_parameter_entry(self):
        state = tk.NORMAL
        self.learning_rate_entry.config(state=state)
        self.iterations_entry.config(state=state)
        self.batch_size_entry.config(state=state)

    def load_and_run_parameters(self):
        json_file_path = filedialog.askopenfilename(
            title="Select the JSON file in which the already found optimal parameters are uploaded:",
            filetypes=[("JSON files", "*.json")])
        if json_file_path:
            self.load_json_parameters(json_file_path)
            self.run_method_with_loaded_parameters()

    def load_json_parameters(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extrahujte potřebná data
        self.loaded_method = data.get("method", "")
        self.loaded_parameters = data.get("parameters", {})
        self.detect_corrupted_var.set(data.get("detect_corrupted", False))

    def reset_gui(self):
        self.detect_corrupted_var.set(False)
        self.detect_all_var.set(False)
        self.detect_corrupted_var.set(False)
        self.detect_outer_var.set(False)
        self.create_json_var.set(False)
        self.calculate_contours_var.set(False)
        for _, var in self.methods_checkboxes:
            var.set(0)

        # Clear and enable all entry fields
        self.project_name_entry.delete(0, tk.END)
        self.learning_rate_entry.delete(0, tk.END)
        self.iterations_entry.delete(0, tk.END)
        self.batch_size_entry.delete(0, tk.END)

        self.learning_rate_entry.insert(0, "0.01")
        self.iterations_entry.insert(0, "50")
        self.batch_size_entry.insert(0, "10")

        self.enable_parameter_entry()

        # Clear all label texts
        self.coco_address_label.config(text="COCO Annotations Directory: Not selected")
        self.mask_address_label.config(text="Masks Directory: Not selected")
        self.images_address_label.config(text="Images Directory: Not selected")
        self.dataset_address_label.config(text="Dataset Directory: Not selected")
        self.output_address_label.config(text="Output Directory: Not selected")

        # Reset the loaded parameters and cancel button
        self.loaded_parameters = None
        self.loaded_method = None
        self.parameters_loaded_label.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def run_method_with_loaded_parameters(self):
        if not self.loaded_parameters:
            messagebox.showerror("Error", "No parameters loaded.")
            return

        # Předpokládá se, že tato metoda otevře dialog pro potvrzení parametrů
        parameter_entry_dialog = ParameterEntryDialog(self.dialog, self.loaded_method, self.loaded_parameters)
        self.dialog.wait_window(parameter_entry_dialog)

        if parameter_entry_dialog.result is None:
            messagebox.showinfo("Info", "Parameters were not saved.")
        else:
            self.parameters_loaded_label.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)

            loaded_method = self.loaded_method

            # Set the loaded method and lock all method checkboxes
            for checkbox, var in self.methods_checkboxes:
                if checkbox.cget("text") == loaded_method:
                    var.set(1)  # Check the loaded method's checkbox
                    checkbox.config(state=tk.DISABLED)
                else:
                    var.set(0)  # Uncheck other method checkboxes
                    checkbox.config(state=tk.DISABLED)

            # Lock learning rate, number of iterations, and stop condition text fields
            self.learning_rate_entry.config(state=tk.DISABLED)
            self.iterations_entry.config(state=tk.DISABLED)
            self.batch_size_entry.config(state=tk.DISABLED)

    def run_method(self):
        project_name = self.project_name_entry.get()

        hole_finding_options = [self.detect_outer_var.get(), self.detect_all_var.get(), self.view_select_var.get()]
        if sum(hole_finding_options) != 1:
            messagebox.showerror("Error", "Exactly one hole finding option must be selected.")
            return

        if self.loaded_parameters is None:
            current_tab = self.notebook.nametowidget(self.notebook.select())

            # Check for the COCO or masks paths based on the selected method
            if current_tab == self.coco_tab and not self.coco_annotation_path.get():
                messagebox.showerror("Error", "The COCO annotations path must be filled.")
                return
            elif current_tab == self.mask_tab:
                if not self.masks_annotation_path.get() or not self.image_dataset_path.get():
                    messagebox.showerror("Error", "Both masks and image dataset paths must be filled.")
                    return

            # Check that dataset and output addresses are always filled
        if not all([self.dataset_path.get(), self.output_path.get()]):
            messagebox.showerror("Error", "Both 'Image Dataset Path' and 'Output Path' must be filled.")
            return

        if not project_name:
            messagebox.showerror("Error", "Project name must be filled in.")
            return

        if self.loaded_parameters is None and not any(var.get() == 1 for _, var in self.methods_checkboxes):
            messagebox.showerror("Error", "At least one of the four segmentation methods must be selected.")
            return

        if self.loaded_parameters is None:
            if current_tab == self.coco_tab:
                annotation_address = self.coco_annotation_path.get()
                annotation_address = fm.unzip(annotation_address)
                annotations_address, images_address = update_addresses(annotation_address)
                annotation_data = fm.load_annotations(
                    os.path.join(annotations_address, 'instances_default.json'), images_address)
                print(f"Loaded {len(annotation_data)} annotated images")
            elif current_tab == self.mask_tab:
                mask_adress = self.masks_annotation_path.get()
                images_address = self.image_dataset_path.get()
                annotation_data = fm.load_masks_from_images(mask_adress, images_address)
                print(f"Loaded {len(annotation_data)} annotated images")
        else:
            annotation_data = None

        dataset_address = self.dataset_path.get()
        output_address = self.output_path.get()

        algorithms = [method for method, (checkbox, var) in
                      zip(["Sauvola", "Niblack", "Gaussian"], self.methods_checkboxes) if
                      var.get() == 1]

        # Načtené parametry z JSON souboru, pokud jsou k dispozici
        if self.loaded_parameters:
            parameters = self.loaded_parameters
            progress_window1 = None
        else:
            parameters = None
            progress_window1 = OptimizationProgressWindow(self.dialog)
            progress_window1.update_info(project_name, algorithms, 0, "Unknown", "Unknown", "Unknown")
            progress_window1.withdraw()

        contours_state = self.get_contours_state()
        detect_corrupted = self.detect_corrupted_var.get()
        create_json = self.create_json_var.get()
        calculate_properties = self.calculate_contours_var.get()

        progress_window2 = ProcessingProgressWindow(self.dialog)
        progress_window2.update_progress("Initializing...")
        progress_window2.withdraw()

        run_thread = threading.Thread(target=self.run_main, args=(
            annotation_data, dataset_address, output_address, project_name, algorithms, parameters,
            contours_state, detect_corrupted, create_json, calculate_properties, progress_window1,
            progress_window2))
        run_thread.start()

    def run_main(self, annotation_data, dataset_address, output_address, project_name, algorithms, known_parameters,
                 contours_state, detect_corrupted, create_json, calculate_properties, progress_window1,
                 progress_window2):
        totalTime = time.time()

        for algorithm in algorithms:
            startTime = time.time()

            if known_parameters is None:
                learning_rate = float(self.learning_rate_entry.get())
                num_iterations = int(self.iterations_entry.get())
                stop_condition = 0.0002
                batch_size = int(self.batch_size_entry.get())
                progress_window1.deiconify()
                parameters, iou = g.GradientDescent(annotation_data, output_address, project_name, algorithm,
                                                    learning_rate,
                                                    num_iterations, stop_condition, batch_size, F.IoU, progress_window1,
                                                    contours_state=contours_state,
                                                    detect_corrupted=detect_corrupted).run()
                print(f"Resulting parameters: {parameters}", f"IoU: {round(iou * 100, 2)}%")
                progress_window1.withdraw()
            else:
                parameters = known_parameters

            progress_window2.deiconify()
            F.Contours(self.dialog, dataset_address, output_address, project_name, algorithm, parameters,
                       False, F.IoU, contours_state, detect_corrupted, create_json, calculate_properties,
                       progress_window2).run()
            print(f"Segmentation of the project took: {round(time.time() - startTime)} seconds")
            progress_window2.withdraw()

        print(f"Total time: {round(time.time() - totalTime)} seconds")

        # Zobrazit dialogové okno po dokončení segmentace
        self.show_completion_dialog(round(time.time() - totalTime), output_address)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Optionally hide the root window
    app = SelectionDialog(root)
    root.mainloop()
