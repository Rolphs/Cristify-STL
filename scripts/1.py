import trimesh
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_stl(file_path: str) -> trimesh.Trimesh:
    """
    Carga un archivo STL y lo devuelve como un objeto Trimesh.

    Args:
        file_path (str): Ruta del archivo STL a cargar.

    Returns:
        trimesh.Trimesh: Objeto Trimesh cargado desde el archivo STL.
    """
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
    """
    Guarda un objeto Trimesh como un archivo STL.

    Args:
        mesh (trimesh.Trimesh): Objeto Trimesh a guardar.
        file_path (str): Ruta donde se guardará el archivo STL.
    """
    try:
        mesh.export(file_path)
        logging.info(f"Archivo STL guardado en {file_path}")
    except Exception as e:
        logging.error(f"Error al guardar el archivo STL: {e}")

def reorient_mesh_for_printing(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """
    Reorienta la malla para la mejor posición de impresión.

    Args:
        mesh (trimesh.Trimesh): Objeto Trimesh a reorientar.

    Returns:
        trimesh.Trimesh: Objeto Trimesh reorientado.
    """
    mesh.rezero()  # Opcional: Centra la malla en el origen
    orientation = mesh.bounding_box_oriented.primitive.transform
    mesh.apply_transform(orientation)
    logging.info("Malla reorientada para la mejor posición de impresión.")
    return mesh

def check_mesh_health(mesh: trimesh.Trimesh) -> None:
    """
    Verifica que la malla sea watertight y no tenga manifolds.

    Args:
        mesh (trimesh.Trimesh): Objeto Trimesh a verificar.

    Raises:
        ValueError: Si la malla no es watertight o tiene partes manifold.
    """
    if not mesh.is_watertight:
        raise ValueError("La malla no es watertight.")
    if mesh.is_watertight and not mesh.is_watertight:
        raise ValueError("La malla tiene partes manifold.")
    logging.info("La malla es watertight y saludable.")

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

# Verificar salud de la malla
check_mesh_health(oriented_mesh)

# Guardar la malla procesada
save_stl(oriented_mesh, output_file_path)
logging.info(f"Malla guardada en {output_file_path}")
