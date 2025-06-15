import os
from datetime import datetime

def create_project_structure():
    # Obtener el timestamp actual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Función recursiva para recolectar la estructura y la información de los archivos, omitiendo directorios irrelevantes
    def recolectar_estructura(base_path, prefijo=''):
        estructura_info = []
        exclude_dirs = {'External Libraries', 'Scratches and Consoles', '.venv', '__pycache__'}
        for root, dirs, files in os.walk(base_path):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            level = root.replace(base_path, '').count(os.sep)
            indent = '│   ' * (level)
            estructura_info.append(f"{indent}├── {os.path.basename(root)}/")
            sub_indent = '│   ' * (level + 1)
            for f in files:
                estructura_info.append(f"{sub_indent}├── {f}")
        if estructura_info:
            estructura_info[-1] = estructura_info[-1].replace('├──', '└──')
        return estructura_info

    # Función para recolectar el contenido de los archivos .py relevantes
    def recolectar_contenido(base_path, max_lines=100):
        contenido = []
        exclude_dirs = {'External Libraries', 'Scratches and Consoles', '.venv', '__pycache__'}
        for root, dirs, files in os.walk(base_path):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            print(f"Leyendo archivo: {file_path} (tamaño: {file_size} bytes)")
                            if file_size > 0:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    contenido.append(f"# {file_path}\n")
                                    contenido.extend(lines[:max_lines])
                                    if len(lines) > max_lines:
                                        contenido.append(f"# ... (truncated {len(lines) - max_lines} lines)\n")
                                    contenido.append("\n" + "#" * 80 + "\n")
                            else:
                                print(f"Archivo vacío: {file_path}")
                        else:
                            print(f"Archivo no encontrado: {file_path}")
                    except Exception as e:
                        print(f"Error leyendo {file_path}: {e}")
        return contenido

    # Cambiar al directorio raíz del proyecto
    project_root = '/Users/raulmb/PycharmProjects/VectorSTL'
    print(f"Directorio raíz del proyecto: {project_root}")

    # Recolectar la estructura de directorios y archivos existentes
    estructura_info = [f"{os.path.basename(project_root)}/"]
    estructura_info.extend(recolectar_estructura(project_root, '│   '))

    # Crear el directorio documentation si no existe
    documentation_dir = os.path.join(project_root, 'documentation')
    os.makedirs(documentation_dir, exist_ok=True)
    print(f"Directorio 'documentation' creado o ya existente: {documentation_dir}")

    # Crear el archivo de estructura con timestamp
    estructura_file = os.path.join(documentation_dir, f'estructura_{timestamp}.txt')
    with open(estructura_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(estructura_info))
    print(f"Archivo de estructura creado: {estructura_file}")

    # Crear el archivo de contenido con timestamp
    contenido = recolectar_contenido(project_root)
    contenido_file = os.path.join(documentation_dir, f'contenido_{timestamp}.txt')
    with open(contenido_file, 'w', encoding='utf-8') as f:
        f.write("".join(contenido))
    print(f"Archivo de contenido creado: {contenido_file}")

    print("Estructura de archivos y directorios creada con éxito.")

if __name__ == "__main__":
    create_project_structure()