import time
import logging
import trimesh
from trimesh.repair import fill_holes, remove_infinite_values, remove_unreferenced_vertices
from optimizacion_fractal import generate_fractal_geometry
from ml_module import predict_and_apply_repair

logger = logging.getLogger()

def repair_mesh(mesh, max_time_seconds=300):
    initial_vertex_count = len(mesh.vertices)
    initial_triangle_count = len(mesh.faces)

    start_time = time.time()
    iteration = 0

    while time.time() - start_time < max_time_seconds:
        iteration += 1
        # Reparaciones de la malla
        mesh.fill_holes()
        mesh.remove_degenerate_faces()
        # mesh.remove_duplicate_faces()  # Esta línea se comenta ya que no existe
        mesh.remove_infinite_values()
        mesh.remove_unreferenced_vertices()
        mesh.process(validate=True)

        final_vertex_count = len(mesh.vertices)
        final_triangle_count = len(mesh.faces)

        logging.info(f"Iteration {iteration}: Vertex count changes from {initial_vertex_count} to {final_vertex_count} ({final_vertex_count - initial_vertex_count:+d})")
        logging.info(f"Iteration {iteration}: Triangle count changes from {initial_triangle_count} to {final_triangle_count} ({final_triangle_count - initial_triangle_count:+d})")

        if mesh.is_watertight:
            logging.info("Malla reparada y es watertight.")
            return mesh, iteration, True
        else:
            logging.warning(f"Reparación iteración {iteration} no fue exitosa. Intentando nuevamente...")

    logging.error("La malla no se pudo reparar para ser watertight después del tiempo máximo permitido.")
    report_mesh_problems(mesh)
    return mesh, iteration, False

def optimize_mesh(mesh, max_iterations):
    for _ in range(max_iterations):
        mesh, iterations, repaired = repair_mesh(mesh)
        if repaired:
            return mesh, iterations, True
        predict_and_apply_repair(mesh)
    return mesh, max_iterations, False

def report_mesh_problems(mesh):
    logging.warning("La malla tiene problemas de integridad.")