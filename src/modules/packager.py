import json
import os
import shutil
import src.modules.imageTools as img

# Map part types to KSP categories
CATEGORY_MAP = {
    "Fuel Tank": "FuelTank",
    "Engine": "Propulsion",
    "Flag": "Utility"
}

def update_mod_version(json_path="mod_info.json"):
    """Update mod version by +0.1 once per run."""
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
    else:
        data = {"mod_version": 0.1}

    current_version = float(data.get("mod_version", 0.1))
    new_version = round(current_version + 0.1, 1)

    data["mod_version"] = new_version
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Updated mod version: {new_version}")
    return new_version

def pkg_parts(json_path="parts.json", output_dir="PackagedParts/parts", mod_version=None, mod_author="KSPModCreator"):
    if not os.path.exists(json_path):
        raise FileNotFoundError("No parts.json found!")

    with open(json_path, "r") as f:
        data = json.load(f)

    parts = data.get("parts", {})
    if not parts:
        raise ValueError("No parts to package!")

    non_flag_parts = {name: pdata for name, pdata in parts.items() if pdata.get("type") != "Flag"}
    if not non_flag_parts:
        raise ValueError("No non-flag parts to package!")

    os.makedirs(output_dir, exist_ok=True)

    for name, pdata in non_flag_parts.items():
        part_dir = os.path.join(output_dir, name.replace(" ", "_"))
        os.makedirs(part_dir, exist_ok=True)

        model_path = pdata.get("model")
        texture_path = pdata.get("texture")

        model_filename = os.path.basename(model_path) if model_path and os.path.exists(model_path) else "default.mu"
        texture_filename = os.path.basename(texture_path) if texture_path and os.path.exists(texture_path) else "default.png"

        if model_path and os.path.exists(model_path):
            shutil.copy(model_path, part_dir)

        if texture_path and os.path.exists(texture_path) and texture_filename.endswith('.png'):
            dds_filename = texture_filename.replace('.png', '.dds')
            if not img.png_to_dds(texture_path, os.path.join(part_dir, dds_filename)):
                shutil.copy(texture_path, part_dir)
                dds_filename = texture_filename
        else:
            if texture_path and os.path.exists(texture_path):
                shutil.copy(texture_path, part_dir)
            dds_filename = texture_filename

        cfg_lines = [
            "PART",
            "{",
            f"  name = {name.replace(' ', '_')}",
            "  module = Part",
            f"  author = {mod_author}",
            f"  version = {mod_version}",  # embed version here
            "",
            "  MODEL",
            "  {",
            f"    model = {model_filename}",
            f"    texture = {dds_filename}",
            "  }",
            "",
            "  rescaleFactor = 1.0",
            f"  node_stack_top = {', '.join(map(str, pdata.get('node_stack_top', [0.0, 0.1, 0.0, 0.0, 1.0, 0.0, 1])))}",
        ]

        if pdata["type"] in ("Fuel Tank", "Engine"):
            cfg_lines.append(
                f"  node_stack_bottom = {', '.join(map(str, pdata.get('node_stack_bottom', [0.0, -0.1, 0.0, 0.0, -1.0, 0.0, 1])))}"
            )

        cfg_lines += [
            f"  TechRequired = {pdata.get('tech_required', 'basicRocketry')}",
            f"  entryCost = {pdata.get('entry_cost', 1000)}",
            f"  cost = {pdata.get('cost', 150)}",
            f"  category = {CATEGORY_MAP.get(pdata['type'], 'Utility')}",
            "  subcategory = 0",
            f"  title = {name}",
            "  manufacturer = KSPModCreator Inc.",
            f"  description = {pdata.get('description', 'A custom part.')}",
            "  attachRules = 1,1,1,1,0",
            "  mass = 0.05",
            "  dragModelType = default",
            "  maximum_drag = 0.2",
            "  minimum_drag = 0.2",
            "  angularDrag = 2",
            "  crashTolerance = 6",
            f"  maxTemp = {pdata.get('max_temp', 2000)}",
            "  bulkheadProfiles = size1, srf",
            ""
        ]

        if pdata["type"] == "Fuel Tank":
            capacity = int(pdata.get('capacity', 0))
            fuel_type = pdata.get('fuel_type', 'LiquidFuel')

            cfg_lines += [
                "  RESOURCE",
                "  {",
                f"    name = {fuel_type}",
                f"    amount = {capacity}",
                f"    maxAmount = {capacity}",
                "  }"
            ]

            if pdata.get("use_oxidizer", False):
                oxidizer_amount = int(capacity * (11/9))
                cfg_lines += [
                    "  RESOURCE",
                    "  {",
                    "    name = Oxidizer",
                    f"    amount = {oxidizer_amount}",
                    f"    maxAmount = {oxidizer_amount}",
                    "  }"
                ]

        elif pdata["type"] == "Engine":
            thrust = pdata.get('thrust', 0)
            fuel_type = pdata.get('fuel_type', 'LiquidFuel')

            cfg_lines += [
                "  MODULE",
                "  {",
                "    name = ModuleEngines",
                "    thrustVectorTransformName = thrustTransform",
                f"    maxThrust = {thrust}",
                "    minThrust = 0",
                "    heatProduction = 150",
                "    useEngineResponseTime = True",
                "    engineAccelerationSpeed = 2.0",
                "    engineDecelerationSpeed = 2.0",
                "    exhaustDamage = True",
                "    ignitionThreshold = 0.1",
                "",
                "    PROPELLANT",
                "    {",
                f"      name = {fuel_type}",
                "      ratio = 0.9",
                "    }",
            ]

            if pdata.get("use_oxidizer", False):
                cfg_lines += [
                    "    PROPELLANT",
                    "    {",
                    "      name = Oxidizer",
                    "      ratio = 1.1",
                    "    }",
                ]

            cfg_lines += [
                "  }"
            ]

        cfg_lines.append("}")

        cfg_path = os.path.join(part_dir, f"{name.replace(' ', '_')}.cfg")
        with open(cfg_path, "w") as cfg_file:
            cfg_file.write("\n".join(cfg_lines))

    return f"Packaged {len(non_flag_parts)} parts with .cfg files in '{output_dir}'"

def pkg_flags(json_path="parts.json", output_dir="PackagedFlags/flags"):
    if not os.path.exists(json_path):
        raise FileNotFoundError("No parts.json found!")

    with open(json_path, "r") as f:
        data = json.load(f)

    parts = data.get("parts", {})
    flags = {name: pdata for name, pdata in parts.items() if pdata.get("type") == "Flag"}
    if not flags:
        raise ValueError("No flags to package!")

    os.makedirs(output_dir, exist_ok=True)

    for name, pdata in flags.items():
        texture_path = pdata.get("texture")
        dest_name_base = name.replace(" ", "_")
        copied = False

        if texture_path and os.path.exists(texture_path):
            _, ext = os.path.splitext(texture_path)
            if not ext:
                ext = ".png"
            dest_path = os.path.join(output_dir, dest_name_base + ext)
            shutil.copy(texture_path, dest_path)
            copied = True
        else:
            search_dirs = [os.path.dirname(json_path) or ".", "."]
            common_exts = [".png", ".jpg", ".jpeg", ".dds"]

            for d in search_dirs:
                for ext in common_exts:
                    candidate = os.path.join(d, dest_name_base + ext)
                    if os.path.exists(candidate):
                        dest_path = os.path.join(output_dir, dest_name_base + ext)
                        shutil.copy(candidate, dest_path)
                        copied = True
                        break
                if copied:
                    break

        if not copied:
            print(f"Warning: Texture not found for flag '{name}'")

    return f"Packaged {len(flags)} flags in '{output_dir}'"
