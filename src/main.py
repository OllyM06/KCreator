import os
import json
import webbrowser
import customtkinter as tk
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tkinter import ttk, filedialog, messagebox, simpledialog
from modules.UI_tools import ToolTip
from modules.image_tools import check_flag_size
from modules.packager import pkg_parts, pkg_flags
import menu

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULTS_DIR = os.path.join(SRC_DIR, "defaults")

class KCreator(tk.CTk):
    def __init__(self, parts_data, mod_name, workspace_dir, mod_ver, mod_author):
        super().__init__()

        self.parts_data = parts_data
        self.mod_name = mod_name
        self.mod_version = mod_ver
        self.mod_author = mod_author
        self.workspace_dir = workspace_dir
        self.version = "0.0.0"

        self.title(f"{self.mod_name} KCreator v{self.version}")
        self.geometry("700x420")
        self.iconbitmap(os.path.join(ROOT_DIR, "KCreator.ico"))
        self.part_type = None
        self.editing_part_name = None
        self.build_ui()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def build_ui(self):
        self.clear_window()

        frm = tk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=8)

        bold_font = ("Arial", 10, "bold")
        big_bold_font = ("Arial", 24, "bold")

        frm.grid_columnconfigure(0, weight=1)
        frm.grid_rowconfigure(1, weight=1)

        # ---------------- MAIN BUTTON ----------------
        new = tk.CTkButton(frm, text="+ New Part", font=big_bold_font)
        new.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # ---------------- DROPDOWN ----------------
        dropdown = tk.CTkFrame(frm)
        dropdown.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        dropdown.grid_remove()

        tk.CTkButton(
            dropdown,
            text="Fuel Tank",
            command=lambda: self.create_part("FT")
        ).pack(fill="x", padx=5, pady=2)

        tk.CTkButton(
            dropdown,
            text="Engine",
            command=lambda: self.create_part("ENG")
        ).pack(fill="x", padx=5, pady=2)

        tk.CTkButton(
            dropdown,
            text="Flag",
            command=lambda: self.create_part("FLAG")
        ).pack(fill="x", padx=5, pady=2)

        # ---------------- TOGGLE LOGIC ----------------
        def toggle_dropdown():
            if dropdown.winfo_ismapped():
                dropdown.grid_remove()
            else:
                dropdown.lift()
                dropdown.grid()

        new.configure(command=toggle_dropdown)

        # REMOVE GLOBAL BIND COMPLETELY (FIXES)
        # self.bind("<Button-1>", close_dropdown)

        # ---------------- LOAD DATA ----------------
        with open(self.parts_data, "r") as f:
            data = json.load(f)

        # ---------------- TITLE ----------------
        tk.CTkLabel(frm, text="Created Parts:", font=bold_font).grid(
            row=2, column=0, sticky="w", padx=10, pady=(10, 5)
        )

        # ---------------- PART LIST ----------------
        list_frame = tk.CTkFrame(frm)
        list_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=(0, 10))
        for col in range(4):
            list_frame.grid_columnconfigure(col, weight=1, uniform="part_cols")

        if not data.get("parts"):
            tk.CTkLabel(list_frame, text="No Parts Created Yet").grid(row=0, column=0, sticky="w", padx=20, pady=5)
        else:
            for i, (part_name, part_info) in enumerate(data["parts"].items()):
                row = i // 4
                col = i % 4
                info = tk.CTkLabel(
                    list_frame,
                    text=f"{part_name}: {part_info.get('type', 'Unknown')}",
                    text_color="white",
                    cursor="hand2",
                    justify="left",
                    wraplength=140
                )
                info.grid(row=row, column=col, sticky="w", padx=10, pady=2)
                info.bind("<Button-1>", lambda e, name=part_name: self.view_info(name))

        # ---------------- BOTTOM BUTTONS ----------------
        bottom_frame = tk.CTkFrame(frm)
        bottom_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        tk.CTkButton(
            bottom_frame,
            text="Delete All Parts",
            fg_color="red",
            command=self.delete_all
        ).grid(row=0, column=0, padx=10, pady=6)

        tk.CTkButton(
            bottom_frame,
            text="Package Parts",
            command=self.run_packager
        ).grid(row=0, column=1, padx=10, pady=6)

    def view_info(self, part_name):
        self.clear_window()
        with open(f"{self.parts_data}", "r") as f:
            data = json.load(f)
            part = data["parts"].get(part_name, {})

        tk.CTkLabel(self, text=f"Part Name: {part_name}", font=("Arial", 12, "bold")).pack(pady=5)
        tk.CTkLabel(self, text=f"Type: {part.get('type', 'Unknown')}").pack(pady=5)


        if part['type'] == "Fuel Tank":
            tk.CTkLabel(self, text=f"Description: {part.get('description', 'N/A')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Model: {part.get('model', part.get('texture', 'N/A'))}").pack(pady=5)
            tk.CTkLabel(self, text=f"Capacity: {part.get('capacity', 'N/A')} units").pack(pady=5)
            tk.CTkLabel(self, text=f"Entry Cost: {part.get('entry_cost', '1000')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Cost: {part.get('cost', '150')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Max Temp: {part.get('max_temp', '2000')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Node Stack Top: {part.get('node_stack_top', 'N/A')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Node Stack Bottom: {part.get('node_stack_bottom', 'N/A')}").pack(pady=5)
        elif part['type'] == "Engine":
            tk.CTkLabel(self, text=f"Description: {part.get('description', 'N/A')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Model: {part.get('model', part.get('texture', 'N/A'))}").pack(pady=5)
            tk.CTkLabel(self, text=f"Thrust: {part.get('thrust', 'N/A')} kN").pack(pady=5)
            tk.CTkLabel(self, text=f"Fuel Type: {part.get('fuel_type', 'N/A')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Entry Cost: {part.get('entry_cost', '1000')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Cost: {part.get('cost', '150')}").pack(pady=5)
            tk.CTkLabel(self, text=f"Max Temp: {part.get('max_temp', '2000')}").pack(pady=5)
        elif part['type'] == "Flag":
            tk.CTkLabel(self, text=f"Texture: {part.get('texture', 'N/A')}").pack(pady=5)

        if part['type'] != "Flag":
            tk.CTkButton(self, text="Edit Part", command=lambda: self.edit_part(part_name)).pack(pady=5)

        tk.CTkButton(self, text="Delete Part", fg_color="red", command=lambda: self.delete_part(part_name)).pack(pady=10)
        tk.CTkButton(self, text="Back", command=self.build_ui).pack(pady=10)

    def validate_int(self, P):
        return P.isdigit() or P == ""

    def validate_float(self, P):
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def parse_node_stack(self, entry):
        try:
            return [float(x.strip()) for x in entry.split(",")]
        except ValueError:
            return []

    def edit_part(self, part_name):
        with open(self.parts_data, "r") as f:
            data = json.load(f)
            part = data["parts"].get(part_name, {})

        type_map = {
            "Fuel Tank": "FT",
            "Engine": "ENG",
            "Flag": "FLAG"
        }

        self.editing_part_name = part_name
        self.create_part(type_map.get(part.get("type"), "FT"), part)

    def fill_common_part_fields(self, part_data):
        self.name.insert(0, self.editing_part_name or "")

        if hasattr(self, "description"):
            self.description.insert(0, part_data.get("description", ""))

        if hasattr(self, "model_label"):
            self.model_path = part_data.get("model", "")
            model_name = os.path.basename(self.model_path) if self.model_path else "Default"
            self.model_label.config(text=f"Selected Model: {model_name}")

        if hasattr(self, "texture_label"):
            self.texture_path = part_data.get("texture", "")
            texture_name = os.path.basename(self.texture_path) if self.texture_path else "Default"
            self.texture_label.config(text=f"Selected Texture: {texture_name}")

    def fill_part_fields(self, part_data):
        self.fill_common_part_fields(part_data)

        if self.part_type == "FT":
            self.capacity.delete(0, tk.END)
            self.capacity.insert(0, str(part_data.get("capacity", "")))
            self.node_stack_top.delete(0, tk.END)
            self.node_stack_top.insert(0, ", ".join(map(str, part_data.get("node_stack_top", []))))
            self.node_stack_bottom.delete(0, tk.END)
            self.node_stack_bottom.insert(0, ", ".join(map(str, part_data.get("node_stack_bottom", []))))
            self.tech_required.delete(0, tk.END)
            self.tech_required.insert(0, part_data.get("tech_required", "basicRocketry"))
            self.fuel_type.delete(0, tk.END)
            self.fuel_type.insert(0, part_data.get("fuel_type", "LiquidFuel"))
            self.entry_cost.delete(0, tk.END)
            self.entry_cost.insert(0, str(part_data.get("entry_cost", 1000)))
            self.cost.delete(0, tk.END)
            self.cost.insert(0, str(part_data.get("cost", 150)))
            self.max_temp.delete(0, tk.END)
            self.max_temp.insert(0, str(part_data.get("max_temp", 2000)))
            self.useOxidizer.set(part_data.get("use_oxidizer", 1))

        elif self.part_type == "ENG":
            self.thrust.delete(0, tk.END)
            self.thrust.insert(0, str(part_data.get("thrust", "")))
            self.node_stack_top.delete(0, tk.END)
            self.node_stack_top.insert(0, ", ".join(map(str, part_data.get("node_stack_top", []))))
            self.node_stack_bottom.delete(0, tk.END)
            self.node_stack_bottom.insert(0, ", ".join(map(str, part_data.get("node_stack_bottom", []))))
            self.tech_required.delete(0, tk.END)
            self.tech_required.insert(0, part_data.get("tech_required", "basicRocketry"))
            self.fuel_type.delete(0, tk.END)
            self.fuel_type.insert(0, part_data.get("fuel_type", "LiquidFuel"))
            self.entry_cost.delete(0, tk.END)
            self.entry_cost.insert(0, str(part_data.get("entry_cost", 1000)))
            self.cost.delete(0, tk.END)
            self.cost.insert(0, str(part_data.get("cost", 150)))
            self.max_temp.delete(0, tk.END)
            self.max_temp.insert(0, str(part_data.get("max_temp", 2000)))
            self.useOxidizer.set(part_data.get("use_oxidizer", 1))

        elif self.part_type == "FLAG":
            self.fill_common_part_fields(part_data)
    
    def create_part(self, part_type, part_data=None):
        self.part_type = part_type
        self.clear_window()

        self.vcmd = (self.register(self.validate_int), "%P")
        self.float_vcmd = (self.register(self.validate_float), "%P")

        # ---------------- MAIN ----------------
        main = tk.CTkFrame(self)
        main.pack(fill='both', expand=True, padx=12, pady=12)

        # Proper grid setup
        main.rowconfigure(0, weight=1)
        main.rowconfigure(1, weight=0)
        main.columnconfigure(0, weight=1)

        # ---------------- NOTEBOOK ----------------
        notebook = tk.CTkTabview(main)
        notebook.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6, 0))

        # ---------------- FOOTER ----------------
        footer = tk.CTkFrame(main)
        footer.grid(row=1, column=0, sticky="ew", padx=6, pady=(8, 0))

        # ------------------ Fuel Tank ------------------
        if part_type == "FT":
            notebook.add("Basic")
            notebook.add("Model")
            notebook.add("Science")
            notebook.add("Advanced")

            basic_tab = notebook.tab("Basic")
            model_tab = notebook.tab("Model")
            science_tab = notebook.tab("Science")
            advanced_tab = notebook.tab("Advanced")

            # Basic
            tk.CTkLabel(basic_tab, text="Fuel Tank Name:").pack(anchor="w", padx=18, pady=(10, 2))
            self.name = tk.CTkEntry(basic_tab, width=420)
            self.name.pack(padx=18, pady=(0, 8), fill="x")

            tk.CTkLabel(basic_tab, text="Description:").pack(anchor="w", padx=18, pady=(0, 2))
            self.description = tk.CTkEntry(basic_tab, width=420)
            self.description.pack(padx=18, pady=(0, 8), fill="x")

            tk.CTkLabel(basic_tab, text="Fuel Capacity (units):").pack(anchor="w", padx=18, pady=(0, 2))
            self.capacity = tk.CTkEntry(basic_tab, width=180, validate='key', validatecommand=self.vcmd)
            self.capacity.pack(anchor="w", padx=18, pady=(0, 8))

            # Model
            tk.CTkButton(model_tab, text="Select Model", command=self.select_model).pack(anchor="w", padx=18, pady=(10, 6))
            self.model_label = tk.CTkLabel(model_tab, text="Selected Model: Default")
            self.model_label.pack(anchor="w", padx=18, pady=(0, 6))

            tk.CTkButton(model_tab, text="Select Texture", command=self.select_texture).pack(anchor="w", padx=18, pady=(0, 6))
            self.texture_label = tk.CTkLabel(model_tab, text="Selected Texture: Default")
            self.texture_label.pack(anchor="w", padx=18, pady=(0, 6))

            tk.CTkLabel(model_tab, text="Node Stack Top:").pack(anchor="w", padx=18, pady=(10, 2))
            self.node_stack_top = tk.CTkEntry(model_tab, width=420)
            self.node_stack_top.pack(padx=18, pady=(0, 8), fill="x")
            self.node_stack_top.insert(0, "0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1")
            ToolTip(self.node_stack_top, "Default: 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")

            tk.CTkLabel(model_tab, text="Node Stack Bottom:").pack(anchor="w", padx=18, pady=(0, 2))
            self.node_stack_bottom = tk.CTkEntry(model_tab, width=420)
            self.node_stack_bottom.pack(padx=18, pady=(0, 8), fill="x")
            self.node_stack_bottom.insert(0, "0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1")
            ToolTip(self.node_stack_bottom, "Default: 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")

            tk.CTkButton(model_tab, text="Help", command=lambda: webbrowser.open("https://wiki.kerbalspaceprogram.com/wiki/CFG_File_Documentation#Node_Definitions")).pack(anchor="w", padx=18, pady=(0, 10))

            # Science
            tk.CTkLabel(science_tab, text="Tech Required:").pack(anchor="w", padx=18, pady=(10, 2))
            self.tech_required = tk.CTkEntry(science_tab, width=420)
            self.tech_required.pack(padx=18, pady=(0, 8), fill="x")
            self.tech_required.insert(0, "basicRocketry")
            ToolTip(self.tech_required, "The technology required to unlock this part.\neg. basicRocketry, fuelSystems, propulsionSystems")

            tk.CTkButton(science_tab, text="Help", command=lambda: webbrowser.open("https://wiki.kerbalspaceprogram.com/index.php?title=CFG_File_Documentation#Editor_Parameters")).pack(anchor="w", padx=18, pady=(0, 10))
            tk.CTkLabel(science_tab, text="Entry Cost:").pack(anchor="w", padx=18, pady=(0, 2))
            self.entry_cost = tk.CTkEntry(science_tab, width=180, validate='key', validatecommand=self.vcmd)
            self.entry_cost.pack(anchor="w", padx=18, pady=(0, 8))
            self.entry_cost.insert(0, "1000")

            tk.CTkLabel(science_tab, text="Cost:").pack(anchor="w", padx=18, pady=(0, 2))
            self.cost = tk.CTkEntry(science_tab, width=180, validate='key', validatecommand=self.vcmd)
            self.cost.pack(anchor="w", padx=18, pady=(0, 8))
            self.cost.insert(0, "150")

            # Advanced
            tk.CTkLabel(advanced_tab, text="Fuel Type:").pack(anchor="w", padx=18, pady=(10, 2))
            self.fuel_type = tk.CTkEntry(advanced_tab, width=280)
            self.fuel_type.pack(anchor="w", padx=18, pady=(0, 8))
            self.fuel_type.insert(0, "LiquidFuel")
            self.useOxidizer = tk.IntVar(value=1)
            oxidizerCheck = tk.CTkCheckBox(advanced_tab, text="Use Oxidizer", variable=self.useOxidizer)
            oxidizerCheck.pack(anchor="w", padx=18, pady=(0, 8))
            ToolTip(self.fuel_type, "The fuel the tank holds.\n(LiquidFuel, Oxidizer, SolidFuel, MonoPropellant, XenonGas, ElectricCharge)")
            ToolTip(oxidizerCheck, "Check if the tank is a LiquidFuel/Oxidizer.")

            tk.CTkLabel(advanced_tab, text="Max Temp:").pack(anchor="w", padx=18, pady=(0, 2))
            self.max_temp = tk.CTkEntry(advanced_tab, width=180, validate='key', validatecommand=self.vcmd)
            self.max_temp.pack(anchor="w", padx=18, pady=(0, 10))
            self.max_temp.insert(0, "2000")

            tk.CTkButton(footer, text="Save Fuel Tank", command=self.save_part).pack(side="left", padx=5, pady=6)

        # ------------------ Engine ------------------
        elif part_type == "ENG":
            notebook.add("Basic")
            notebook.add("Model")
            notebook.add("Science")
            notebook.add("Advanced")

            basic_tab = notebook.tab("Basic")
            model_tab = notebook.tab("Model")
            science_tab = notebook.tab("Science")
            advanced_tab = notebook.tab("Advanced")

            # Basic
            tk.CTkLabel(basic_tab, text="Engine Name:").pack(anchor="w", padx=18, pady=(10, 2))
            self.name = tk.CTkEntry(basic_tab, width=420)
            self.name.pack(padx=18, pady=(0, 8), fill="x")

            tk.CTkLabel(basic_tab, text="Description:").pack(anchor="w", padx=18, pady=(0, 2))
            self.description = tk.CTkEntry(basic_tab, width=420)
            self.description.pack(padx=18, pady=(0, 8), fill="x")

            tk.CTkLabel(basic_tab, text="Thrust (kN):").pack(anchor="w", padx=18, pady=(0, 2))
            self.thrust = tk.CTkEntry(basic_tab, width=180, validate='key', validatecommand=self.float_vcmd)
            self.thrust.pack(anchor="w", padx=18, pady=(0, 8))

            # Model
            tk.CTkButton(model_tab, text="Select Model", command=self.select_model).pack(anchor="w", padx=18, pady=(10, 6))
            self.model_label = tk.CTkLabel(model_tab, text="Selected Model: Default")
            self.model_label.pack(anchor="w", padx=18, pady=(0, 6))

            tk.CTkButton(model_tab, text="Select Texture", command=self.select_texture).pack(anchor="w", padx=18, pady=(0, 6))
            self.texture_label = tk.CTkLabel(model_tab, text="Selected Texture: Default")
            self.texture_label.pack(anchor="w", padx=18, pady=(0, 6))

            tk.CTkLabel(model_tab, text="Node Stack Top:").pack(anchor="w", padx=18, pady=(10, 2))
            self.node_stack_top = tk.CTkEntry(model_tab, width=420)
            self.node_stack_top.pack(padx=18, pady=(0, 8), fill="x")
            self.node_stack_top.insert(0, "0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1")
            ToolTip(self.node_stack_top, "Default: 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")
            tk.CTkLabel(model_tab, text="Node Stack Bottom:").pack(anchor="w", padx=18, pady=(0, 2))
            self.node_stack_bottom = tk.CTkEntry(model_tab, width=420)
            self.node_stack_bottom.pack(padx=18, pady=(0, 8), fill="x")
            self.node_stack_bottom.insert(0, "0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1")
            ToolTip(self.node_stack_bottom, "Default: 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")

            tk.CTkButton(model_tab, text="Help", command=lambda: webbrowser.open("https://wiki.kerbalspaceprogram.com/wiki/CFG_File_Documentation#Node_Definitions")).pack(anchor="w", padx=18, pady=(0, 10))

            # Science
            tk.CTkLabel(science_tab, text="Tech Required:").pack(anchor="w", padx=18, pady=(10, 2))
            self.tech_required = tk.CTkEntry(science_tab, width=420)
            self.tech_required.pack(padx=18, pady=(0, 8), fill="x")
            self.tech_required.insert(0, "basicRocketry")
            ToolTip(self.tech_required, "The technology required to unlock this part.\neg. basicRocketry, fuelSystems, propulsionSystems")

            tk.CTkButton(science_tab, text="Help", command=lambda: webbrowser.open("https://wiki.kerbalspaceprogram.com/index.php?title=CFG_File_Documentation#Editor_Parameters")).pack(anchor="w", padx=18, pady=(0, 10))
            tk.CTkLabel(science_tab, text="Entry Cost:").pack(anchor="w", padx=18, pady=(0, 2))
            self.entry_cost = tk.CTkEntry(science_tab, width=180, validate='key', validatecommand=self.vcmd)
            self.entry_cost.pack(anchor="w", padx=18, pady=(0, 8))
            self.entry_cost.insert(0, "1000")

            tk.CTkLabel(science_tab, text="Cost:").pack(anchor="w", padx=18, pady=(0, 2))
            self.cost = tk.CTkEntry(science_tab, width=180, validate='key', validatecommand=self.vcmd)
            self.cost.pack(anchor="w", padx=18, pady=(0, 8))
            self.cost.insert(0, "150")

            # Advanced
            tk.CTkLabel(advanced_tab, text="Fuel Type:").pack(anchor="w", padx=18, pady=(10, 2))
            self.fuel_type = tk.CTkEntry(advanced_tab, width=280)
            self.fuel_type.pack(anchor="w", padx=18, pady=(0, 8))
            self.fuel_type.insert(0, "LiquidFuel")

            self.useOxidizer = tk.IntVar(value=1)
            oxidizerCheck = tk.CTkCheckBox(advanced_tab, text="Use Oxidizer", variable=self.useOxidizer)
            oxidizerCheck.pack(anchor="w", padx=18, pady=(0, 8))
            ToolTip(self.fuel_type, "The fuel the engine uses.\n(LiquidFuel, Oxidizer, SolidFuel, MonoPropellant, XenonGas, ElectricCharge)")
            ToolTip(oxidizerCheck, "Check if the engine is a Liquid Fuel/Oxidizer.")

            tk.CTkLabel(advanced_tab, text="Max Temp:").pack(anchor="w", padx=18, pady=(0, 2))
            self.max_temp = tk.CTkEntry(advanced_tab, width=180, validate='key', validatecommand=self.vcmd)
            self.max_temp.pack(anchor="w", padx=18, pady=(0, 10))
            self.max_temp.insert(0, "2000")

            tk.CTkButton(footer, text="Save Engine", command=self.save_part).pack(side="left", padx=5, pady=6)

        # ------------------ Flag ------------------
        elif part_type == "FLAG":
            notebook.add("Basic")
            basic_tab = notebook.tab("Basic")

            tk.CTkLabel(basic_tab, text="Flag Name:").pack(anchor="w", padx=18, pady=(10, 2))
            self.name = tk.CTkEntry(basic_tab, width=420)
            self.name.pack(padx=18, pady=(0, 8), fill="x")

            tk.CTkButton(basic_tab, text="Select Texture", command=self.select_texture).pack(anchor="w", padx=18, pady=(10, 6))
            self.texture_label = tk.CTkLabel(basic_tab, text="Selected Texture: Default")
            self.texture_label.pack(anchor="w", padx=18, pady=(0, 10))

            tk.CTkButton(footer, text="Save Flag", command=self.save_part).pack(side="left", padx=5, pady=6)

        tk.CTkButton(footer, text="Cancel", command=self.build_ui).pack(side="left", padx=5, pady=6)

        if part_data:
            self.fill_part_fields(part_data)

    def save_part(self):
        with open(self.parts_data, "r+") as f:
            data = json.load(f)

            # Valid fuels list
            valid_fuels = [
                "LiquidFuel",
                "Oxidizer",
                "SolidFuel",
                "MonoPropellant",
                "XenonGas",
                "ElectricCharge"
            ]

            # Ensure "parts" exists
            if "parts" not in data:
                data["parts"] = {}

            original_part_name = self.editing_part_name

            # ------------------ FLAG ------------------
            if self.part_type == "FLAG":
                part_name = self.name.get().strip()

                # Validate name
                if not part_name:
                    messagebox.showerror("Missing Fields", "Please fill in the following fields:\nName")
                    return
                if part_name in data["parts"] and part_name != original_part_name:
                    messagebox.showerror("Error", "Part name already exists.")
                    return

                # Validate texture
                texture_path = getattr(self, "texture_path", None) or os.path.join(DEFAULTS_DIR, "flag.png")
                if not check_flag_size(texture_path):
                    messagebox.showerror("Invalid Texture", "Flag texture must be 256x160 pixels.")
                    return

                # Save flag
                if original_part_name and original_part_name != part_name:
                    data["parts"].pop(original_part_name, None)

                data["parts"][part_name] = {
                    "type": "Flag",
                    "texture": texture_path
                }

            # ------------------ FUEL TANK ------------------
            elif self.part_type == "FT":
                missing_fields = []

                # Validate node stacks
                node_top = self.parse_node_stack(self.node_stack_top.get())
                node_bottom = self.parse_node_stack(self.node_stack_bottom.get())
                if not node_top or not node_bottom or len(node_top) != 7 or len(node_bottom) != 7:
                    messagebox.showerror("Invalid Node Stack", "Node stack entries must be 7 comma-separated numbers.")
                    return

                # Validate required fields
                part_name = self.name.get().strip()
                if not part_name:
                    missing_fields.append("Name")
                elif part_name in data["parts"] and part_name != original_part_name:
                    messagebox.showerror("Error", "Part name already exists.")
                    return

                description = self.description.get().strip()
                if not description:
                    missing_fields.append("Description")

                capacity = self.capacity.get().strip()
                if not capacity:
                    missing_fields.append("Capacity")

                tech_required = self.tech_required.get().strip()
                if not tech_required:
                    missing_fields.append("Tech Required")

                fuel_type = self.fuel_type.get().strip()
                if not fuel_type:
                    missing_fields.append("Fuel Type")
                elif fuel_type not in valid_fuels:
                    messagebox.showerror("Invalid Fuel Type", f"'{fuel_type}' is not a valid KSP fuel type.")
                    return

                entry_cost = self.entry_cost.get().strip()
                if not entry_cost:
                    missing_fields.append("Entry Cost")

                cost = self.cost.get().strip()
                if not cost:
                    missing_fields.append("Cost")

                max_temp = self.max_temp.get().strip()
                if not max_temp:
                    missing_fields.append("Max Temp")

                # Report missing fields
                if missing_fields:
                    messagebox.showerror("Missing Fields", "Please fill in the following fields:\n" + "\n".join(missing_fields))
                    return

                # Save fuel tank
                if original_part_name and original_part_name != part_name:
                    data["parts"].pop(original_part_name, None)

                data["parts"][part_name] = {
                    "type": "Fuel Tank",
                    "description": description,
                    "model": getattr(self, "model_path", os.path.join(DEFAULTS_DIR, "tank.mu")),
                    "texture": getattr(self, "texture_path", os.path.join(DEFAULTS_DIR, "tank.png")),
                    "capacity": capacity,
                    "fuel_type": fuel_type,
                    "tech_required": tech_required,
                    "entry_cost": int(entry_cost),
                    "cost": int(cost),
                    "max_temp": int(max_temp),
                    "node_stack_top": node_top,
                    "node_stack_bottom": node_bottom,
                    "use_oxidizer": self.useOxidizer.get()
                }

            # ------------------ ENGINE ------------------
            elif self.part_type == "ENG":
                missing_fields = []

                node_bottom = self.parse_node_stack(self.node_stack_bottom.get())
                node_top = self.parse_node_stack(self.node_stack_top.get())
                if (not node_bottom or len(node_bottom) != 7) or (not node_top or len(node_top) != 7):
                    messagebox.showerror("Invalid Node Stack", "Node stack entries must be 7 comma-separated numbers.")
                    return

                # Validate required fields
                part_name = self.name.get().strip()
                if not part_name:
                    missing_fields.append("Name")
                elif part_name in data["parts"] and part_name != original_part_name:
                    messagebox.showerror("Error", "Part name already exists.")
                    return

                description = self.description.get().strip()
                if not description:
                    missing_fields.append("Description")

                thrust = self.thrust.get().strip()
                if not thrust:
                    missing_fields.append("Thrust")
                else:
                    try:
                        thrust_val = float(thrust)
                    except ValueError:
                        messagebox.showerror("Invalid Thrust", "Thrust must be a numeric value.")
                        return

                fuel_type = self.fuel_type.get().strip()
                if not fuel_type:
                    missing_fields.append("Fuel Type")
                elif fuel_type not in valid_fuels:
                    messagebox.showerror("Invalid Fuel Type", f"'{fuel_type}' is not a valid KSP fuel type.")
                    return

                tech_required = self.tech_required.get().strip()
                if not tech_required:
                    missing_fields.append("Tech Required")

                entry_cost = self.entry_cost.get().strip()
                if not entry_cost:
                    missing_fields.append("Entry Cost")

                cost = self.cost.get().strip()
                if not cost:
                    missing_fields.append("Cost")

                max_temp = self.max_temp.get().strip()
                if not max_temp:
                    missing_fields.append("Max Temp")

                # Report missing fields
                if missing_fields:
                    messagebox.showerror("Missing Fields", "Please fill in the following fields:\n" + "\n".join(missing_fields))
                    return

                # Save engine
                if original_part_name and original_part_name != part_name:
                    data["parts"].pop(original_part_name, None)

                data["parts"][part_name] = {
                    "type": "Engine",
                    "description": description,
                    "model": getattr(self, "model_path", os.path.join(DEFAULTS_DIR, "eng.mu")),
                    "texture": getattr(self, "texture_path", os.path.join(DEFAULTS_DIR, "eng.png")),
                    "thrust": thrust_val,
                    "fuel_type": fuel_type,
                    "tech_required": tech_required,
                    "entry_cost": int(entry_cost),
                    "cost": int(cost),
                    "max_temp": int(max_temp),
                    "node_stack_bottom": node_bottom,
                    "node_stack_top": node_top,
                    "use_oxidizer": self.useOxidizer.get()
                }

            # ------------------ SAVE TO FILE ------------------
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        self.editing_part_name = None
        # Refresh UI
        self.build_ui()

    def select_model(self):
        filepath = filedialog.askopenfilename(filetypes=[("MU 3D Models", "*.mu")])
        if filepath:
            self.model_path = filepath
            self.model_label.config(text=f"Selected Model: {os.path.basename(filepath)}")

    def select_texture(self):
        filepath = filedialog.askopenfilename(filetypes=[("Custom Textures", "*.png *.dds")])
        if filepath:
            self.texture_path = filepath
            self.texture_label.config(text=f"Selected Texture: {os.path.basename(filepath)}")

    def delete_all(self):
        msg_box = messagebox.askyesno("Delete All", "Are you sure you want to delete all parts?")
        if msg_box:
            if os.path.exists(f"{self.parts_data}"):
                os.remove(f"{self.parts_data}")
            with open(f"{self.parts_data}", "w") as f:
                json.dump({}, f, indent=4)
            self.build_ui()

    def delete_part(self, part_name):
        with open(self.parts_data, "r+") as f:
            data = json.load(f)
            # Check inside the "parts" dictionary
            if "parts" in data and part_name in data["parts"]:
                del data["parts"][part_name]
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
        self.build_ui()

    def run_packager(self):
        mod_dir = os.path.join(self.workspace_dir, "packaged")

        mod_ver = simpledialog.askstring(
            "Mod Version",
            "Enter the mod version (e.g. 1.2.8):",
            initialvalue=self.mod_version
        )

        # User pressed cancel
        if mod_ver is None:
            return

        # Empty version
        mod_ver = mod_ver.strip()
        if not mod_ver:
            messagebox.showerror("Error", "Version cannot be empty.")
            return

        try:
            if os.path.getsize(self.parts_data) <= 2:
                messagebox.showerror("Error", "No parts to package.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read parts.json: {e}")
            return

        # Update version
        self.mod_version = mod_ver

        mod_name = self.mod_name
        base_dir = os.path.join(mod_dir, f"{mod_name}_{self.mod_version}")
        os.makedirs(base_dir, exist_ok=True)

        parts_result = ""
        flags_result = ""
        parts_data = self.parts_data

        try:
            parts_result = pkg_parts(
                json_path=parts_data,
                output_dir=os.path.join(base_dir, "parts"),
                mod_version=self.mod_version,
                mod_author=self.mod_author
            )
        except Exception as e:
            if isinstance(e, ValueError):
                parts_result = "No parts to package."
            else:
                parts_result = f"Parts packaging failed: {str(e)}"

        try:
            flags_result = pkg_flags(
                json_path=parts_data,
                output_dir=os.path.join(base_dir, "flags")
            )
        except Exception as e:
            if isinstance(e, ValueError):
                flags_result = "No flags to package."
            else:
                flags_result = f"Flags packaging failed: {str(e)}"

        messagebox.showinfo(
            "Packager",
            f"{parts_result}\n{flags_result}\nMod version now {self.mod_version}"
        )


def start_app(parts_data, mod_name, workspace_dir, mod_version, mod_author):
    app = KCreator(parts_data=parts_data, mod_name=mod_name, workspace_dir=workspace_dir, mod_ver=mod_version, mod_author=mod_author)
    print(f"KCreator v{app.version} Copyright © 2025 TheOR30")
    app.mainloop()

if __name__ == "__main__":
    menu.start_menu()

