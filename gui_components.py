"""
MF4Bridge GUI Components
Unified GUI implementation supporting both standard tkinter and CustomTkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import List, Optional
import logging

# Try to import CustomTkinter for enhanced UI
try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False

from converter_engine import MF4Converter
from utils import (
    validate_file_extension, 
    create_output_directory, 
    format_file_size,
    validate_output_directory
)

logger = logging.getLogger(__name__)

class MF4BridgeGUI:
    """Main GUI class with unified tkinter/CustomTkinter support"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.using_ctk = CTK_AVAILABLE and isinstance(root, (ctk.CTk if CTK_AVAILABLE else type(None)))
        
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        self.converter = MF4Converter(progress_callback=self.update_progress)
        
        logger.info(f"GUI initialized with {'CustomTkinter' if self.using_ctk else 'standard tkinter'}")
        
    def setup_window(self):
        """Configure main window properties"""
        self.root.title("MF4Bridge - MDF4 File Converter")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Center window on screen
        self.center_window()
        
        # Set icon if available
        self.set_window_icon()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 1000
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def set_window_icon(self):
        """Set window icon if available"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # Ignore if icon not found
            
    def setup_variables(self):
        """Initialize variables"""
        self.selected_files = []
        self.output_directory = tk.StringVar()
        
        # Format selection variables
        self.csv_var = tk.BooleanVar(value=True)
        self.asc_var = tk.BooleanVar(value=False)
        self.trc_var = tk.BooleanVar(value=False)
        
        # Progress variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready - Select MDF4 files to begin")
        
    def create_widget(self, widget_type, parent, **kwargs):
        """Create widget with appropriate library (CTK or tkinter)"""
        if self.using_ctk and hasattr(ctk, f"CTk{widget_type}"):
            return getattr(ctk, f"CTk{widget_type}")(parent, **kwargs)
        else:
            # Map CustomTkinter widgets to tkinter equivalents
            widget_map = {
                "Frame": ttk.Frame,
                "Label": ttk.Label,
                "Button": ttk.Button,
                "Entry": ttk.Entry,
                "Checkbox": ttk.Checkbutton,
                "Progressbar": ttk.Progressbar,
                "ScrollableFrame": ttk.Frame  # Fallback for scrollable frame
            }
            widget_class = widget_map.get(widget_type, getattr(ttk, widget_type, tk.Frame))
            return widget_class(parent, **kwargs)
        
    def setup_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        if self.using_ctk:
            main_frame = self.root
            main_frame.grid_rowconfigure(0, weight=1)
            main_frame.grid_columnconfigure(0, weight=1)
            
            # Create scrollable frame for CTK
            scroll_frame = ctk.CTkScrollableFrame(main_frame)
            scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            container = scroll_frame
        else:
            # Create canvas with scrollbar for standard tkinter
            canvas = tk.Canvas(self.root)
            scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
            scroll_frame = ttk.Frame(canvas)
            
            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            scrollbar.pack(side="right", fill="y")
            
            container = scroll_frame
        
        # Create sections
        self.create_header(container)
        self.create_input_section(container)
        self.create_output_section(container)
        self.create_progress_section(container)
        self.create_action_buttons(container)
        
    def create_header(self, parent):
        """Create header section"""
        if self.using_ctk:
            header_frame = ctk.CTkFrame(parent)
            header_frame.pack(fill="x", pady=(0, 20), padx=10)
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="MF4Bridge",
                font=ctk.CTkFont(size=28, weight="bold")
            )
            title_label.pack(pady=15)
            
            subtitle_label = ctk.CTkLabel(
                header_frame,
                text="Convert MDF4 files to ASC, CSV, and TRC formats",
                font=ctk.CTkFont(size=14)
            )
            subtitle_label.pack(pady=(0, 15))
        else:
            header_frame = ttk.LabelFrame(parent, text="", padding="15")
            header_frame.pack(fill="x", pady=(0, 20))
            
            title_label = ttk.Label(
                header_frame,
                text="MF4Bridge",
                font=("Arial", 24, "bold")
            )
            title_label.pack(pady=(0, 5))
            
            subtitle_label = ttk.Label(
                header_frame,
                text="Convert MDF4 files to ASC, CSV, and TRC formats",
                font=("Arial", 12)
            )
            subtitle_label.pack()
        
    def create_input_section(self, parent):
        """Create file input section"""
        if self.using_ctk:
            input_frame = ctk.CTkFrame(parent)
            input_frame.pack(fill="both", expand=True, pady=(0, 15), padx=10)
            
            # Section label
            section_label = ctk.CTkLabel(
                input_frame,
                text="Input Files",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            section_label.pack(pady=(15, 10))
            
        else:
            input_frame = ttk.LabelFrame(parent, text="Input Files", padding="15")
            input_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # File selection buttons
        button_frame = ttk.Frame(input_frame) if not self.using_ctk else ctk.CTkFrame(input_frame)
        button_frame.pack(fill="x", pady=(0, 10), padx=15 if self.using_ctk else 0)
        
        if self.using_ctk:
            self.select_files_btn = ctk.CTkButton(
                button_frame,
                text="📁 Select MDF4 Files",
                command=self.select_files,
                height=35
            )
            self.select_files_btn.pack(side="left", padx=(0, 10), pady=5)
            
            self.clear_files_btn = ctk.CTkButton(
                button_frame,
                text="🗑️ Clear All",
                command=self.clear_files,
                height=35
            )
            self.clear_files_btn.pack(side="left", pady=5)
        else:
            self.select_files_btn = ttk.Button(
                button_frame,
                text="📁 Select MDF4 Files",
                command=self.select_files
            )
            self.select_files_btn.pack(side="left", padx=(0, 10))
            
            self.clear_files_btn = ttk.Button(
                button_frame,
                text="🗑️ Clear All",
                command=self.clear_files
            )
            self.clear_files_btn.pack(side="left")
        
        # File list
        list_frame = ttk.Frame(input_frame) if not self.using_ctk else ctk.CTkFrame(input_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10), padx=15 if self.using_ctk else 0)
        
        # Create file list widget
        if self.using_ctk:
            self.file_listbox = tk.Listbox(list_frame, height=6)
            scrollbar_files = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
            self.file_listbox.configure(yscrollcommand=scrollbar_files.set)
            
            self.file_listbox.pack(side="left", fill="both", expand=True)
            scrollbar_files.pack(side="right", fill="y")
        else:
            # Use treeview for better appearance
            columns = ("File", "Size", "Status")
            self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=6)
            
            self.file_tree.heading("File", text="File Name")
            self.file_tree.heading("Size", text="Size") 
            self.file_tree.heading("Status", text="Status")
            
            self.file_tree.column("File", width=400)
            self.file_tree.column("Size", width=100)
            self.file_tree.column("Status", width=100)
            
            scrollbar_tree = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
            self.file_tree.configure(yscrollcommand=scrollbar_tree.set)
            
            self.file_tree.pack(side="left", fill="both", expand=True)
            scrollbar_tree.pack(side="right", fill="y")
        
    def create_output_section(self, parent):
        """Create output configuration section"""
        if self.using_ctk:
            output_frame = ctk.CTkFrame(parent)
            output_frame.pack(fill="x", pady=(0, 15), padx=10)
            
            section_label = ctk.CTkLabel(
                output_frame,
                text="Output Configuration",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            section_label.pack(pady=(15, 10))
        else:
            output_frame = ttk.LabelFrame(parent, text="Output Configuration", padding="15")
            output_frame.pack(fill="x", pady=(0, 10))
        
        # Format selection
        if self.using_ctk:
            format_frame = ctk.CTkFrame(output_frame)
            format_frame.pack(fill="x", pady=(0, 10), padx=15)
            
            format_label = ctk.CTkLabel(
                format_frame,
                text="Output Formats:",
                font=ctk.CTkFont(weight="bold")
            )
            format_label.pack(pady=(15, 5))
            
            self.csv_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="CSV (Comma Separated Values)",
                variable=self.csv_var
            )
            self.csv_checkbox.pack(pady=5, padx=20, anchor="w")
            
            self.asc_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="ASC (Vector CANoe/CANalyzer)",
                variable=self.asc_var
            )
            self.asc_checkbox.pack(pady=5, padx=20, anchor="w")
            
            self.trc_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="TRC (PEAK PCAN-View)",
                variable=self.trc_var
            )
            self.trc_checkbox.pack(pady=(5, 15), padx=20, anchor="w")
        else:
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
        if self.using_ctk:
            dir_frame = ctk.CTkFrame(output_frame)
            dir_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            dir_label = ctk.CTkLabel(
                dir_frame,
                text="Output Directory:",
                font=ctk.CTkFont(weight="bold")
            )
            dir_label.pack(pady=(15, 5))
            
            dir_select_frame = ctk.CTkFrame(dir_frame)
            dir_select_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            self.dir_entry = ctk.CTkEntry(
                dir_select_frame,
                textvariable=self.output_directory,
                placeholder_text="Select output directory..."
            )
            self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            self.dir_browse_btn = ctk.CTkButton(
                dir_select_frame,
                text="Browse",
                command=self.select_output_directory,
                width=80
            )
            self.dir_browse_btn.pack(side="right")
        else:
            dir_frame = ttk.LabelFrame(output_frame, text="Output Directory", padding="10")
            dir_frame.pack(fill="x")
            
            dir_select_frame = ttk.Frame(dir_frame)
            dir_select_frame.pack(fill="x")
            
            self.dir_entry = ttk.Entry(
                dir_select_frame,
                textvariable=self.output_directory
            )
            self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            self.dir_browse_btn = ttk.Button(
                dir_select_frame,
                text="Browse",
                command=self.select_output_directory
            )
            self.dir_browse_btn.pack(side="right")
        
    def create_progress_section(self, parent):
        """Create progress tracking section"""
        if self.using_ctk:
            progress_frame = ctk.CTkFrame(parent)
            progress_frame.pack(fill="x", pady=(0, 15), padx=10)
            
            section_label = ctk.CTkLabel(
                progress_frame,
                text="Conversion Progress",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            section_label.pack(pady=(15, 10))
            
            self.progress_bar = ctk.CTkProgressBar(progress_frame)
            self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
            self.progress_bar.set(0)
            
            self.status_label = ctk.CTkLabel(
                progress_frame,
                textvariable=self.status_var,
                font=ctk.CTkFont(size=12)
            )
            self.status_label.pack(pady=(0, 15))
        else:
            progress_frame = ttk.LabelFrame(parent, text="Conversion Progress", padding="15")
            progress_frame.pack(fill="x", pady=(0, 10))
            
            self.progress_bar = ttk.Progressbar(
                progress_frame,
                variable=self.progress_var,
                maximum=100,
                mode='determinate'
            )
            self.progress_bar.pack(fill="x", pady=(0, 10))
            
            self.status_label = ttk.Label(
                progress_frame,
                textvariable=self.status_var
            )
            self.status_label.pack()
        
    def create_action_buttons(self, parent):
        """Create action buttons section"""
        if self.using_ctk:
            button_frame = ctk.CTkFrame(parent)
            button_frame.pack(fill="x", pady=(0, 20), padx=10)
            
            # Convert button
            self.convert_btn = ctk.CTkButton(
                button_frame,
                text="🚀 Convert Files",
                command=self.start_conversion,
                height=50,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            self.convert_btn.pack(side="left", padx=(15, 10), pady=15)
            
            # Info button
            self.info_btn = ctk.CTkButton(
                button_frame,
                text="ℹ️ About",
                command=self.show_about_info,
                height=50
            )
            self.info_btn.pack(side="left", padx=(0, 10), pady=15)
            
            # Exit button
            self.exit_btn = ctk.CTkButton(
                button_frame,
                text="❌ Exit",
                command=self.root.quit,
                height=50
            )
            self.exit_btn.pack(side="right", padx=15, pady=15)
        else:
            button_frame = ttk.Frame(parent)
            button_frame.pack(fill="x", pady=(10, 20))
            
            self.convert_btn = ttk.Button(
                button_frame,
                text="🚀 Convert Files",
                command=self.start_conversion
            )
            self.convert_btn.pack(side="left", padx=(0, 10), pady=10)
            
            self.info_btn = ttk.Button(
                button_frame,
                text="ℹ️ About",
                command=self.show_about_info
            )
            self.info_btn.pack(side="left", padx=(0, 10), pady=10)
            
            self.exit_btn = ttk.Button(
                button_frame,
                text="❌ Exit",
                command=self.root.quit
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
        added_count = 0
        for file_path in file_paths:
            if file_path not in self.selected_files:
                if validate_file_extension(file_path, ['.mf4', '.MF4', '.mdf', '.MDF']):
                    if self.converter.validate_mdf4_file(file_path):
                        self.selected_files.append(file_path)
                        added_count += 1
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
        
        if added_count > 0:
            self.update_file_list()
            self.status_var.set(f"Added {added_count} file(s). Total: {len(self.selected_files)} files selected.")
            
    def clear_files(self):
        """Clear all selected files"""
        self.selected_files.clear()
        self.update_file_list()
        self.status_var.set("Ready - Select MDF4 files to begin")
        
    def update_file_list(self):
        """Update the file list display"""
        if self.using_ctk:
            # Clear and update listbox
            self.file_listbox.delete(0, tk.END)
            for file_path in self.selected_files:
                file_name = os.path.basename(file_path)
                file_size = format_file_size(os.path.getsize(file_path))
                display_text = f"{file_name} ({file_size})"
                self.file_listbox.insert(tk.END, display_text)
        else:
            # Clear and update treeview
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            for file_path in self.selected_files:
                file_name = os.path.basename(file_path)
                file_size = format_file_size(os.path.getsize(file_path))
                self.file_tree.insert("", "end", values=(file_name, file_size, "Ready"))
        
    def select_output_directory(self):
        """Open dialog to select output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
            # Validate the selected directory
            validation = validate_output_directory(directory)
            if validation['valid']:
                self.status_var.set(f"Output directory set: {directory}")
            else:
                messagebox.showwarning("Directory Issue", validation['error_message'])
                
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
            
        # Validate output directory
        validation = validate_output_directory(self.output_directory.get())
        if not validation['valid']:
            messagebox.showerror("Invalid Output Directory", validation['error_message'])
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
            
        # Update UI for conversion state
        self.set_conversion_state(True)
        
        # Create output directory if it doesn't exist
        create_output_directory(self.output_directory.get())
        
        # Start conversion in separate thread
        formats = self.get_selected_formats()
        conversion_thread = threading.Thread(
            target=self.run_conversion,
            args=(self.selected_files, self.output_directory.get(), formats),
            daemon=True
        )
        conversion_thread.start()
        
    def set_conversion_state(self, converting: bool):
        """Update UI elements for conversion state"""
        state = "disabled" if converting else "normal"
        
        # Disable/enable buttons
        if hasattr(self, 'convert_btn'):
            if self.using_ctk:
                self.convert_btn.configure(state=state)
                self.convert_btn.configure(text="Converting..." if converting else "🚀 Convert Files")
            else:
                self.convert_btn.configure(state=state)
                self.convert_btn.configure(text="Converting..." if converting else "🚀 Convert Files")
        
        if hasattr(self, 'select_files_btn'):
            if self.using_ctk:
                self.select_files_btn.configure(state=state)
            else:
                self.select_files_btn.configure(state=state)
        
        if hasattr(self, 'clear_files_btn'):
            if self.using_ctk:
                self.clear_files_btn.configure(state=state)
            else:
                self.clear_files_btn.configure(state=state)
        
        if hasattr(self, 'dir_browse_btn'):
            if self.using_ctk:
                self.dir_browse_btn.configure(state=state)
            else:
                self.dir_browse_btn.configure(state=state)
        
        # Reset progress if starting conversion
        if converting:
            if self.using_ctk:
                self.progress_bar.set(0)
            else:
                self.progress_var.set(0)
        
    def run_conversion(self, file_list: List[str], output_dir: str, formats: List[str]):
        """Run conversion in background thread"""
        try:
            results = self.converter.batch_convert(file_list, output_dir, formats)
            
            # Update UI in main thread
            self.root.after(0, self.conversion_completed, results)
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            error_msg = f"Conversion failed: {str(e)}"
            self.root.after(0, self.conversion_error, error_msg)
            
    def conversion_completed(self, results: dict):
        """Handle conversion completion"""
        # Re-enable UI
        self.set_conversion_state(False)
        
        # Update progress to 100%
        if self.using_ctk:
            self.progress_bar.set(1.0)
        else:
            self.progress_var.set(100)
        
        # Show completion message
        successful = len(results['successful'])
        failed = len(results['failed'])
        total = results['total_conversions']
        
        if failed == 0:
            self.status_var.set(f"✅ All conversions completed successfully! ({successful}/{total})")
            messagebox.showinfo(
                "Conversion Complete",
                f"All conversions completed successfully!\n\n"
                f"Files converted: {successful}\n"
                f"Output directory: {self.output_directory.get()}\n\n"
                f"You can now open the output directory to view your converted files."
            )
        else:
            self.status_var.set(f"⚠️ Conversion completed with errors ({successful}/{total} successful)")
            messagebox.showwarning(
                "Conversion Complete with Errors",
                f"Conversion completed with some errors.\n\n"
                f"Successful: {successful}\n"
                f"Failed: {failed}\n"
                f"Total: {total}\n\n"
                f"Output directory: {self.output_directory.get()}\n\n"
                f"Check the log files for error details."
            )
            
    def conversion_error(self, error_msg: str):
        """Handle conversion error"""
        # Re-enable UI
        self.set_conversion_state(False)
        
        # Reset progress
        if self.using_ctk:
            self.progress_bar.set(0)
        else:
            self.progress_var.set(0)
            
        self.status_var.set("❌ Conversion failed")
        
        # Show error message
        messagebox.showerror("Conversion Error", error_msg)
        
    def update_progress(self, message: str, percentage: float):
        """Update progress bar and status (called from converter)"""
        # Update UI in main thread
        self.root.after(0, self._update_progress_ui, message, percentage)
        
    def _update_progress_ui(self, message: str, percentage: float):
        """Update progress UI elements"""
        if self.using_ctk:
            self.progress_bar.set(percentage / 100.0)
        else:
            self.progress_var.set(percentage)
            
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_about_info(self):
        """Show information about the application"""
        from converter_engine import ASAMMDF_AVAILABLE
        
        if ASAMMDF_AVAILABLE:
            mode_info = "✅ Full Mode - Real MDF4 processing enabled"
            features = [
                "✅ Process real MDF4 files from CANedge loggers",
                "✅ Extract actual CAN bus data", 
                "✅ Handle encrypted and compressed files",
                "✅ Support large datasets (100MB+)"
            ]
        else:
            mode_info = "⚠️ Demo Mode - Generating sample data"
            features = [
                "✅ Test all functionality with sample data",
                "✅ Learn the interface and workflow",
                "⚠️ Real MDF4 files won't be processed",
                "📝 Install asammdf to enable real processing"
            ]
        
        feature_text = "\n".join(features)
        
        messagebox.showinfo(
            "About MF4Bridge",
            f"MF4Bridge v1.0\n"
            f"MDF4 File Converter\n\n"
            f"Status: {mode_info}\n\n"
            f"Features:\n{feature_text}\n\n"
            f"Supported Output Formats:\n"
            f"• CSV - Comma Separated Values\n"
            f"• ASC - Vector CANoe/CANalyzer\n"
            f"• TRC - PEAK PCAN-View\n\n"
            f"GUI: {'CustomTkinter' if self.using_ctk else 'Standard Tkinter'}"
        )