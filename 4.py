import trimesh
import numpy as np
import logging
from scipy.spatial import KDTree

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
        return trimesh.Trimesh()  # Devolver un objeto Trimesh vacío en caso de error


def save_stl(mesh: trimesh.Trimesh, file_path: str) -> None:
    """Guarda un objeto Trimesh como un archivo STL."""
    try:
        mesh.export(file_path)
        logging.info(f"Archivo STL guardado en {file_path}")
    except Exception as e:
        logging.error(f"Error al guardar el archivo STL: {e}")


def reorient_mesh_for_printing(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Reorienta la malla para la mejor posición de impresión."""
    mesh.rezero()  # Opcional: Centra la malla en el origen
    orientation = mesh.bounding_box_oriented.primitive.transform
    mesh.apply_transform(orientation)
    logging.info("Malla reorientada para la mejor posición de impresión.")
    return mesh


def create_kd_tree(vertices: np.ndarray) -> KDTree:
    """Crea un árbol KD a partir de los vértices de la malla para búsquedas rápidas de vecinos."""
    if not isinstance(vertices, np.ndarray):
        raise ValueError("Los vértices deben ser un array numpy.")
    return KDTree(vertices)


def apply_gravitational_attraction(input_mesh: trimesh.Trimesh, kd_tree: KDTree, g: float = 1e-3) -> np.ndarray:
    """Aplica una fuerza de atracción gravitacional entre los vértices para simular una forma más eficiente y orgánica."""
    new_vertices = input_mesh.vertices.copy()
    for i, vertex in enumerate(input_mesh.vertices):
        distances, indices = kd_tree.query(vertex, k=10)  # Considerar 10 vecinos más cercanos
        force = np.zeros(3)
        for dist, index in zip(distances[1:], indices[1:]):  # Saltar la distancia cero (el mismo punto)
            direction = input_mesh.vertices[index] - vertex
            if dist > 0:  # Para evitar división por cero
                force += g * direction / (dist ** 2)
        new_vertices[i] += force
    return new_vertices


def make_organic_with_gravity(input_mesh: trimesh.Trimesh, noise_strength: float = 0.01, smooth_iterations: int = 200,
                              g: float = 1e-3) -> trimesh.Trimesh:
    """Combina la adición de ruido, suavizado Taubin y atracción gravitacional para hacer la malla más orgánica y eficiente."""
    if not isinstance(input_mesh, trimesh.Trimesh):
        raise ValueError("El input_mesh debe ser un objeto Trimesh.")

    # Añadir ruido
    noise = noise_strength * np.random.randn(*input_mesh.vertices.shape)
    input_mesh.vertices += noise
    logging.info("Ruido añadido a los vértices.")

    # Suavizado Taubin
    trimesh.smoothing.filter_taubin(input_mesh, lamb=0.5, nu=-0.53, iterations=smooth_iterations)
    logging.info("Suavizado Taubin aplicado.")

    # Crear KD-Tree para vértices
    kd_tree = create_kd_tree(input_mesh.vertices)

    # Aplicar atracción gravitacional para hacer la malla más eficiente
    input_mesh.vertices = apply_gravitational_attraction(input_mesh, kd_tree, g)
    logging.info("Atracción gravitacional aplicada.")

    return input_mesh


# Bloque principal para ejecutar y probar la función
if __name__ == "__main__":
    # Rutas de los archivos de entrada y salida
    input_file_path = '/Users/raulmb/Downloads/corazon.stl'
    output_file_path = '/Users/raulmb/Downloads/corazon_optimizado_gravedad.stl'

    # Cargar la malla
    initial_mesh = load_stl(input_file_path)
    if initial_mesh.is_empty:
        raise FileNotFoundError("No se pudo cargar la malla. Verifica la ruta del archivo.")

    logging.info(f"Malla cargada: {initial_mesh}")

    # Reorientar la malla
    oriented_mesh = reorient_mesh_for_printing(initial_mesh)

    # Optimizar la malla con gravedad
    optimized_mesh = make_organic_with_gravity(oriented_mesh)
    logging.info("Malla optimizada utilizando teorías de gravedad y tensión superficial.")

    # Guardar la malla procesada
    save_stl(optimized_mesh, output_file_path)
    logging.info(f"Malla guardada en {output_file_path}")