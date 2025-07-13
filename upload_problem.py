import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, MULTIPLE
from tkcalendar import DateEntry
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_DIR = os.path.join(SCRIPT_DIR, "problems")
INDEX_FILE = os.path.join(PROBLEMS_DIR, "index.json")
TAGS_FILE = os.path.join(SCRIPT_DIR, "tags.json")

IMAGE_NAME = "problem.png"
TEXT_NAME = "discussion.txt"
EXTRAS_DIR_NAME = "extras"

def ensure_problems_dir():
    os.makedirs(PROBLEMS_DIR, exist_ok=True)
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w") as f:
            json.dump([], f)

def load_tags():
    if not os.path.exists(TAGS_FILE):
        return []
    with open(TAGS_FILE, "r") as f:
        return json.load(f)

def update_index(date_str, tags, extras_files):
    try:
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        index = []

    # Remove existing entry for this date
    index = [item for item in index if (item != date_str and not (isinstance(item, dict) and item.get("date") == date_str))]

    # Add new entry
    entry = {"date": date_str, "tags": tags}
    if extras_files:
        entry["extras"] = extras_files
    else:
        entry["extras"] = []

    index.append(entry)
    index.sort(key=lambda x: x if isinstance(x, str) else x["date"])

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

def submit():
    date_str = date_picker.get_date().strftime("%Y-%m-%d")
    discussion = discussion_box.get("1.0", "end-1c").strip()
    image_path = image_path_var.get()

    selected_indices = tag_listbox.curselection()
    selected_tags = [available_tags[i] for i in selected_indices]

    if not date_str or not discussion or not image_path:
        messagebox.showerror("Error", "Date, discussion and main image are required.")
        return

    target_folder = os.path.join(PROBLEMS_DIR, date_str)
    os.makedirs(target_folder, exist_ok=True)

    # Copy main image
    shutil.copy(image_path, os.path.join(target_folder, IMAGE_NAME))

    # Save discussion
    with open(os.path.join(target_folder, TEXT_NAME), "w", encoding="utf-8") as f:
        f.write(discussion)

    # Handle extras folder and files
    extras_folder = os.path.join(target_folder, EXTRAS_DIR_NAME)
    os.makedirs(extras_folder, exist_ok=True)

    extras_files = []
    for extra_path in extra_images_paths:
        filename = os.path.basename(extra_path)
        dest_path = os.path.join(extras_folder, filename)
        shutil.copy(extra_path, dest_path)
        extras_files.append(f"{EXTRAS_DIR_NAME}/{filename}")

    update_index(date_str, selected_tags, extras_files)

    messagebox.showinfo("Success", f"Problem added under {target_folder}")
    root.destroy()

def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image_path_var.set(file_path)

def browse_extras():
    files = filedialog.askopenfilenames(title="Select extra images",
                                        filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if files:
        # Add new files cumulatively, ignore duplicates
        for f in files:
            if f not in extra_images_paths:
                extra_images_paths.append(f)
        update_extras_listbox()

def update_extras_listbox():
    extras_listbox.delete(0, tk.END)
    for f in extra_images_paths:
        extras_listbox.insert(tk.END, os.path.basename(f))

def remove_selected_extra(event):
    # Remove clicked extra
    sel = extras_listbox.curselection()
    if not sel:
        return
    idx = sel[0]
    removed = extra_images_paths.pop(idx)
    update_extras_listbox()

# GUI Setup
root = tk.Tk()
root.title("Math Club Problem Uploader")

ensure_problems_dir()
available_tags = load_tags()
extra_images_paths = []

tk.Label(root, text="Select Problem Date:").pack(pady=(10,0))
date_picker = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, year=date.today().year)
date_picker.pack(pady=5)

tk.Label(root, text="Select Problem Image:").pack()
image_path_var = tk.StringVar()
img_entry_frame = tk.Frame(root)
img_entry_frame.pack(pady=5, fill=tk.X, padx=10)
tk.Entry(img_entry_frame, textvariable=image_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(img_entry_frame, text="Browse", command=browse_image).pack(side=tk.LEFT, padx=5)

# Frame for Discussion and Tags side by side
content_frame = tk.Frame(root)
content_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

# Discussion on left
discussion_frame = tk.Frame(content_frame)
discussion_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(discussion_frame, text="Discussion:").pack(anchor="w")
discussion_box = tk.Text(discussion_frame, width=50, height=12)
discussion_box.pack(fill=tk.BOTH, expand=True)

# Tags on right
tags_frame = tk.Frame(content_frame)
tags_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))

tk.Label(tags_frame, text="Select Tags:").pack(anchor="w")
tag_listbox = Listbox(tags_frame, selectmode=MULTIPLE, exportselection=False,
                      height=min(len(available_tags), 10), width=25)
for tag in available_tags:
    tag_listbox.insert(tk.END, tag)
tag_listbox.pack(fill=tk.Y, expand=False)

# Extras section below tags (still on right side)
tk.Label(tags_frame, text="Extra Images:").pack(anchor="w", pady=(15,0))
extras_btn = tk.Button(tags_frame, text="Add Extra Images", command=browse_extras)
extras_btn.pack(pady=5)

extras_listbox = Listbox(tags_frame, height=6, width=25)
extras_listbox.pack(fill=tk.Y, expand=False)
extras_listbox.bind('<<ListboxSelect>>', remove_selected_extra)

tk.Button(root, text="Submit", command=submit).pack(pady=15)

root.mainloop()
