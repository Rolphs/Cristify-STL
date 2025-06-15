import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import os
import cmd
import logging
from load_save import load_stl, save_stl
from reorient_repair import reorient_mesh_for_printing, check_mesh_health, repair_mesh
from texturize_bark import create_kd_tree, apply_gravitational_attraction, fractal_noise as bark_fractal_noise
from texturize_bone import fractal_noise as bone_fractal_noise
from texturize_liquid_metal import smooth_mesh
from simplify_mesh import simplify_mesh
from gravitational_tension import apply_gravitational_tension_model
from voronize import voronize_mesh
from wrap import wrap_mesh
from menu import App, show_help
from report import generate_summary_report

# Configuración de logging
logging.basicConfig(level=logging.INFO)

def run_verification():
    try:
        result = subprocess.run([sys.executable, "Verify.py"], check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error",
                             "La verificación de dependencias ha fallado. Por favor, verifica las dependencias.")
        sys.exit(1)

run_verification()

class MeshEditor(cmd.Cmd):
    """
    Clase que proporciona una interfaz de línea de comandos para manipular mallas 3D.
    """
    intro = None
    prompt = "(editor) "
    file_path = None
    mesh = None
    files_processed = []
    files_repaired = []
    repair_attempts = {}

    def preloop(self):
        show_help()

    def do_load(self, arg):
        """
        Cargar un archivo STL: load <ruta_del_archivo>
        """
        if not arg:
            arg = input("Por favor, proporciona la ruta del archivo STL: ")
        if not os.path.exists(arg):
            print("El archivo no existe. Por favor, proporciona una ruta válida.")
            return
        try:
            self.file_path = arg
            self.mesh = load_stl(arg)
            if not self.mesh.is_empty:
                print(f"Malla cargada de {arg}")
                logging.info(f"Malla cargada de {arg}")
                self.files_processed.append(arg)
            else:
                print("Error al cargar la malla.")
        except Exception as e:
            print(f"Error al cargar la malla: {e}")
            logging.error(f"Error al cargar la malla: {e}")

    def do_save(self, arg):
        """
        Guardar el archivo STL: save <ruta_del_archivo>
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        if not arg:
            arg = input("Por favor, proporciona la ruta para guardar el archivo STL: ")
        output_path = arg
        if os.path.exists(output_path):
            response = input(f"El archivo {output_path} ya existe. ¿Deseas sobrescribirlo? (s/n): ")
            if response.lower() != 's':
                print("Operación cancelada. Elige un nuevo nombre para el archivo.")
                return
        try:
            with open(output_path, 'w') as file:
                save_stl(self.mesh, file)
            print(f"Malla guardada en {output_path}")
            logging.info(f"Malla guardada en {output_path}")
        except Exception as e:
            print(f"Error al guardar la malla: {e}")
            logging.error(f"Error al guardar la malla: {e}")

    def do_reorient(self, arg):
        """
        Reorientar la malla para impresión: reorient
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            self.mesh = reorient_mesh_for_printing(self.mesh)
            print("Malla reorientada para impresión.")
            logging.info("Malla reorientada para impresión.")
        except Exception as e:
            print(f"Error al reorientar la malla: {e}")
            logging.error(f"Error al reorientar la malla: {e}")

    def do_check_health(self, arg):
        """
        Verificar la salud de la malla: check_health
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            check_mesh_health(self.mesh)
            print("La malla es watertight y saludable.")
            logging.info("La malla es watertight y saludable.")
        except ValueError as e:
            print(f"Problema detectado: {e}")
            logging.warning(f"Problema detectado: {e}")

    def do_repair(self, arg):
        """
        Reparar la malla: repair
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            repair_attempts_count = self.repair_attempts.get(self.file_path, 0)
            self.mesh = repair_mesh(self.mesh)
            print("Malla reparada y es watertight.")
            logging.info("Malla reparada y es watertight.")
            self.files_repaired.append(self.file_path)
            self.repair_attempts[self.file_path] = repair_attempts_count + 1
        except ValueError as e:
            print(f"No se pudo reparar la malla: {e}")
            logging.error(f"No se pudo reparar la malla: {e}")
            self.repair_attempts[self.file_path] = repair_attempts_count + 1

    def do_texturize_bark(self, arg):
        """
        Aplicar textura de corteza: texturize_bark
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            kd_tree = create_kd_tree(self.mesh.vertices)
            self.mesh.vertices = apply_gravitational_attraction(self.mesh, kd_tree)
            self.mesh.vertices = bark_fractal_noise(self.mesh.vertices)
            print("Textura de corteza aplicada.")
            logging.info("Textura de corteza aplicada.")
        except Exception as e:
            print(f"Error al aplicar textura de corteza: {e}")
            logging.error(f"Error al aplicar textura de corteza: {e}")

    def do_texturize_bone(self, arg):
        """
        Aplicar textura de hueso: texturize_bone
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            self.mesh.vertices = bone_fractal_noise(self.mesh.vertices)
            print("Textura de hueso aplicada.")
            logging.info("Textura de hueso aplicada.")
        except Exception as e:
            print(f"Error al aplicar textura de hueso: {e}")
            logging.error(f"Error al aplicar textura de hueso: {e}")

    def do_texturize_liquid_metal(self, arg):
        """
        Aplicar textura de metal líquido: texturize_liquid_metal
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            self.mesh.vertices = smooth_mesh(self.mesh.vertices)
            print("Textura de metal líquido aplicada.")
            logging.info("Textura de metal líquido aplicada.")
        except Exception as e:
            print(f"Error al aplicar textura de metal líquido: {e}")
            logging.error(f"Error al aplicar textura de metal líquido: {e}")

    def do_simplify(self, arg):
        """
        Simplificar la malla: simplify
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            self.mesh = simplify_mesh(self.mesh)
            print("Malla simplificada.")
            logging.info("Malla simplificada.")
        except Exception as e:
            print(f"Error al simplificar la malla: {e}")
            logging.error(f"Error al simplificar la malla: {e}")

    def do_apply_gravitational_tension(self, arg):
        """
        Aplicar modelo de tensión gravitacional: apply_gravitational_tension
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            self.mesh = apply_gravitational_tension_model(self.mesh)
            print("Modelo de tensión gravitacional aplicado.")
            logging.info("Modelo de tensión gravitacional aplicado.")
        except Exception as e:
            print(f"Error al aplicar modelo de tensión gravitacional: {e}")
            logging.error(f"Error al aplicar modelo de tensión gravitacional: {e}")

    def do_voronize(self, arg):
        """
        Aplicar voronización a la malla: voronize
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            self.mesh = voronize_mesh(self.mesh)
            print("Voronización aplicada.")
            logging.info("Voronización aplicada.")
        except Exception as e:
            print(f"Error al aplicar voronización: {e}")
            logging.error(f"Error al aplicar voronización: {e}")

    def do_wrap(self, arg):
        """
        Envolver la malla: wrap
        """
        if self.mesh is None:
            print("Primero carga una malla con 'load'.")
            return
        try:
            self.mesh = wrap_mesh(self.mesh)
            print("Malla envuelta.")
            logging.info("Malla envuelta.")
        except Exception as e:
            print(f"Error al envolver la malla: {e}")
            logging.error(f"Error al envolver la malla: {e}")

    def do_generate_report(self, arg):
        """
        Generar un reporte de resumen: generate_report
        """
        try:
            generate_summary_report(self.files_processed, self.files_repaired, self.repair_attempts)
            print("Reporte de resumen generado.")
            logging.info("Reporte de resumen generado.")
        except Exception as e:
            print(f"Error al generar el reporte: {e}")
            logging.error(f"Error al generar el reporte: {e}")

    def do_exit(self, arg):
        """
        Salir del editor: exit
        """
        print("Saliendo del editor.")
        return True

if __name__ == "__main__":
    MeshEditor().cmdloop()
