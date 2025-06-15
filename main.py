import os
import logging
from trimesh import load_mesh
from optimizacion import optimize_mesh
from ml_module import train_ml_model, predict_and_apply_repair
from reporteo import generate_process_summary

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Directorios de entrada y salida
input_directory = "/Users/raulmb/Library/CloudStorage/OneDrive-Personal/3D Prints and Models"
output_directory = "/Users/raulmb/Library/CloudStorage/OneDrive-Personal/optimized"

# Almacenar resumen del proceso
process_summary = {
    "total_files_processed": 0,
    "total_iterations": 0,
    "files_repaired": [],
    "files_not_repaired": []
}


def process_directory(input_dir, output_dir, max_iterations=25):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".stl"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_optimized.stl")

                logger.info(f"Procesando archivo STL: {input_path}")
                process_summary["total_files_processed"] += 1

                try:
                    initial_mesh = load_mesh(input_path)
                    optimized_mesh, iterations, repaired = optimize_mesh(initial_mesh, max_iterations)

                    if repaired:
                        process_summary["files_repaired"].append({
                            "file": input_path,
                            "iterations": iterations
                        })
                    else:
                        process_summary["files_not_repaired"].append({
                            "file": input_path,
                            "iterations": iterations
                        })

                    process_summary["total_iterations"] += iterations

                    optimized_mesh.export(output_path)
                    logger.info(f"Archivo STL guardado en {output_path}")

                except Exception as e:
                    logger.error(f"Error procesando {input_path}: {str(e)}")


if __name__ == "__main__":
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    process_directory(input_directory, output_directory)
    generate_process_summary(process_summary)