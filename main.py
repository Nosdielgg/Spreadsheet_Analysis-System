
"""
Spreadsheet Analysis System
A complete desktop application for Excel/CSV data processing and analysis
"""

from src.gui import SpreadsheetApplication
import tkinter as tk

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = SpreadsheetApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
