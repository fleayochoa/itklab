import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os
import re
import sys

def main():
    # Ocultar la ventana principal de Tkinter
    root = tk.Tk()
    root.withdraw()

    # Abrir ventana para seleccionar archivo
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo CSV",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    if not file_path:
        print("No se seleccionó ningún archivo.")
        return

    df = pd.read_csv(file_path)
    filename = os.path.basename(file_path)
    

    # Regex para validar: XXXX-3 YYYY-4
    patron = r"^\d{4}-3 \d{4}-4\.csv$"
    if not re.match(patron, filename):
        print(f"Nombre de archivo inválido: {filename}")
        print("Debe tener el formato: XXXX-3 YYYY-4.csv")
        sys.exit(1)
    print("Nombres de las columnas:")
    print(df.columns.tolist())

    print("Valores para dispositivo 1:")
    print("{}\t{}\t{}\t{}\t{}\t{}".format(df["Vin1+ Prom. (V)"].iloc[-1], df["Vin1- Prom. (V)"].iloc[-1],
                                           df["GND1+ Prom. (V)"].iloc[-1], df["GND1- Prom. (V)"].iloc[-1],
                                             df["HVmon1 Prom. (V)"].iloc[-1], df["NTC1 Prom. (V)"].iloc[-1]))
    print("Valores para dispositivo 2:")
    print("{}\t{}\t{}\t{}\t{}\t{}".format(df["Vin2+ Prom. (V)"].iloc[-1], df["Vin2- Prom. (V)"].iloc[-1],
                                           df["GND2+ Prom. (V)"].iloc[-1], df["GND2- Prom. (V)"].iloc[-1],
                                             df["HVmon2 Prom. (V)"].iloc[-1], df["NTC2 Prom. (V)"].iloc[-1]))
    

if __name__ == "__main__":
    main()
