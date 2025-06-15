import trimesh
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reorient_mesh_for_printing(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mesh.rezero()
    orientation = mesh.bounding_box_oriented.primitive.transform
    mesh.apply_transform(orientation)
    logging.info("Malla reorientada para la mejor posición de impresión.")
    return mesh

def check_mesh_health(mesh: trimesh.Trimesh) -> None:
    if not mesh.is_watertight:
        raise ValueError("La malla no es watertight.")
    logging.info("La malla es watertight y saludable.")

def repair_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mesh.fill_holes()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_infinite_values()
    mesh.remove_unreferenced_vertices()
    if not mesh.is_watertight:
        raise ValueError("La malla no se pudo reparar para ser watertight.")
    logging.info("Malla reparada y es watertight.")
    return mesh