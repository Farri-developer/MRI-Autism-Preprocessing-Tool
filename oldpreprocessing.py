import tkinter as tk
from tkinter import filedialog, messagebox
import nibabel as nib
import numpy as np
from scipy.ndimage import zoom
import os

def preprocess_pipeline(file_path):

    try:
        status_label.config(text="Running HD-BET (skull removal)...")
        root.update()

        base = os.path.dirname(file_path)
        name = os.path.splitext(os.path.basename(file_path))[0]

        skull_removed = os.path.join(base, name + "_brain.nii.gz")

        os.system(f'hd-bet -i "{file_path}" -o "{skull_removed}" -device cuda --disable_tta')

        if not os.path.exists(skull_removed):
            raise Exception("HD-BET failed. Output file not created.")

        status_label.config(text="Loading MRI...")
        root.update()

        img = nib.load(skull_removed)
        data = img.get_fdata()

        status_label.config(text="Resizing MRI to 128x128x128...")
        root.update()

        target = (128,128,128)

        factors = (
            target[0] / data.shape[0],
            target[1] / data.shape[1],
            target[2] / data.shape[2]
        )

        data = zoom(data, factors)

        status_label.config(text="Normalizing intensity...")
        root.update()

        data = (data - data.min()) / (data.max() - data.min())

        status_label.config(text="Adding channel dimension...")
        root.update()

        data = np.expand_dims(data, axis=-1)

        status_label.config(text="Saving file to Desktop...")
        root.update()

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")

        output_path = os.path.join(desktop, name + "_preprocessed.nii")

        new_img = nib.Nifti1Image(data[:,:,:,0], img.affine)

        nib.save(new_img, output_path)

        status_label.config(text="Completed ✔")

        messagebox.showinfo("Success", f"Preprocessed MRI saved to:\n{output_path}")

    except Exception as e:

        status_label.config(text="Error occurred")
        messagebox.showerror("Error", str(e))


def select_file():

    file_path = filedialog.askopenfilename(
        title="Select MRI File",
        filetypes=[("NIfTI files", "*.nii")]
    )

    if file_path:
        preprocess_pipeline(file_path)


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("MRI Preprocessing Tool (CNN Ready)")
root.geometry("450x260")
root.resizable(False, False)

title = tk.Label(
    root,
    text="MRI Preprocessing Tool",
    font=("Arial",16,"bold")
)

title.pack(pady=20)

btn = tk.Button(
    root,
    text="Select MRI (.nii)",
    font=("Arial",12),
    width=20,
    height=2,
    command=select_file
)

btn.pack(pady=20)

status_label = tk.Label(
    root,
    text="Waiting for file selection...",
    font=("Arial",10)
)

status_label.pack(pady=10)

root.mainloop()