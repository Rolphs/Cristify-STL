# main.py
import trimesh
import logging
import textura
import topologia

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_stl(file_path: str) -> trimesh.Trimesh:
    """Carga un archivo STL y lo devuelve como un objeto Trimesh."""
    try:
        mesh = trimesh.load(file_path)
        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError("El archivo no contiene una malla Trimesh válida.")
        logging.info("Archivo STL cargado correctamente.")
        return mesh
    except Exception as e:
        logging.error(f"Error al cargar el archivo STL: {e}")
        return trimesh.Trimesh()

def save_stl(mesh: trimesh.Trimesh, file_path: str) -> None:
    """Guarda un objeto Trimesh como un archivo STL."""
    try:
        mesh.export(file_path)
        logging.info(f"Archivo STL guardado en {file_path}")
    except Exception as e:
        logging.error(f"Error al guardar el archivo STL: {e}")

def reorient_mesh_for_printing(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Reorienta la malla para la mejor posición de impresión."""
    mesh.rezero()
    orientation = mesh.bounding_box_oriented.primitive.transform
    mesh.apply_transform(orientation)
    logging.info("Malla reorientada para la mejor posición de impresión.")
    return mesh

def make_organic(input_mesh: trimesh.Trimesh, surface_tension_strength: float, gravity_strength: float, noise_strength: float, max_iterations: int, convergence_threshold: float) -> trimesh.Trimesh:
    """Aplica tensión superficial, atracción gravitacional y ruido aleatorio hasta que se alcance el umbral de convergencia o el número máximo de iteraciones."""
    edges = input_mesh.edges_unique
    vertices = input_mesh.vertices.copy()

    for iteration in range(max_iterations):
        previous_vertices = vertices.copy()

        # Aplicar tensión superficial
        vertices = topologia.apply_surface_tension(vertices, edges, k=surface_tension_strength)

        # Agregar ruido aleatorio controlado
        vertices = textura.add_random_noise(vertices, noise_strength=noise_strength)

        #​⬤