#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from pdf_coordinate_finder import PDFCoordinateFinder

def main():
    """
    Запускает инструмент для поиска координат на PDF файле.
    Если указан путь к PDF файлу в аргументах командной строки, 
    то этот файл будет открыт автоматически.
    """
    # Проверяем наличие аргументов командной строки
    pdf_path = None
    
    # Если запущено без аргументов, но есть целевой PDF файл в директории
    target_pdf = "Безопастность_и_охрана_труда_корочка_1.pdf"
    if os.path.exists(target_pdf):
        pdf_path = target_pdf
    
    # Если есть аргумент командной строки, используем его
    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        if os.path.exists(arg_path):
            pdf_path = arg_path
        else:
            print(f"Файл не найден: {arg_path}")
    
    # Создаем главное окно
    root = tk.Tk()
    app = PDFCoordinateFinder(root, pdf_path)
    root.mainloop()

if __name__ == "__main__":
    main() 