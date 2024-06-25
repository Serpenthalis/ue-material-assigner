import unreal
import logging
import re

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# Config
directory_path = "/Game/EE_UE/Models"


def main():

    # Load static/skeletal mesh, check for matching material and assign if necessary
    skeletal_meshes, static_meshes = get_meshes(directory_path)
    pattern = re.compile("^.*_[0-9]{3}$")
    for mesh in skeletal_meshes:
        skeletal_mesh = unreal.EditorAssetLibrary.load_asset(mesh.package_name)
        if len(skeletal_mesh.materials) > 1:
            matched_material = get_matched_material(skeletal_mesh, True)
            if matched_material:
                assign_material(skeletal_mesh, matched_material, pattern, True)
    for mesh in static_meshes:
        static_mesh = unreal.EditorAssetLibrary.load_asset(mesh.package_name)
        if len(static_mesh.static_materials) > 1:
            matched_material = get_matched_material(static_mesh, False)
            if matched_material:
                assign_material(static_mesh, matched_material, pattern, False)


# Get all static/skeletal meshes from given directory
def get_meshes(path):
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = asset_registry.get_assets_by_path(path, recursive=True)
    skeletal_meshes = [asset for asset in assets if asset.asset_class_path.asset_name == 'SkeletalMesh']
    static_meshes = [asset for asset in assets if asset.asset_class_path.asset_name == 'StaticMesh']
    return skeletal_meshes, static_meshes


# Return any material that is not the default one
def get_matched_material(mesh, skeletal=True):
    materials = []
    if skeletal:
        materials = mesh.materials
    else:
        materials = mesh.static_materials
    for material in materials:
        material_name = material.material_interface.get_name()
        if material_name != "WorldGridMaterial":
            return material
    return None


# Assign material if material slot name is "player_color" or ends with "_XXX" where X is a number
def assign_material(mesh, matched_material, pattern, skeletal=True):
    if skeletal:
        for idx, material in enumerate(mesh.materials):
            if pattern.match(str(material.material_slot_name))\
            or material.material_slot_name == "player_color":
                mats_copy = mesh.materials.copy()
                matched_material_copy = matched_material.copy()
                matched_material_copy.material_slot_name = material.material_slot_name
                mats_copy[idx] = matched_material_copy
                mesh.modify() # Mark asset as changed
                mesh.materials = mats_copy # Change asset
    else:
        for idx, material in enumerate(mesh.static_materials):
            if pattern.match(str(material.material_slot_name))\
            or material.material_slot_name == "player_color":
                mats_copy = mesh.static_materials.copy()
                matched_material_copy = matched_material.copy()
                matched_material_copy.material_slot_name = material.material_slot_name
                mats_copy[idx] = matched_material_copy
                mesh.modify() # Mark asset as changed
                mesh.static_materials = mats_copy # Change asset


if __name__ == '__main__':
    main()
