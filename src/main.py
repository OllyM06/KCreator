import os
import json
import webbrowser
import tkinter as tk
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tkinter import ttk, filedialog, messagebox, simpledialog
from src.modules.UITools import ToolTip
from src.modules.imageTools import check_flag_size
from src.modules.packager import pkg_parts, pkg_flags, update_mod_version as update_mod

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULTS_DIR = os.path.join(SRC_DIR, "defaults")

class KCreator(tk.Tk):
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
        self.iconbitmap(os.path.join(ROOT_DIR, "kcreator.ico"))
        self.part_type = None
        self.editing_part_name = None
        self.build_ui()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def build_ui(self):
        self.clear_window()
        frm = tk.Frame(self)
        frm.pack(fill="x", padx=10, pady=8)
        bold_font = ("Arial", 10, "bold")
        big_bold_font = ("Arial", 24, "bold")

        new = tk.Menubutton(frm, text=" + ", relief=tk.RAISED, font=big_bold_font)
        new.grid(row=0, column=0, padx=5, pady=5)
        new_menu = tk.Menu(new, tearoff=0)
        new_menu.add_command(label="Fuel Tank", command=lambda: self.create_part("FT"))
        new_menu.add_command(label="Engine", command=lambda: self.create_part("ENG"))
        new_menu.add_command(label="Flag", command=lambda: self.create_part("FLAG"))
        new["menu"] = new_menu

        with open(f"{self.parts_data}", "r") as f:
            data = json.load(f)

        tk.Label(frm, text="Created Parts:", font=bold_font).grid(row=1, column=0, padx=10)

        if not data["parts"]:
            tk.Label(frm, text="No Parts Created Yet").grid(row=2, column=0, sticky="w", padx=20, pady=5)
        else:
            for i, (part_name, part_info) in enumerate(data["parts"].items(), start=2):
                info = tk.Label(frm, text=f"{part_name}: {part_info.get('type', 'Unknown')}", fg="blue", cursor="hand2")
                info.grid(row=i, column=0, sticky="w", padx=20)
                info.bind("<Button-1>", lambda e, name=part_name: self.view_info(name))


        tk.Button(self, text="Delete All Parts", fg="red", command=self.delete_all).pack(side="bottom", pady=10)
        tk.Button(self, text="Package Parts", command=self.run_packager).pack(side="bottom", pady=5)

    def view_info(self, part_name):
        self.clear_window()
        with open(f"{self.parts_data}", "r") as f:
            data = json.load(f)
            part = data["parts"].get(part_name, {})

        tk.Label(self, text=f"Part Name: {part_name}", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(self, text=f"Type: {part.get('type', 'Unknown')}").pack(pady=5)


        if part['type'] == "Fuel Tank":
            tk.Label(self, text=f"Description: {part.get('description', 'N/A')}").pack(pady=5)
            tk.Label(self, text=f"Model: {part.get('model', part.get('texture', 'N/A'))}").pack(pady=5)
            tk.Label(self, text=f"Capacity: {part.get('capacity', 'N/A')} units").pack(pady=5)
            tk.Label(self, text=f"Entry Cost: {part.get('entry_cost', '1000')}").pack(pady=5)
            tk.Label(self, text=f"Cost: {part.get('cost', '150')}").pack(pady=5)
            tk.Label(self, text=f"Max Temp: {part.get('max_temp', '2000')}").pack(pady=5)
            tk.Label(self, text=f"Node Stack Top: {part.get('node_stack_top', 'N/A')}").pack(pady=5)
            tk.Label(self, text=f"Node Stack Bottom: {part.get('node_stack_bottom', 'N/A')}").pack(pady=5)
        elif part['type'] == "Engine":
            tk.Label(self, text=f"Description: {part.get('description', 'N/A')}").pack(pady=5)
            tk.Label(self, text=f"Model: {part.get('model', part.get('texture', 'N/A'))}").pack(pady=5)
            tk.Label(self, text=f"Thrust: {part.get('thrust', 'N/A')} kN").pack(pady=5)
            tk.Label(self, text=f"Fuel Type: {part.get('fuel_type', 'N/A')}").pack(pady=5)
            tk.Label(self, text=f"Entry Cost: {part.get('entry_cost', '1000')}").pack(pady=5)
            tk.Label(self, text=f"Cost: {part.get('cost', '150')}").pack(pady=5)
            tk.Label(self, text=f"Max Temp: {part.get('max_temp', '2000')}").pack(pady=5)
        elif part['type'] == "Flag":
            tk.Label(self, text=f"Texture: {part.get('texture', 'N/A')}").pack(pady=5)

        if part['type'] != "Flag":
            tk.Button(self, text="Edit Part", command=lambda: self.edit_part(part_name)).pack(pady=5)
        tk.Button(self, text="Delete Part", fg="red", command=lambda: self.delete_part(part_name)).pack(pady=10)
        tk.Button(self, text="Back", command=self.build_ui).pack(pady=10)

    def validate_int(self, P):
        return P.isdigit() or P == ""

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
        self.clear_window()
        self.part_type = part_type
        self.vcmd = (self.register(self.validate_int), '%P')

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=0, pady=0)

        # ------------------ Fuel Tank ------------------
        if part_type == "FT":
            basic_tab = ttk.Frame(notebook)
            model_tab = ttk.Frame(notebook)
            advanced_tab = ttk.Frame(notebook)

            notebook.add(basic_tab, text='Basic')
            notebook.add(model_tab, text='Model')
            notebook.add(advanced_tab, text='Advanced')

            # Basic
            tk.Label(basic_tab, text="Fuel Tank Name:").pack(pady=5)
            self.name = tk.Entry(basic_tab, width=40)
            self.name.pack(pady=5)

            tk.Label(basic_tab, text="Description:").pack(pady=5)
            self.description = tk.Entry(basic_tab, width=40)
            self.description.pack(pady=5)

            tk.Label(basic_tab, text="Fuel Capacity (units):").pack(pady=5)
            self.capacity = tk.Entry(basic_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.capacity.pack(pady=5)

            # Model
            tk.Button(model_tab, text="Select Model", command=self.select_model).pack(pady=5)
            self.model_label = tk.Label(model_tab, text="Selected Model: Default")
            self.model_label.pack(pady=5)

            tk.Button(model_tab, text="Select Texture", command=self.select_texture).pack(pady=5)
            self.texture_label = tk.Label(model_tab, text="Selected Texture: Default")
            self.texture_label.pack(pady=5)

            tk.Label(model_tab, text="Node Stack Top:").pack(pady=5)
            self.node_stack_top = tk.Entry(model_tab, width=40)
            self.node_stack_top.pack(pady=5)
            self.node_stack_top.insert(0, "0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1")
            ToolTip(self.node_stack_top, "Default: 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")

            tk.Label(model_tab, text="Node Stack Bottom:").pack(pady=5)
            self.node_stack_bottom = tk.Entry(model_tab, width=40)
            self.node_stack_bottom.pack(pady=5)
            self.node_stack_bottom.insert(0, "0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1")
            ToolTip(self.node_stack_bottom, "Default: 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")

            tk.Button(model_tab, text="Help", command=lambda: webbrowser.open("https://wiki.kerbalspaceprogram.com/wiki/CFG_File_Documentation#Node_Definitions")).pack(pady=5)

            # Advanced
            tk.Label(advanced_tab, text="Tech Required:").pack(pady=20)
            self.tech_required = tk.Entry(advanced_tab, width=40)
            self.tech_required.pack(pady=5)
            self.tech_required.insert(0, "basicRocketry")
            ToolTip(self.tech_required, "The technology required to unlock this part.\neg. basicRocketry, fuelSystems, propulsionSystems")
            tk.Button(advanced_tab, text="Help", command=lambda: webbrowser.open("https://wiki.kerbalspaceprogram.com/index.php?title=CFG_File_Documentation#Editor_Parameters")).pack(pady=5)

            tk.Label(advanced_tab, text="Fuel Type:").pack(pady=5)
            self.fuel_type = tk.Entry(advanced_tab, width=30)
            self.fuel_type.pack(pady=5)
            self.fuel_type.insert(0, "LiquidFuel")
            self.useOxidizer = tk.IntVar(value=1)
            oxidizerCheck = tk.Checkbutton(advanced_tab, text="Use Oxidizer", variable=self.useOxidizer)
            oxidizerCheck.pack()
            ToolTip(self.fuel_type, "The fuel the tank holds.\n(LiquidFuel, Oxidizer, SolidFuel, MonoPropellant, XenonGas, ElectricCharge)")
            ToolTip(oxidizerCheck, "Check if the tank is a LiquidFuel/Oxidizer.")

            tk.Label(advanced_tab, text="Entry Cost:").pack(pady=5)
            self.entry_cost = tk.Entry(advanced_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.entry_cost.pack(pady=5)
            self.entry_cost.insert(0, "1000")

            tk.Label(advanced_tab, text="Cost:").pack(pady=5)
            self.cost = tk.Entry(advanced_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.cost.pack(pady=5)
            self.cost.insert(0, "150")

            tk.Label(advanced_tab, text="Max Temp:").pack(pady=5)
            self.max_temp = tk.Entry(advanced_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.max_temp.pack(pady=5)
            self.max_temp.insert(0, "2000")

            tk.Button(self, text="Save Fuel Tank", command=self.save_part).pack(pady=5)

        # ------------------ Engine ------------------
        elif part_type == "ENG":
            basic_tab = ttk.Frame(notebook)
            model_tab = ttk.Frame(notebook)
            advanced_tab = ttk.Frame(notebook)

            notebook.add(basic_tab, text='Basic')
            notebook.add(model_tab, text='Model')
            notebook.add(advanced_tab, text='Advanced')

            # Basic
            tk.Label(basic_tab, text="Engine Name:").pack(pady=5)
            self.name = tk.Entry(basic_tab, width=40)
            self.name.pack(pady=5)

            tk.Label(basic_tab, text="Description:").pack(pady=5)
            self.description = tk.Entry(basic_tab, width=40)
            self.description.pack(pady=5)

            tk.Label(basic_tab, text="Thrust (kN):").pack(pady=5)
            self.thrust = tk.Entry(basic_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.thrust.pack(pady=5)

            # Model
            tk.Button(model_tab, text="Select Model", command=self.select_model).pack(pady=5)
            self.model_label = tk.Label(model_tab, text="Selected Model: Default")
            self.model_label.pack(pady=5)

            tk.Button(model_tab, text="Select Texture", command=self.select_texture).pack(pady=5)
            self.texture_label = tk.Label(model_tab, text="Selected Texture: Default")
            self.texture_label.pack(pady=5)

            tk.Label(model_tab, text="Node Stack Top:").pack(pady=5)
            self.node_stack_top = tk.Entry(model_tab, width=40)
            self.node_stack_top.pack(pady=5)
            self.node_stack_top.insert(0, "0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1")
            ToolTip(self.node_stack_top, "Default: 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")
            tk.Label(model_tab, text="Node Stack Bottom:").pack(pady=5)
            self.node_stack_bottom = tk.Entry(model_tab, width=40)
            self.node_stack_bottom.pack(pady=5)
            self.node_stack_bottom.insert(0, "0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1")
            ToolTip(self.node_stack_bottom, "Default: 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1\nFormat: X, Y, Z, Xdir, Ydir, Zdir, size")

            tk.Button(model_tab, text="Help", command=lambda: webbrowser.open("https://wiki.kerbalspaceprogram.com/wiki/CFG_File_Documentation#Node_Definitions")).pack(pady=5)

            # Advanced
            tk.Label(advanced_tab, text="Tech Required:").pack(pady=20)
            self.tech_required = tk.Entry(advanced_tab, width=40)
            self.tech_required.pack(pady=5)
            self.tech_required.insert(0, "basicRocketry")
            ToolTip(self.tech_required, "The technology required to unlock this part.\neg. basicRocketry, fuelSystems, propulsionSystems")

            tk.Label(advanced_tab, text="Fuel Type:").pack(pady=5)
            self.fuel_type = tk.Entry(advanced_tab, width=30)
            self.fuel_type.pack(pady=5)
            self.fuel_type.insert(0, "LiquidFuel")
            self.useOxidizer = tk.IntVar(value=1)
            oxidizerCheck = tk.Checkbutton(advanced_tab, text="Use Oxidizer", variable=self.useOxidizer)
            oxidizerCheck.pack()
            ToolTip(self.fuel_type, "The fuel the engine uses.\n(LiquidFuel, Oxidizer, SolidFuel, MonoPropellant, XenonGas, ElectricCharge)")
            ToolTip(oxidizerCheck, "Check if the engine is a Liquid Fuel/Oxidizer.")

            tk.Label(advanced_tab, text="Entry Cost:").pack(pady=5)
            self.entry_cost = tk.Entry(advanced_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.entry_cost.pack(pady=5)
            self.entry_cost.insert(0, "1000")

            tk.Label(advanced_tab, text="Cost:").pack(pady=5)
            self.cost = tk.Entry(advanced_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.cost.pack(pady=5)
            self.cost.insert(0, "150")

            tk.Label(advanced_tab, text="Max Temp:").pack(pady=5)
            self.max_temp = tk.Entry(advanced_tab, width=20, validate='key', validatecommand=self.vcmd)
            self.max_temp.pack(pady=5)
            self.max_temp.insert(0, "2000")


            tk.Button(self, text="Save Engine", command=self.save_part).pack(pady=5)

        # ------------------ Flag ------------------
        elif part_type == "FLAG":
            basic_tab = ttk.Frame(notebook)
            notebook.add(basic_tab, text='Basic')

            tk.Label(basic_tab, text="Flag Name:").pack(pady=5)
            self.name = tk.Entry(basic_tab, width=40)
            self.name.pack(pady=5)

            tk.Button(basic_tab, text="Select Texture", command=self.select_texture).pack(pady=5)
            self.texture_label = tk.Label(basic_tab, text="Selected Texture: Default")
            self.texture_label.pack(pady=5)

            tk.Button(self, text="Save Flag", command=self.save_part).pack(pady=5)

        tk.Button(self, text="Cancel", command=self.build_ui).pack(pady=5)

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
        try:
            if os.path.getsize(self.parts_data) <= 2:
                messagebox.showerror("Error", "No parts to package.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read parts.json: {e}")
            return

        # bump version once per run
        try:
            self.mod_version = update_mod(self.parts_data)
        except Exception as e:
            messagebox.showerror("Error", f"Version update failed: {e}")
            return

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
    import src.menu as menu
    menu.start_menu()

