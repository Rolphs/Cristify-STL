import trimesh
import numpy as np
from scipy.spatial import KDTree
import logging

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

def check_mesh_health(mesh: trimesh.Trimesh) -> None:
    """Verifica que la malla sea watertight."""
    if not mesh.is_watertight:
        raise ValueError("La malla no es watertight.")
    logging.info("La malla es watertight y saludable.")

def repair_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Repara una malla para que sea watertight."""
    mesh.fill_holes()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_infinite_values()
    mesh.remove_unreferenced_vertices()
    if not mesh.is_watertight:
        raise ValueError("La malla no se pudo reparar para ser watertight.")
    logging.info("Malla reparada y es watertight.")
    return mesh

def create_kd_tree(vertices: np.ndarray) -> KDTree:
    """Crea un árbol KD a partir de los vértices de la malla."""
    return KDTree(vertices)

def apply_gravitational_attraction(input_mesh: trimesh.Trimesh, kd_tree: KDTree, g: float = 1e-3) -> np.ndarray:
    """Aplica una fuerza de atracción gravitacional entre los vértices."""
    new_vertices = input_mesh.vertices.copy()
    for i, vertex in enumerate(input_mesh.vertices):
        distances, indices = kd_tree.query(vertex, k=10)
        force = np.zeros(3)
        for dist, index in zip(distances[1:], indices[1:]):
            direction = input_mesh.vertices[index] - vertex
            if dist > 0:
                force += g * direction / (dist ** 2)
        new_vertices[i] += force
    return new_vertices

def fractal_noise(vertices: np.ndarray, scale: float = 0.1, octaves: int = 4) -> np.ndarray:
    """Añade ruido fractal a los vértices para crear detalles orgánicos."""
    noise = np.zeros_like(vertices)
    for octave in range(octaves):
        frequency = 2 ** octave
        amplitude = scale / frequency
        noise += amplitude * np.random.randn(*vertices.shape)
    return vertices + noise

def make_organic_with_gravity(input_mesh: trimesh.Trimesh, noise_strength: float = 0.01, smooth_iterations: int = 200,
                              g: float = 1e-3, fractal_scale: float = 0.1, fractal_octaves: int = 4) -> trimesh.Trimesh:
    """Combina la adición de ruido fractal, suavizado y atracción gravitacional."""
    input_mesh.vertices = fractal_noise(input_mesh.vertices, scale=fractal_scale, octaves=fractal_octaves)
    logging.info("Ruido fractal añadido a los vértices.")
    trimesh.smoothing.filter_taubin(input_mesh, lamb=0.5, nu=-0.53, iterations=smooth_iterations)
    logging.info("Suavizado Taubin aplicado.")
    kd_tree = create_kd_tree(input_mesh.vertices)
    input_mesh.vertices = apply_gravitational_attraction(input_mesh, kd_tree, g)
    logging.info("Atracción gravitacional aplicada.")
    return input_mesh

# Rutas de los archivos de entrada y salida
input_file_path = '/Users/raulmb/Downloads/corazon.stl'
output_file_path = '/Users/raulmb/Downloads/corazon_optimizado.stl'

# Cargar la malla
initial_mesh = load_stl(input_file_path)
if initial_mesh.is_empty:
    raise FileNotFoundError("No se pudo cargar la malla. Verifica la ruta del archivo.")
logging.info(f"Malla cargada: {initial_mesh}")

# Reorientar la malla
oriented_mesh = reorient_mesh_for_printing(initial_mesh)

# Verificar salud de la malla y repararla si es necesario
try:
    check_mesh_health(oriented_mesh)
except ValueError as e:
    logging.warning(f"{e} Intentando reparar la malla...")
    oriented_mesh = repair_mesh(oriented_mesh)

# Hacer la malla más orgánica y eficiente con atracción gravitacional
organic_mesh = make_organic_with_gravity(oriented_mesh, noise_strength=0.01, smooth_iterations=200)
logging.info("Malla transformada a una forma más orgánica y eficiente.")

# Guardar la malla procesada
save_stl(organic_mesh, output_file_path)
logging.info(f"Malla guardada en {output_file_path}")
