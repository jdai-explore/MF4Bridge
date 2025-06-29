
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
    print("✓ NumPy working")
except ImportError as e:
    print(f"✗ NumPy not available: {e}")

try:
    import tkinter
    print("✓ tkinter working")
except ImportError as e:
    print(f"✗ tkinter not available: {e}")

try:
    import asammdf
    print(f"asammdf: {asammdf.__version__}")
    print("✓ asammdf working")
except ImportError as e:
    print(f"✗ asammdf not available: {e}")

try:
    import customtkinter
    print(f"customtkinter: {customtkinter.__version__}")
    print("✓ customtkinter working")
except ImportError as e:
    print(f"✗ customtkinter not available: {e}")
