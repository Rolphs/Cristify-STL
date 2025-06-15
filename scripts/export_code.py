import os

def print_tree(directory, prefix='', structure_file=None):
    # Imprimir el nombre del directorio actual
    line = f"{prefix}{os.path.basename(directory)}/"
    print(line)
    if structure_file:
        structure_file.write(line + '\n')

    # Obtener el contenido del directorio
    items = sorted(os.listdir(directory))

    for i, item in enumerate(items):
        path = os.path.join(directory, item)
        # Determinar si es el último elemento para ajustar el prefijo
        if i == len(items) - 1:
            tree_prefix = f"{prefix}└── "
        else:
            tree_prefix = f"{prefix}├── "

        if os.path.isdir(path):
            # Imprimir subdirectorios (solo el nombre, sin recursión)
            line = f"{tree_prefix}{item}/"
            print(line)
            if structure_file:
                structure_file.write(line + '\n')
        elif item.endswith(".py"):
            # Imprimir archivos
            line = f"{tree_prefix}{item}"
            print(line)
            if structure_file:
                structure_file.write(line + '\n')

def export_code(directory, code_file):
    # Obtener el contenido del directorio
    items = sorted(os.listdir(directory))

    for item in items:
        if item.endswith(".py"):  # Incluir todos los archivos .py
            file_path = os.path.join(directory, item)
            with open(file_path, 'r', encoding='utf-8') as f:
                header = f"\n\n--- {file_path} ---\n\n"
                content = f.read()
                print(header)
                print(content)
                if code_file:
                    code_file.write(header + '\n')
                    code_file.write(content + '\n')

if __name__ == "__main__":
    # Obtener la ruta del directorio donde se encuentra este script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Crear el directorio de documentación si no existe
    documentation_dir = os.path.join(current_directory, 'documentation')
    os.makedirs(documentation_dir, exist_ok=True)

    # Rutas de los archivos de salida
    structure_path = os.path.join(documentation_dir, 'project_structure.txt')
    code_path = os.path.join(documentation_dir, 'project_code.txt')

    # Verificar si los archivos ya existen y anunciar si serán sobrescritos
    if os.path.exists(structure_path):
        print(f"Sobrescribiendo el archivo existente: {structure_path}")
    if os.path.exists(code_path):
        print(f"Sobrescribiendo el archivo existente: {code_path}")

    # Abrir los archivos de salida para escritura
    with open(structure_path, 'w', encoding='utf-8') as structure_file, \
            open(code_path, 'w', encoding='utf-8') as code_file:
        # Imprimir la estructura del árbol de directorios
        print("Estructura del proyecto:\n")
        structure_file.write("Estructura del proyecto:\n\n")
        print_tree(current_directory, structure_file=structure_file)

        # Exportar el contenido de los archivos .py en un solo archivo
        export_code(current_directory, code_file)

    print(f"\nLa estructura del proyecto se ha guardado en {structure_path}")
    print(f"El contenido de los archivos .py se ha guardado en {code_path}")