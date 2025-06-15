import trimesh
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_stl(file_path: str) -> trimesh.Trimesh:
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
    try:
        mesh.export(file_path)
        logging.info(f"Archivo STL guardado en {file_path}")
    except Exception as e:
        logging.error(f"Error al guardar el archivo STL: {e}")