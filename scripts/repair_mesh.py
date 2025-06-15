import trimesh
import time
import logging

def repair_mesh(mesh: trimesh.Trimesh, max_time_seconds: int = 300) -> trimesh.Trimesh:
    initial_vertex_count = len(mesh.vertices)
    initial_triangle_count = len(mesh.faces)

    start_time = time.time()
    iteration = 0

    while time.time() - start_time < max_time_seconds:
        iteration += 1
        # Reparaciones de la malla
        mesh.fill_holes()
        mesh.remove_degenerate_faces()
        mesh.remove_duplicate_faces()
        mesh.remove_infinite_values()
        mesh.remove_unreferenced_vertices()
        mesh.process(validate=True)

        final_vertex_count = len(mesh.vertices)
        final_triangle_count = len(mesh.faces)

        logging.info(f"Iteration {iteration}: Vertex count changes from {initial_vertex_count} to {final_vertex_count} ({final_vertex_count - initial_vertex_count:+d})")
        logging.info(f"Iteration {iteration}: Triangle count changes from {initial_triangle_count} to {final_triangle_count} ({final_triangle_count - initial_triangle_count:+d})")

        if mesh.is_watertight:
            logging.info("Malla reparada y es watertight.")
            return mesh
        else:
            logging.warning(f"Reparación iteración {iteration} no fue exitosa. Intentando nuevamente...")

    logging.error("La malla no se pudo reparar para ser watertight después del tiempo máximo permitido.")
    report_mesh_problems(mesh)
    return mesh

def report_mesh_problems(mesh: trimesh.Trimesh) -> None:
    if not mesh.is_watertight:
        logging.warning("La malla tiene agujeros.")
    if not mesh.is_watertight:
        logging.warning("La malla tiene bordes no conectados.")
