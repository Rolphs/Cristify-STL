import trimesh
import numpy as np
import logging
import pymeshlab

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

def get_overhang_faces(input_mesh: trimesh.Trimesh, max_overhang_angle: float = 45.0) -> np.ndarray:
    """Identifica las caras que necesitan soportes debido a su ángulo."""
    angles = input_mesh.face_normals[:, 2]
    overhang_faces = np.where(np.degrees(np.arccos(angles)) > max_overhang_angle)[0]
    return overhang_faces

def modify_overhangs(input_mesh: trimesh.Trimesh, overhang_faces: np.ndarray) -> trimesh.Trimesh:
    """Modifica las caras que necesitan soportes transformándolas en arcos góticos."""
    new_faces = []
    new_vertices_list = []

    for face_index in overhang_faces:
        face = input_mesh.faces[face_index]
        vertices = input_mesh.vertices[face]

        center = vertices.mean(axis=0)
        center[2] += 0.01  # Ajustar altura para eliminar voladizos

        new_vertex_indices = []
        for _ in range(3):
            new_vertices_list.append(center)
            new_vertex_indices.append(len(input_mesh.vertices) + len(new_vertices_list) - 1)

        for i in range(3):
            new_faces.append([face[i], face[(i + 1) % 3], new_vertex_indices[i]])

    if new_vertices_list:
        new_vertices_array = np.array(new_vertices_list)
        input_mesh.vertices = np.vstack((input_mesh.vertices, new_vertices_array))

    if new_faces:
        new_faces_array = np.array(new_faces)
        input_mesh.faces = np.vstack((input_mesh.faces, new_faces_array))

    input_mesh.update_faces(np.delete(input_mesh.faces, overhang_faces, axis=0))

    return input_mesh

def gaudify_mesh(input_mesh: trimesh.Trimesh, max_overhang_angle: float = 45.0, max_iterations: int = 10) -> trimesh.Trimesh:
    """Transforma la malla en una estructura inspirada en arcos góticos para eliminar la necesidad de soportes."""
    iteration = 0

    while iteration < max_iterations:
        logging.info(f"Iteración {iteration + 1}/{max_iterations}")
        overhang_faces = get_overhang_faces(input_mesh, max_overhang_angle)
        logging.info(f"Voladizos encontrados: {len(overhang_faces)}")

        if len(overhang_faces) == 0:
            logging.info("No se encontraron más voladizos.")
            break

        input_mesh = modify_overhangs(input_mesh, overhang_faces)
        iteration += 1

        # Verificar la integridad de la malla después de cada modificación
        if not input_mesh.is_watertight:
            logging.warning("La malla no es watertight después de la modificación. Intentando reparar.")
            input_mesh = input_mesh.fill_holes()

        if input_mesh.faces.shape[0] == 0:
            logging.error("La malla no tiene caras después de la modificación. Deteniendo proceso.")
            break

    return input_mesh

# Bloque principal para ejecutar y probar la función gaudify_mesh
if __name__ == "__main__":
    # Rutas de los archivos de entrada y salida
    input_file_path = '/Users/raulmb/Downloads/corazon.stl'
    output_file_path = '/Users/raulmb/Downloads/corazon_gaudificado.stl'

    # Cargar la malla
    initial_mesh = load_stl(input_file_path)
    if initial_mesh.is_empty:
        raise FileNotFoundError("No se pudo cargar la malla. Verifica la ruta del archivo.")

    logging.info(f"Malla cargada: {initial_mesh}")

    # Reorientar la malla
    oriented_mesh = reorient_mesh_for_printing(initial_mesh)

    # Aplicar gaudificación a la malla
    gaudified_mesh = gaudify_mesh(oriented_mesh)
    logging.info("Malla gaudificada para eliminar voladizos.")

    # Guardar la malla procesada
    save_stl(gaudified_mesh, output_file_path)
    logging.info(f"Malla guardada en {output_file_path}")

