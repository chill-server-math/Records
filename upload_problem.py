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

def update_index(date_str, tags):
    try:
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        index = []

    # Remove any existing entry for this date
    index = [item for item in index if (item != date_str and not (isinstance(item, dict) and item.get("date") == date_str))]

    # Add new entry
    index.append({"date": date_str, "tags": tags})
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
        messagebox.showerror("Error", "All fields are required.")
        return

    target_folder = os.path.join(PROBLEMS_DIR, date_str)
    os.makedirs(target_folder, exist_ok=True)

    shutil.copy(image_path, os.path.join(target_folder, IMAGE_NAME))

    with open(os.path.join(target_folder, TEXT_NAME), "w", encoding="utf-8") as f:
        f.write(discussion)

    update_index(date_str, selected_tags)

    messagebox.showinfo("Success", f"Problem added under {target_folder}")
    root.destroy()

def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image_path_var.set(file_path)

# GUI Setup
root = tk.Tk()
root.title("Chill Sever Math Problem Uploader")

ensure_problems_dir()
available_tags = load_tags()

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

tk.Button(root, text="Submit", command=submit).pack(pady=15)

root.mainloop()
