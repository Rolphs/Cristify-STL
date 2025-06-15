import sys
import os
from tkinter import filedialog, messagebox
from datetime import datetime
import tkinter as tk

# Agregar el directorio src al PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stl_to_vector import stl_to_vectors
from optimize_with_ml import optimize_vectors
from vector_to_stl import vectors_to_stl

def select_and_optimize_stl():
    root = tk.Tk()
    root.withdraw()
    input_stl = filedialog.askopenfilename(title="Select STL File", filetypes=[("STL Files", "*.stl")])

    if input_stl:
        try:
            vectors = stl_to_vectors(input_stl)
            optimized_vectors = optimize_vectors(vectors)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_stl = os.path.join('data/output',
                                      f'optimized_{os.path.basename(input_stl).split(".")[0]}_{timestamp}.stl')
            vectors_to_stl(optimized_vectors, output_stl)
            messagebox.showinfo("Success", f"Optimized STL file saved as {output_stl}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during optimization: {e}")

def create_main_window():
    window = tk.Tk()
    window.title("STL Optimizer")
    window.geometry("400x200")

    label = tk.Label(window, text="Welcome to the STL Optimizer", font=("Helvetica", 16))
    label.pack(pady=20)

    optimize_button = tk.Button(window, text="Select STL File to Optimize", command=select_and_optimize_stl,
                                font=("Helvetica", 14))
    optimize_button.pack(pady=20)

    window.mainloop()

if __name__ == "__main__":
    create_main_window()