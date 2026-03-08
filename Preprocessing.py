import tkinter as tk
from tkinter import messagebox
import nibabel as nib
import numpy as np
from scipy.ndimage import zoom
import os
import subprocess
import threading

INPUT_FOLDER = r"D:\MRI\Filter mri"
OUTPUT_FOLDER = r"D:\MRI\preprocess"


def preprocess_all():

    try:

        subjects = os.listdir(INPUT_FOLDER)
        total = 0

        for subject in subjects:

            subject_path = os.path.join(INPUT_FOLDER, subject)

            if not os.path.isdir(subject_path):
                continue

            file_path = os.path.join(subject_path, "MPRAGE.nii")

            if not os.path.exists(file_path):
                print("MRI not found:", subject)
                continue

            status_label.config(text=f"Processing {subject}...")
            root.update()

            # -------- HD-BET Skull Removal --------

            skull_removed = os.path.join(subject_path, "MPRAGE_brain.nii.gz")

            subprocess.run([
                "hd-bet",
                "-i", file_path,
                "-o", skull_removed,
                "-device", "cuda",
                "--disable_tta"
            ])

            if not os.path.exists(skull_removed):
                print("HD-BET failed:", subject)
                continue

            # -------- Load MRI --------

            img = nib.load(skull_removed)
            data = img.get_fdata()

            # -------- Resize --------

            target = (128,128,128)

            factors = (
                target[0] / data.shape[0],
                target[1] / data.shape[1],
                target[2] / data.shape[2]
            )

            data = zoom(data, factors)

            # -------- Normalize --------

            data = (data - data.min()) / (data.max() - data.min())

            # -------- Save --------

            out_folder = os.path.join(OUTPUT_FOLDER, subject)
            os.makedirs(out_folder, exist_ok=True)

            output_path = os.path.join(out_folder, "MPRAGE.nii")

            new_img = nib.Nifti1Image(data, img.affine)
            nib.save(new_img, output_path)

            total += 1

        status_label.config(text="Completed ✔")

        messagebox.showinfo(
            "Finished",
            f"{total} MRIs processed\nSaved in:\n{OUTPUT_FOLDER}"
        )

    except Exception as e:

        status_label.config(text="Error occurred")
        messagebox.showerror("Error", str(e))


# -------- Run in thread (GUI freeze fix) --------

def start_processing():
    threading.Thread(target=preprocess_all).start()


# -------- GUI --------

root = tk.Tk()
root.title("MRI Batch Preprocessing")
root.geometry("450x260")

title = tk.Label(root, text="MRI Batch Preprocessing (HD-BET + GPU)", font=("Arial",16,"bold"))
title.pack(pady=20)

btn = tk.Button(root, text="Start Preprocessing", width=22, height=2, command=start_processing)
btn.pack(pady=20)

status_label = tk.Label(root, text="Waiting to start...")
status_label.pack()

root.mainloop()