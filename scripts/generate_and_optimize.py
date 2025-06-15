from stl_to_vector import stl_to_vectors
from vector_to_stl import vectors_to_stl
from optimize_with_ml import optimize_vectors
from datetime import datetime
import os

def main():
    # Leer archivo STL
    input_stl = 'data/input/example.stl'
    vectors = stl_to_vectors(input_stl)

    # Optimizar vectores usando AI/ML
    optimized_vectors = optimize_vectors(vectors)

    # Generar archivo STL optimizado
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_stl = os.path.join('data/output', f'optimized_example_{timestamp}.stl')
    vectors_to_stl(optimized_vectors, output_stl)

if __name__ == "__main__":
    main()