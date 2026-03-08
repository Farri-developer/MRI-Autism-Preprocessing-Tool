import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import shutil

MRI_PATH = r"D:\MRI"
RAW_PATH = r"D:\MRI\Raw"
CSV_PATH = r"D:\MRI\5320_ABIDE_Phenotypics_20251123.csv"

OUTPUT_CSV = os.path.join(MRI_PATH, "final_dataset.csv")
FILTERED_CSV = os.path.join(MRI_PATH, "filtered_dataset.csv")
DEST_FOLDER = r"D:\MRI\Filtered_Data"

def create_dataset():

    try:

        df = pd.read_csv(CSV_PATH)

        results = []
        missing = []

        for index, row in df.iterrows():

            subject_id = row["Anonymized ID"]
            folder_path = os.path.join(RAW_PATH, subject_id)

            if os.path.exists(folder_path):

                results.append({
                    "ID": subject_id,
                    "Folder_Path": folder_path,
                    "Age": row["AgeAtScan"],
                    "Sex": row["Sex"],
                    "DxGroup": row["DxGroup"],
                    "SUB_TYPE": row["Subject Type"]
                })

            else:
                missing.append(subject_id)

        df_final = pd.DataFrame(results)
        df_final.to_csv(OUTPUT_CSV, index=False)

        messagebox.showinfo("Success", "Dataset CSV Created Successfully")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -----------------------------------
# CSV INFO + AGE FILTER
# -----------------------------------

def show_csv_info():

    try:

        if not os.path.exists(OUTPUT_CSV):
            messagebox.showerror("Error", "Dataset CSV not found")
            return

        df = pd.read_csv(OUTPUT_CSV)

        min_age_filter = min_age_entry.get()
        max_age_filter = max_age_entry.get()

        if min_age_filter and max_age_filter:
            df = df[(df["Age"] >= float(min_age_filter)) &
                    (df["Age"] <= float(max_age_filter))]

        total = len(df)

        autism = (df["DxGroup"] == 1).sum()
        control = (df["DxGroup"] == 2).sum()

        male = (df["Sex"] == 1).sum()
        female = (df["Sex"] == 2).sum()

        min_age = df["Age"].min()
        max_age = df["Age"].max()

        stats = f"""
FILTERED DATASET INFO

Total Subjects : {total}

Autism (DxGroup=1) : {autism}
Control (DxGroup=2) : {control}

Male (Sex=1) : {male}
Female (Sex=2) : {female}

Minimum Age : {min_age}
Maximum Age : {max_age}
"""

        messagebox.showinfo("CSV Statistics", stats)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -----------------------------------
# EXPORT FILTERED CSV
# -----------------------------------

def export_filtered_csv():

    try:

        if not os.path.exists(OUTPUT_CSV):
            messagebox.showerror("Error", "Dataset CSV not found")
            return

        df = pd.read_csv(OUTPUT_CSV)

        min_age_filter = min_age_entry.get()
        max_age_filter = max_age_entry.get()

        if min_age_filter and max_age_filter:
            df = df[(df["Age"] >= float(min_age_filter)) &
                    (df["Age"] <= float(max_age_filter))]

        # Age ko integer bana do
        df["Age"] = df["Age"].astype(int)

        df.to_csv(FILTERED_CSV, index=False)

        messagebox.showinfo(
            "Export Complete",
            f"Filtered CSV created\n\nFile:\n{FILTERED_CSV}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))



def copy_filtered_folders():

    try:

        if not os.path.exists(FILTERED_CSV):
            messagebox.showerror("Error", "Filtered CSV not found")
            return

        df = pd.read_csv(FILTERED_CSV)

        # destination folder create
        if not os.path.exists(DEST_FOLDER):
            os.makedirs(DEST_FOLDER)

        copied = 0

        for folder in df["Folder_Path"]:

            if os.path.exists(folder):

                folder_name = os.path.basename(folder)

                destination = os.path.join(DEST_FOLDER, folder_name)

                if not os.path.exists(destination):
                    shutil.copytree(folder, destination)
                    copied += 1

        messagebox.showinfo(
            "Completed",
            f"Folders Copied: {copied}\n\nDestination:\n{DEST_FOLDER}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


import gzip
import threading
def extract_mprage_files():

    try:

        processed = 0

        for subject in os.listdir(DEST_FOLDER):

            subject_path = os.path.join(DEST_FOLDER, subject)

            if not os.path.isdir(subject_path):
                continue

            found_file = None
            session_folder = None

            for root_dir, dirs, files in os.walk(subject_path):

                for file in files:

                    if "mprage" in file.lower() and file.lower().endswith(".nii.gz"):

                        found_file = os.path.join(root_dir, file)

                        # session folder save karo
                        session_folder = root_dir.split(subject_path)[1].split("\\")[1]

                        break

                if found_file:
                    break

            if found_file:

                destination = os.path.join(subject_path, "MPRAGE.nii")

                with gzip.open(found_file, 'rb') as f_in:
                    with open(destination, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # session folder delete
                for item in os.listdir(subject_path):

                    item_path = os.path.join(subject_path, item)

                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)

                processed += 1

        messagebox.showinfo(
            "Completed",
            f"MPRAGE extracted from {processed} subjects"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

        # ---------------- GUI ----------------

root = tk.Tk()
root.title("MRI Autism Dataset Builder")
root.geometry("520x390")

title = tk.Label(root, text="MRI Autism Dataset Creator",
                 font=("Arial", 14, "bold"))
title.pack(pady=10)

# Create Dataset
btn_create = tk.Button(root, text="Create Dataset CSV",
                       command=create_dataset, width=25, height=2)
btn_create.pack(pady=10)

# Age Filter
age_label = tk.Label(root, text="Age Filter")
age_label.pack()

frame = tk.Frame(root)
frame.pack(pady=5)

tk.Label(frame, text="Min Age").grid(row=0, column=0)
min_age_entry = tk.Entry(frame, width=10)
min_age_entry.grid(row=0, column=1)

tk.Label(frame, text="Max Age").grid(row=0, column=2)
max_age_entry = tk.Entry(frame, width=10)
max_age_entry.grid(row=0, column=3)

# Show CSV Info
btn_info = tk.Button(root, text="Show CSV Info",
                     command=show_csv_info, width=25, height=2)
btn_info.pack(pady=10)

# NEW BUTTON
btn_export = tk.Button(root, text="Export Filtered CSV",
                       command=export_filtered_csv, width=25, height=2)
btn_export.pack(pady=10)


btn_copy = tk.Button(root, text="Copy Filtered Folders",
                     command=copy_filtered_folders, width=25, height=2)
btn_copy.pack(pady=10)

btn_extract = tk.Button(root, text="Extract MPRAGE Files",
                        command=lambda: threading.Thread(target=extract_mprage_files).start(),
                        width=25, height=2)

btn_extract.pack(pady=10)

root.mainloop()