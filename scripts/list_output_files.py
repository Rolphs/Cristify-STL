import os

def list_output_files():
    output_directory = 'data/output'
    if os.path.exists(output_directory):
        files = os.listdir(output_directory)
        if files:
            print("Archivos en 'data/output':")
            for file in files:
                print(file)
        else:
            print("'data/output' está vacío.")
    else:
        print("El directorio 'data/output' no existe.")

if __name__ == "__main__":
    list_output_files()