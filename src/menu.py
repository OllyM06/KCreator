import os
import json
import sys
from pathlib import Path
from modules.style_tools import auto_hook, enable_auto_refresh

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
try:
    from PIL import Image, ImageTk  # Pillow for image resizing
except ImportError:
    Image = None
    ImageTk = None

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULTS_DIR = os.path.join(SRC_DIR, "defaults")


def start_main(parts_data, mod_name, workspace_dir, mod_version, mod_author):
    import main as main
    main.start_app(parts_data, mod_name, workspace_dir, mod_version, mod_author)


class KCreatorMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KCreator")
        self.geometry("400x400")
        self.iconbitmap(os.path.join(ROOT_DIR, "KCreator.ico"))

        # Project state
        self.parts_data = ""
        self.mod_name = ""
        self.mod_logo = ""
        self.mod_version = ""
        self.mod_author = ""
        self.workspace_dir = ""

        # AppData setup
        self.appdata = Path(os.getenv('APPDATA')) / "KCreator"
        self.appdata.mkdir(parents=True, exist_ok=True)
        self.recent_path = self.appdata / "recent.json"

        # Ensure recent.json exists
        if not self.recent_path.exists():
            with open(self.recent_path, "w") as f:
                json.dump({"recent_files": []}, f)


        self._images = []  # keep references to PhotoImage objects
        self.build_ui()

    # ---------------- Recent file handling ----------------
    def update_recent(self, filepath):
        try:
            with open(self.recent_path, "r") as rf:
                recent_files = json.load(rf).get("recent_files", [])
        except Exception:
            recent_files = []

        if filepath not in recent_files:
            recent_files.append(filepath)

        with open(self.recent_path, "w") as rf:
            json.dump({"recent_files": recent_files}, rf, indent=4)

    def remove_recent(self, filepath, label_widget):
        try:
            with open(self.recent_path, "r") as f:
                recent_files = json.load(f).get("recent_files", [])
            if filepath in recent_files:
                recent_files.remove(filepath)
                with open(self.recent_path, "w") as f:
                    json.dump({"recent_files": recent_files}, f, indent=4)
            self.build_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove recent: {e}")

    def view_recent(self, frame, event=None):
        try:
            with open(self.recent_path, "r") as f:
                recent_files = json.load(f).get("recent_files", [])
        except Exception:
            recent_files = []

        # Filter out files that no longer exist
        existing_files = [f for f in recent_files if os.path.exists(f)]
        if len(existing_files) != len(recent_files):
            with open(self.recent_path, "w") as f:
                json.dump({"recent_files": existing_files}, f, indent=4)
            recent_files = existing_files

        if not recent_files:
            tk.Label(frame, text="No recent projects").pack(pady=5)
            return

        for file in recent_files:
            try:
                with open(file, "r") as pf:
                    pdata = json.load(pf)
                    mod_name = pdata.get("mod_name", os.path.basename(file))
                    mod_logo = pdata.get("mod_logo", "")
            except Exception:
                mod_name = os.path.basename(file)
                mod_logo = ""

            mod_photo = None
            if Image is not None and ImageTk is not None and mod_logo and os.path.exists(mod_logo):
                try:
                    img = Image.open(mod_logo)
                    img.thumbnail((64, 64))
                    mod_photo = ImageTk.PhotoImage(img)
                    self._images.append(mod_photo)
                except Exception:
                    mod_photo = None

            lbl = tk.Label(
                frame,
                text=mod_name,
                fg="blue",
                cursor="hand2",
                font=("Arial", 24),
                image=mod_photo,
                compound="left"
            )
            lbl.bind("<Button-1>", lambda e, path=file: self.open_recent(path))
            lbl.bind("<Button-3>", lambda e, path=file, widget=lbl, name=mod_name: self.show_menu(e, path, widget, name))
            lbl.pack(pady=2, anchor="w")

    # ---------------- UI ----------------
    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        print(self.recent_path)
        print("APPDATA =", os.getenv("APPDATA"))


        recent_frm = tk.Frame(self, relief="sunken", borderwidth=1.5)

        label = tk.Label(self, text="Welcome to KCreator!", font=("Arial", 16))
        label.pack(pady=20)

        new_button = tk.Button(self, text="New Project", command=self.new_project)
        new_button.pack(pady=5)

        open_button = tk.Button(self, text="Open Project from File", command=self.open_project)
        open_button.pack(pady=5)

        recent_frm.pack(fill="x", padx=10, pady=8)
        tk.Label(recent_frm, text="Recent Projects:", font=("Arial", 10, "bold")).pack(pady=5)
        sep = ttk.Separator(recent_frm, orient="horizontal")
        sep.pack(fill="x", pady=5)
        # then populate recent projects
        self.view_recent(recent_frm)
        sep = ttk.Separator(recent_frm, orient="horizontal")
        sep.pack(fill="x", pady=10)

        refresh_button = tk.Button(self, text="Refresh Recent", command=self.build_ui)
        refresh_button.pack(pady=5)

        exit_button = tk.Button(self, text="Exit", command=self.quit)
        exit_button.pack(pady=5)

    def show_menu(self, event, filepath, label_widget, mod_name):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Open in Explorer", command=lambda: self.open_in_explorer(filepath))
        menu.add_command(label="Remove from Recent", command=lambda: self.remove_recent(filepath, label_widget))
        menu.add_command(label="Change Icon", command=lambda: self.change_icon(filepath))
        menu.tk_popup(event.x_root, event.y_root)

    def open_in_explorer(self, filepath):
        try:
            folder = os.path.dirname(filepath)
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Explorer: {e}")

    # ---------------- Project management ----------------
    def new_project(self):
        mod = simpledialog.askstring("Mod Name", "Enter the mod name:")
        if not mod:
            return
        author = simpledialog.askstring("Author Username", "Enter the Author username:")
        if not author:
            return
        workspace_dir = filedialog.askdirectory(title="Select workspace directory")
        if not workspace_dir:
            return

        mod_logo = filedialog.askopenfilename(
            title="Select Mod Logo. Leave empty for default",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not mod_logo:
            mod_logo = os.path.join(DEFAULTS_DIR, "logo.png")

        self.mod_name = mod
        self.mod_author = author
        self.workspace_dir = workspace_dir
        self.mod_logo = mod_logo
        self.mod_version = 0.0

        mod_dir = os.path.join(self.workspace_dir, self.mod_name)
        os.makedirs(mod_dir, exist_ok=True)
        os.makedirs(os.path.join(mod_dir, "packaged"), exist_ok=True)

        self.parts_data = os.path.join(mod_dir, "parts.json")
        with open(self.parts_data, "w") as f:
            json.dump(
                {
                    "mod_name": self.mod_name,
                    "mod_author": self.mod_author,
                    "mod_logo": self.mod_logo,
                    "mod_version": self.mod_version,
                    "parts": {}
                },
                f,
                indent=4
            )

        self.update_recent(self.parts_data)
        self.destroy()
        start_main(self.parts_data, self.mod_name, self.workspace_dir, self.mod_version, self.mod_author)

    def open_project(self):
        filename = filedialog.askopenfilename(
            title="Open project file",
            filetypes=[("Project Files", "*.json *.json")]
        )
        if not filename:
            return

        try:
            with open(filename, "r") as f:
                data = json.load(f)
            self.parts_data = filename
            self.workspace_dir = os.path.dirname(filename)
            self.mod_name = data.get("mod_name", "Unknown")
            self.mod_author = data.get("mod_author", "KSPModCreator")
            self.mod_version = data.get("mod_version", "0.1.0")

            self.update_recent(filename)
            self.destroy()
            start_main(self.parts_data, self.mod_name, self.workspace_dir, self.mod_version, self.mod_author)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def open_recent(self, filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            self.parts_data = filepath
            self.workspace_dir = os.path.dirname(filepath)
            self.mod_name = data.get("mod_name", "Unknown")
            self.mod_author = data.get("mod_author", "KSPModCreator")
            self.mod_version = data.get("mod_version", "0.1.0")

            self.destroy()
            start_main(self.parts_data, self.mod_name, self.workspace_dir, self.mod_version, self.mod_author)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def change_icon(self, mod_data):
        new_logo = filedialog.askopenfilename(
            title="Select New Mod Logo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not new_logo:
            return

        try:
            with open(mod_data, "r") as f:
                data = json.load(f)
            data["mod_logo"] = new_logo
            with open(mod_data, "w") as f:
                json.dump(data, f, indent=4)
            self.build_ui()  # refresh UI to show new logo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change icon: {e}")

def start_menu():
    app = KCreatorMenu()
    # Apply dark mode styling and auto-refresh hooks
    auto_hook(app)  # auto-apply dark mode to all widgets
    enable_auto_refresh(app)  # ensure new widgets also get styled
    app.mainloop()


if __name__ == "__main__":
    start_menu()

