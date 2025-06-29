"""
MF4Bridge GUI Components (Standard Tkinter Version)
Fallback GUI using only standard tkinter - no external dependencies
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import List

from converter_engine import MF4Converter
from utils import validate_file_extension, create_output_directory, format_file_size

class MF4BridgeGUI:
    """Main GUI class for MF4Bridge application using standard tkinter"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_styles()
        self.setup_widgets()
        self.converter = MF4Converter(progress_callback=self.update_progress)
        
    def setup_window(self):
        """Configure main window properties"""
        self.root.title("MF4Bridge - MDF4 File Converter")
        self.root.geometry("900x800")  # Increased height to show all buttons
        self.root.minsize(700, 600)    # Increased minimum size
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"900x800+{x}+{y}")
        
        # Configure window icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass  # Ignore if icon file not found
            
    def setup_variables(self):
        """Initialize tkinter variables"""
        self.selected_files = []
        self.output_directory = tk.StringVar()
        
        # Format selection variables
        self.csv_var = tk.BooleanVar(value=True)
        self.asc_var = tk.BooleanVar(value=False)
        self.trc_var = tk.BooleanVar(value=False)
        
        # Progress variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure("Action.TButton", padding=(10, 5))
        style.configure("Primary.TButton", padding=(20, 10), font=("Arial", 12, "bold"))
        
        # Configure frame styles
        style.configure("Card.TFrame", relief="solid", borderwidth=1)
        
    def setup_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Input Section
        self.create_input_section(main_frame)
        
        # Output Section
        self.create_output_section(main_frame)
        
        # Progress Section
        self.create_progress_section(main_frame)
        
        # Action Buttons
        self.create_action_buttons(main_frame)
        
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.LabelFrame(parent, text="", padding="15")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="MF4Bridge",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Convert MDF4 files to ASC, CSV, and TRC formats",
            font=("Arial", 12)
        )
        subtitle_label.pack()
        
    def create_input_section(self, parent):
        """Create file input section"""
        input_frame = ttk.LabelFrame(parent, text="Input Files", padding="15")
        input_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # File selection buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.select_files_btn = ttk.Button(
            button_frame,
            text="Select MDF4 Files",
            command=self.select_files,
            style="Action.TButton"
        )
        self.select_files_btn.pack(side="left", padx=(0, 10))
        
        self.clear_files_btn = ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_files,
            style="Action.TButton"
        )
        self.clear_files_btn.pack(side="left")
        
        # File list with reduced height to fit everything
        list_frame = ttk.Frame(input_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create treeview for file list
        columns = ("File", "Size", "Status")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=4)  # Reduced height
        
        # Configure columns
        self.file_tree.heading("File", text="File Name")
        self.file_tree.heading("Size", text="Size")
        self.file_tree.heading("Status", text="Status")
        
        self.file_tree.column("File", width=400)
        self.file_tree.column("Size", width=100)
        self.file_tree.column("Status", width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Drag and drop label
        self.drop_label = ttk.Label(
            input_frame,
            text="Use 'Select Files' button to choose MDF4 files",
            font=("Arial", 10, "italic")
        )
        self.drop_label.pack()
        
    def create_output_section(self, parent):
        """Create output configuration section"""
        output_frame = ttk.LabelFrame(parent, text="Output Configuration", padding="15")
        output_frame.pack(fill="x", pady=(0, 10))
        
        # Format selection
        format_frame = ttk.LabelFrame(output_frame, text="Output Formats", padding="10")
        format_frame.pack(fill="x", pady=(0, 10))
        
        self.csv_checkbox = ttk.Checkbutton(
            format_frame,
            text="CSV (Comma Separated Values)",
            variable=self.csv_var
        )
        self.csv_checkbox.pack(anchor="w", pady=2)
        
        self.asc_checkbox = ttk.Checkbutton(
            format_frame,
            text="ASC (Vector CANoe/CANalyzer)",
            variable=self.asc_var
        )
        self.asc_checkbox.pack(anchor="w", pady=2)
        
        self.trc_checkbox = ttk.Checkbutton(
            format_frame,
            text="TRC (PEAK PCAN-View)",
            variable=self.trc_var
        )
        self.trc_checkbox.pack(anchor="w", pady=2)
        
        # Output directory selection
        dir_frame = ttk.LabelFrame(output_frame, text="Output Directory", padding="10")
        dir_frame.pack(fill="x")
        
        dir_select_frame = ttk.Frame(dir_frame)
        dir_select_frame.pack(fill="x")
        
        self.dir_entry = ttk.Entry(
            dir_select_frame,
            textvariable=self.output_directory,
            font=("Arial", 10)
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dir_browse_btn = ttk.Button(
            dir_select_frame,
            text="Browse",
            command=self.select_output_directory,
            style="Action.TButton"
        )
        self.dir_browse_btn.pack(side="right")
        
    def create_progress_section(self, parent):
        """Create progress tracking section"""
        progress_frame = ttk.LabelFrame(parent, text="Conversion Progress", padding="15")
        progress_frame.pack(fill="x", pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=("Arial", 10)
        )
        self.status_label.pack()
        
    def create_action_buttons(self, parent):
        """Create action buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))  # Added top padding
        
        # Convert button - make it more prominent
        self.convert_btn = ttk.Button(
            button_frame,
            text="🚀 Convert Files",
            command=self.start_conversion,
            style="Primary.TButton"
        )
        self.convert_btn.pack(side="left", padx=(0, 10), pady=10)
        
        # Status info button
        self.info_btn = ttk.Button(
            button_frame,
            text="ℹ️ About",
            command=self.show_about_info,
            style="Action.TButton"
        )
        self.info_btn.pack(side="left", padx=(0, 10), pady=10)
        
        # Exit button
        self.exit_btn = ttk.Button(
            button_frame,
            text="❌ Exit",
            command=self.root.quit,
            style="Action.TButton"
        )
        self.exit_btn.pack(side="right", pady=10)
        
    def select_files(self):
        """Open file dialog to select MDF4 files"""
        file_types = [
            ("MDF4 files", "*.mf4 *.MF4 *.mdf *.MDF"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select MDF4 Files",
            filetypes=file_types
        )
        
        if files:
            self.add_files(files)
            
    def add_files(self, file_paths):
        """Add files to the file list"""
        for file_path in file_paths:
            if file_path not in self.selected_files:
                # Validate file
                if validate_file_extension(file_path, ['.mf4', '.MF4', '.mdf', '.MDF']):
                    if self.converter.validate_mdf4_file(file_path):
                        self.selected_files.append(file_path)
                        self.update_file_tree()
                    else:
                        messagebox.showwarning(
                            "Invalid File",
                            f"File is not a valid MDF4 file:\n{os.path.basename(file_path)}"
                        )
                else:
                    messagebox.showwarning(
                        "Invalid File Type",
                        f"Please select MDF4 files (.mf4 or .mdf):\n{os.path.basename(file_path)}"
                    )
                    
    def clear_files(self):
        """Clear all selected files"""
        self.selected_files.clear()
        self.update_file_tree()
        
    def update_file_tree(self):
        """Update the file tree display"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # Add current files
        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            file_size = format_file_size(os.path.getsize(file_path))
            
            self.file_tree.insert(
                "",
                "end",
                values=(file_name, file_size, "Ready")
            )
            
    def select_output_directory(self):
        """Open dialog to select output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
            
    def validate_inputs(self) -> bool:
        """Validate user inputs before conversion"""
        if not self.selected_files:
            messagebox.showerror("No Files", "Please select at least one MDF4 file.")
            return False
            
        if not (self.csv_var.get() or self.asc_var.get() or self.trc_var.get()):
            messagebox.showerror("No Format", "Please select at least one output format.")
            return False
            
        if not self.output_directory.get():
            messagebox.showerror("No Output Directory", "Please select an output directory.")
            return False
            
        return True
        
    def get_selected_formats(self) -> List[str]:
        """Get list of selected output formats"""
        formats = []
        if self.csv_var.get():
            formats.append('csv')
        if self.asc_var.get():
            formats.append('asc')
        if self.trc_var.get():
            formats.append('trc')
        return formats
        
    def start_conversion(self):
        """Start the conversion process"""
        if not self.validate_inputs():
            return
            
        # Disable convert button during conversion
        self.convert_btn.configure(state="disabled", text="Converting...")
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting conversion...")
        
        # Create output directory if it doesn't exist
        create_output_directory(self.output_directory.get())
        
        # Start conversion in separate thread
        formats = self.get_selected_formats()
        conversion_thread = threading.Thread(
            target=self.run_conversion,
            args=(self.selected_files, self.output_directory.get(), formats)
        )
        conversion_thread.daemon = True
        conversion_thread.start()
        
    def run_conversion(self, file_list: List[str], output_dir: str, formats: List[str]):
        """Run conversion in background thread"""
        try:
            results = self.converter.batch_convert(file_list, output_dir, formats)
            
            # Update UI in main thread
            self.root.after(0, self.conversion_completed, results)
            
        except Exception as e:
            # Handle conversion error
            error_msg = f"Conversion failed: {str(e)}"
            self.root.after(0, self.conversion_error, error_msg)
            
    def conversion_completed(self, results: dict):
        """Handle conversion completion"""
        # Re-enable convert button
        self.convert_btn.configure(state="normal", text="Convert Files")
        
        # Update progress to 100%
        self.progress_var.set(100)
        
        # Show completion message
        successful = len(results['successful'])
        failed = len(results['failed'])
        total = results['total_conversions']
        
        if failed == 0:
            self.status_var.set(f"Conversion completed successfully! ({successful}/{total})")
            messagebox.showinfo(
                "Conversion Complete",
                f"All conversions completed successfully!\n\n"
                f"Files converted: {successful}\n"
                f"Output directory: {self.output_directory.get()}"
            )
        else:
            self.status_var.set(f"Conversion completed with errors ({successful}/{total} successful)")
            messagebox.showwarning(
                "Conversion Complete with Errors",
                f"Conversion completed with some errors.\n\n"
                f"Successful: {successful}\n"
                f"Failed: {failed}\n"
                f"Total: {total}\n\n"
                f"Output directory: {self.output_directory.get()}"
            )
            
    def conversion_error(self, error_msg: str):
        """Handle conversion error"""
        # Re-enable convert button
        self.convert_btn.configure(state="normal", text="Convert Files")
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Conversion failed")
        
        # Show error message
        messagebox.showerror("Conversion Error", error_msg)
        
    def update_progress(self, message: str, percentage: float):
        """Update progress bar and status (called from converter)"""
        # Update UI in main thread
        self.root.after(0, self._update_progress_ui, message, percentage)
        
    def _update_progress_ui(self, message: str, percentage: float):
        """Update progress UI elements"""
        self.progress_var.set(percentage)
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_about_info(self):
        """Show information about the application"""
        from converter_engine import ASAMMDF_AVAILABLE
        
        if ASAMMDF_AVAILABLE:
            mode_info = "✅ Full Mode - Real MDF4 processing enabled"
        else:
            mode_info = "⚠️ Demo Mode - Generating sample data\n\nTo enable real MDF4 processing:\npython fix_environment.py"
        
        messagebox.showinfo(
            "MF4Bridge Info",
            f"MF4Bridge v1.0\n"
            f"MDF4 File Converter\n\n"
            f"Status: {mode_info}\n\n"
            f"Supported formats:\n"
            f"• CSV - Comma Separated Values\n"
            f"• ASC - Vector CANoe/CANalyzer\n"
            f"• TRC - PEAK PCAN-View"
        )