"""
MF4Bridge Enhanced GUI Components
Responsive GUI implementation with improved screen size handling and better UX
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
    validate_output_directory,
    get_system_info
)

logger = logging.getLogger(__name__)

class ResponsiveFrame:
    """Helper class for responsive layout management"""
    
    @staticmethod
    def get_screen_info():
        """Get screen dimensions and scaling info"""
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate DPI scaling
        try:
            dpi = root.winfo_fpixels('1i')
            scaling = dpi / 96.0  # 96 DPI is standard
        except:
            scaling = 1.0
        
        root.destroy()
        
        return {
            'width': screen_width,
            'height': screen_height,
            'scaling': scaling,
            'is_small': screen_width < 1024 or screen_height < 768,
            'is_large': screen_width > 1920,
            'effective_width': int(screen_width / scaling),
            'effective_height': int(screen_height / scaling)
        }
    
    @staticmethod
    def calculate_window_size(screen_info):
        """Calculate optimal window size based on screen"""
        if screen_info['is_small']:
            # Small screens (tablets, small laptops)
            width = min(800, int(screen_info['width'] * 0.9))
            height = min(600, int(screen_info['height'] * 0.85))
        elif screen_info['is_large']:
            # Large screens
            width = min(1200, int(screen_info['width'] * 0.7))
            height = min(900, int(screen_info['height'] * 0.8))
        else:
            # Standard screens
            width = min(1000, int(screen_info['width'] * 0.8))
            height = min(700, int(screen_info['height'] * 0.75))
        
        return width, height

class MF4BridgeGUI:
    """Enhanced GUI class with responsive design and improved UX"""
    
    def __init__(self, root):
        """Initialize the responsive GUI"""
        self.root = root
        self.using_ctk = CTK_AVAILABLE and isinstance(root, (ctk.CTk if CTK_AVAILABLE else type(None)))
        
        # Get screen information for responsive design
        self.screen_info = ResponsiveFrame.get_screen_info()
        logger.info(f"Screen info: {self.screen_info}")
        
        # Initialize variables first
        self.setup_variables()
        
        # Setup window with responsive sizing
        self.setup_responsive_window()
        
        # Create responsive widgets
        self.setup_responsive_widgets()
        
        # Initialize converter
        self.converter = MF4Converter(progress_callback=self.update_progress)
        
        # Setup auto-cleanup
        self.setup_cleanup()
        
        logger.info(f"Responsive GUI initialized with {'CustomTkinter' if self.using_ctk else 'standard tkinter'}")
        
    def setup_variables(self):
        """Initialize all GUI variables"""
        self.selected_files = []
        self.output_directory = tk.StringVar()
        
        # Format selection variables
        self.csv_var = tk.BooleanVar(value=True)
        self.asc_var = tk.BooleanVar(value=False)
        self.trc_var = tk.BooleanVar(value=False)
        
        # Progress variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready - Select MDF4 files to begin")
        
        # Conversion state
        self.is_converting = False
        self.conversion_thread = None
        
    def setup_responsive_window(self):
        """Configure window with responsive sizing"""
        self.root.title("MF4Bridge - MDF4 File Converter")
        
        # Calculate responsive window size
        width, height = ResponsiveFrame.calculate_window_size(self.screen_info)
        
        # Set minimum size based on screen
        min_width = 600 if self.screen_info['is_small'] else 800
        min_height = 500 if self.screen_info['is_small'] else 600
        
        self.root.minsize(min_width, min_height)
        
        # Center window on screen
        x = (self.screen_info['width'] - width) // 2
        y = (self.screen_info['height'] - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Set icon if available
        self.set_window_icon()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def set_window_icon(self):
        """Set window icon if available"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
            
    def get_font_sizes(self):
        """Get responsive font sizes based on screen"""
        if self.screen_info['is_small']:
            return {'title': 20, 'subtitle': 11, 'section': 13, 'normal': 9}
        elif self.screen_info['is_large']:
            return {'title': 32, 'subtitle': 16, 'section': 18, 'normal': 12}
        else:
            return {'title': 28, 'subtitle': 14, 'section': 16, 'normal': 10}
            
    def get_responsive_padding(self):
        """Get responsive padding values"""
        if self.screen_info['is_small']:
            return {'outer': 10, 'inner': 5, 'section': 8}
        elif self.screen_info['is_large']:
            return {'outer': 25, 'inner': 15, 'section': 20}
        else:
            return {'outer': 20, 'inner': 10, 'section': 15}
        
    def setup_responsive_widgets(self):
        """Create responsive widget layout"""
        padding = self.get_responsive_padding()
        fonts = self.get_font_sizes()
        
        # Create main scrollable container
        self.create_scrollable_container(padding)
        
        # Create sections with responsive sizing
        self.create_responsive_header(fonts, padding)
        self.create_responsive_input_section(fonts, padding)
        self.create_responsive_output_section(fonts, padding)
        self.create_responsive_progress_section(fonts, padding)
        self.create_responsive_action_buttons(fonts, padding)
        
    def create_scrollable_container(self, padding):
        """Create scrollable main container"""
        if self.using_ctk:
            # CustomTkinter scrollable frame
            self.scroll_frame = ctk.CTkScrollableFrame(
                self.root,
                corner_radius=0
            )
            self.scroll_frame.grid(row=0, column=0, sticky="nsew", 
                                 padx=padding['outer'], pady=padding['outer'])
            self.scroll_frame.grid_columnconfigure(0, weight=1)
            self.container = self.scroll_frame
        else:
            # Standard tkinter with custom scrollable frame
            self.main_frame = ttk.Frame(self.root)
            self.main_frame.grid(row=0, column=0, sticky="nsew", 
                               padx=padding['outer'], pady=padding['outer'])
            self.main_frame.grid_rowconfigure(0, weight=1)
            self.main_frame.grid_columnconfigure(0, weight=1)
            
            # Create canvas and scrollbar
            self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
            self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
            self.scroll_frame = ttk.Frame(self.canvas)
            
            # Configure scrolling
            self.scroll_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )
            
            self.canvas_frame = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
            
            # Bind mouse wheel
            self.bind_mousewheel()
            
            # Grid layout
            self.canvas.grid(row=0, column=0, sticky="nsew")
            self.v_scrollbar.grid(row=0, column=1, sticky="ns")
            
            self.container = self.scroll_frame
        
        # Configure container for responsive layout
        self.container.grid_columnconfigure(0, weight=1)
        
    def bind_mousewheel(self):
        """Bind mouse wheel scrolling for better UX"""
        def _on_mousewheel(event):
            if not self.using_ctk:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            if not self.using_ctk:
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            if not self.using_ctk:
                self.canvas.unbind_all("<MouseWheel>")
        
        if not self.using_ctk:
            self.canvas.bind('<Enter>', _bind_to_mousewheel)
            self.canvas.bind('<Leave>', _unbind_from_mousewheel)
            
            # Handle canvas resize
            def _configure_scroll_region(event):
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
                # Update canvas window width
                canvas_width = event.width
                self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
            
            self.canvas.bind('<Configure>', _configure_scroll_region)
    
    def create_responsive_header(self, fonts, padding):
        """Create responsive header section"""
        if self.using_ctk:
            header_frame = ctk.CTkFrame(self.container)
            header_frame.grid(row=0, column=0, sticky="ew", pady=(0, padding['section']))
            header_frame.grid_columnconfigure(0, weight=1)
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="MF4Bridge",
                font=ctk.CTkFont(size=fonts['title'], weight="bold")
            )
            title_label.grid(row=0, column=0, pady=(padding['inner'], 5))
            
            subtitle_label = ctk.CTkLabel(
                header_frame,
                text="Convert MDF4 files to ASC, CSV, and TRC formats",
                font=ctk.CTkFont(size=fonts['subtitle'])
            )
            subtitle_label.grid(row=1, column=0, pady=(0, padding['inner']))
        else:
            header_frame = ttk.LabelFrame(self.container, padding=str(padding['inner']))
            header_frame.grid(row=0, column=0, sticky="ew", pady=(0, padding['section']))
            header_frame.grid_columnconfigure(0, weight=1)
            
            title_label = ttk.Label(
                header_frame,
                text="MF4Bridge",
                font=("Arial", fonts['title'], "bold")
            )
            title_label.grid(row=0, column=0, pady=(0, 5))
            
            subtitle_label = ttk.Label(
                header_frame,
                text="Convert MDF4 files to ASC, CSV, and TRC formats",
                font=("Arial", fonts['subtitle'])
            )
            subtitle_label.grid(row=1, column=0)
    
    def create_responsive_input_section(self, fonts, padding):
        """Create responsive file input section"""
        row_num = 1
        
        if self.using_ctk:
            input_frame = ctk.CTkFrame(self.container)
            input_frame.grid(row=row_num, column=0, sticky="ew", pady=(0, padding['section']))
            input_frame.grid_columnconfigure(0, weight=1)
            
            section_label = ctk.CTkLabel(
                input_frame,
                text="Input Files",
                font=ctk.CTkFont(size=fonts['section'], weight="bold")
            )
            section_label.grid(row=0, column=0, pady=(padding['inner'], padding['inner']//2))
        else:
            input_frame = ttk.LabelFrame(self.container, text="Input Files", padding=str(padding['inner']))
            input_frame.grid(row=row_num, column=0, sticky="ew", pady=(0, padding['section']))
            input_frame.grid_columnconfigure(0, weight=1)
        
        # Button frame with responsive layout
        button_frame = ctk.CTkFrame(input_frame) if self.using_ctk else ttk.Frame(input_frame)
        button_frame.grid(row=1, column=0, sticky="ew", pady=(0, padding['inner']))
        button_frame.grid_columnconfigure(2, weight=1)  # Make middle column expand
        
        # Responsive button sizing
        button_height = 35 if not self.screen_info['is_small'] else 30
        
        if self.using_ctk:
            self.select_files_btn = ctk.CTkButton(
                button_frame,
                text="📁 Select MDF4 Files",
                command=self.select_files,
                height=button_height
            )
            self.select_files_btn.grid(row=0, column=0, padx=(0, padding['inner']//2), pady=5, sticky="w")
            
            self.clear_files_btn = ctk.CTkButton(
                button_frame,
                text="🗑️ Clear All",
                command=self.clear_files,
                height=button_height
            )
            self.clear_files_btn.grid(row=0, column=1, pady=5, sticky="w")
            
            # File count label
            self.file_count_label = ctk.CTkLabel(
                button_frame,
                text="No files selected",
                font=ctk.CTkFont(size=fonts['normal'])
            )
            self.file_count_label.grid(row=0, column=3, padx=(padding['inner'], 0), pady=5, sticky="e")
        else:
            self.select_files_btn = ttk.Button(
                button_frame,
                text="📁 Select MDF4 Files",
                command=self.select_files
            )
            self.select_files_btn.grid(row=0, column=0, padx=(0, padding['inner']//2), sticky="w")
            
            self.clear_files_btn = ttk.Button(
                button_frame,
                text="🗑️ Clear All",
                command=self.clear_files
            )
            self.clear_files_btn.grid(row=0, column=1, sticky="w")
            
            # File count label
            self.file_count_label = ttk.Label(
                button_frame,
                text="No files selected",
                font=("Arial", fonts['normal'])
            )
            self.file_count_label.grid(row=0, column=3, padx=(padding['inner'], 0), sticky="e")
        
        # File list with responsive height
        list_height = 4 if self.screen_info['is_small'] else 6
        self.create_file_list(input_frame, list_height, fonts, padding)
    
    def create_file_list(self, parent, height, fonts, padding):
        """Create responsive file list widget"""
        list_frame = ctk.CTkFrame(parent) if self.using_ctk else ttk.Frame(parent)
        list_frame.grid(row=2, column=0, sticky="ew", pady=(0, padding['inner']))
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Use tkinter Treeview for file list functionality
        columns = ("File", "Size", "Status")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=height)
        
        self.file_tree.heading("File", text="File Name")
        self.file_tree.heading("Size", text="Size") 
        self.file_tree.heading("Status", text="Status")
        
        # Responsive column widths
        if self.screen_info['is_small']:
            self.file_tree.column("File", width=250, minwidth=200)
            self.file_tree.column("Size", width=80, minwidth=60)
            self.file_tree.column("Status", width=80, minwidth=60)
        else:
            self.file_tree.column("File", width=400, minwidth=300)
            self.file_tree.column("Size", width=100, minwidth=80)
            self.file_tree.column("Status", width=100, minwidth=80)
        
        scrollbar_tree = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar_tree.set)
        
        self.file_tree.grid(row=0, column=0, sticky="ew")
        scrollbar_tree.grid(row=0, column=1, sticky="ns")
    
    def create_responsive_output_section(self, fonts, padding):
        """Create responsive output configuration section"""
        row_num = 2
        
        if self.using_ctk:
            output_frame = ctk.CTkFrame(self.container)
            output_frame.grid(row=row_num, column=0, sticky="ew", pady=(0, padding['section']))
            output_frame.grid_columnconfigure(0, weight=1)
            
            section_label = ctk.CTkLabel(
                output_frame,
                text="Output Configuration",
                font=ctk.CTkFont(size=fonts['section'], weight="bold")
            )
            section_label.grid(row=0, column=0, pady=(padding['inner'], padding['inner']//2))
        else:
            output_frame = ttk.LabelFrame(self.container, text="Output Configuration", padding=str(padding['inner']))
            output_frame.grid(row=row_num, column=0, sticky="ew", pady=(0, padding['section']))
            output_frame.grid_columnconfigure(0, weight=1)
        
        # Format selection with responsive layout
        if self.screen_info['is_small']:
            # Vertical layout for small screens
            self.create_format_selection_vertical(output_frame, fonts, padding)
        else:
            # Horizontal layout for larger screens
            self.create_format_selection_horizontal(output_frame, fonts, padding)
        
        # Output directory selection
        self.create_directory_selection(output_frame, fonts, padding)
    
    def create_format_selection_vertical(self, parent, fonts, padding):
        """Create vertical format selection for small screens"""
        format_frame = ctk.CTkFrame(parent) if self.using_ctk else ttk.LabelFrame(parent, text="Output Formats")
        format_frame.grid(row=1, column=0, sticky="ew", pady=(0, padding['inner']))
        format_frame.grid_columnconfigure(0, weight=1)
        
        if self.using_ctk:
            format_label = ctk.CTkLabel(
                format_frame,
                text="Output Formats:",
                font=ctk.CTkFont(weight="bold")
            )
            format_label.grid(row=0, column=0, pady=(padding['inner'], 5), sticky="w")
            
            self.csv_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="CSV (Comma Separated Values)",
                variable=self.csv_var
            )
            self.csv_checkbox.grid(row=1, column=0, pady=2, padx=padding['inner'], sticky="w")
            
            self.asc_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="ASC (Vector CANoe/CANalyzer)",
                variable=self.asc_var
            )
            self.asc_checkbox.grid(row=2, column=0, pady=2, padx=padding['inner'], sticky="w")
            
            self.trc_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="TRC (PEAK PCAN-View)",
                variable=self.trc_var
            )
            self.trc_checkbox.grid(row=3, column=0, pady=(2, padding['inner']), padx=padding['inner'], sticky="w")
        else:
            self.csv_checkbox = ttk.Checkbutton(
                format_frame,
                text="CSV (Comma Separated Values)",
                variable=self.csv_var
            )
            self.csv_checkbox.grid(row=0, column=0, sticky="w", pady=2)
            
            self.asc_checkbox = ttk.Checkbutton(
                format_frame,
                text="ASC (Vector CANoe/CANalyzer)",
                variable=self.asc_var
            )
            self.asc_checkbox.grid(row=1, column=0, sticky="w", pady=2)
            
            self.trc_checkbox = ttk.Checkbutton(
                format_frame,
                text="TRC (PEAK PCAN-View)",
                variable=self.trc_var
            )
            self.trc_checkbox.grid(row=2, column=0, sticky="w", pady=2)
    
    def create_format_selection_horizontal(self, parent, fonts, padding):
        """Create horizontal format selection for larger screens"""
        format_frame = ctk.CTkFrame(parent) if self.using_ctk else ttk.LabelFrame(parent, text="Output Formats")
        format_frame.grid(row=1, column=0, sticky="ew", pady=(0, padding['inner']))
        format_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        if self.using_ctk:
            format_label = ctk.CTkLabel(
                format_frame,
                text="Output Formats:",
                font=ctk.CTkFont(weight="bold")
            )
            format_label.grid(row=0, column=0, columnspan=3, pady=(padding['inner'], 5))
            
            self.csv_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="CSV",
                variable=self.csv_var
            )
            self.csv_checkbox.grid(row=1, column=0, pady=5, padx=padding['inner'])
            
            self.asc_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="ASC (Vector)",
                variable=self.asc_var
            )
            self.asc_checkbox.grid(row=1, column=1, pady=5, padx=padding['inner'])
            
            self.trc_checkbox = ctk.CTkCheckBox(
                format_frame,
                text="TRC (PEAK)",
                variable=self.trc_var
            )
            self.trc_checkbox.grid(row=1, column=2, pady=(5, padding['inner']), padx=padding['inner'])
        else:
            checkbox_frame = ttk.Frame(format_frame)
            checkbox_frame.grid(row=0, column=0, sticky="ew")
            checkbox_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            self.csv_checkbox = ttk.Checkbutton(
                checkbox_frame,
                text="CSV",
                variable=self.csv_var
            )
            self.csv_checkbox.grid(row=0, column=0, sticky="w")
            
            self.asc_checkbox = ttk.Checkbutton(
                checkbox_frame,
                text="ASC (Vector)",
                variable=self.asc_var
            )
            self.asc_checkbox.grid(row=0, column=1, sticky="w")
            
            self.trc_checkbox = ttk.Checkbutton(
                checkbox_frame,
                text="TRC (PEAK)",
                variable=self.trc_var
            )
            self.trc_checkbox.grid(row=0, column=2, sticky="w")
    
    def create_directory_selection(self, parent, fonts, padding):
        """Create responsive directory selection"""
        dir_frame = ctk.CTkFrame(parent) if self.using_ctk else ttk.LabelFrame(parent, text="Output Directory")
        dir_frame.grid(row=2, column=0, sticky="ew", pady=(0, padding['inner']))
        dir_frame.grid_columnconfigure(0, weight=1)
        
        if self.using_ctk:
            dir_label = ctk.CTkLabel(
                dir_frame,
                text="Output Directory:",
                font=ctk.CTkFont(weight="bold")
            )
            dir_label.grid(row=0, column=0, pady=(padding['inner'], 5), sticky="w")
            
            dir_select_frame = ctk.CTkFrame(dir_frame)
            dir_select_frame.grid(row=1, column=0, sticky="ew", padx=padding['inner'], pady=(0, padding['inner']))
            dir_select_frame.grid_columnconfigure(0, weight=1)
            
            self.dir_entry = ctk.CTkEntry(
                dir_select_frame,
                textvariable=self.output_directory,
                placeholder_text="Select output directory..."
            )
            self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, padding['inner']//2))
            
            self.dir_browse_btn = ctk.CTkButton(
                dir_select_frame,
                text="Browse",
                command=self.select_output_directory,
                width=80
            )
            self.dir_browse_btn.grid(row=0, column=1)
        else:
            dir_select_frame = ttk.Frame(dir_frame)
            dir_select_frame.grid(row=0, column=0, sticky="ew")
            dir_select_frame.grid_columnconfigure(0, weight=1)
            
            self.dir_entry = ttk.Entry(
                dir_select_frame,
                textvariable=self.output_directory
            )
            self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, padding['inner']//2))
            
            self.dir_browse_btn = ttk.Button(
                dir_select_frame,
                text="Browse",
                command=self.select_output_directory
            )
            self.dir_browse_btn.grid(row=0, column=1)
    
    def create_responsive_progress_section(self, fonts, padding):
        """Create responsive progress section"""
        row_num = 3
        
        if self.using_ctk:
            progress_frame = ctk.CTkFrame(self.container)
            progress_frame.grid(row=row_num, column=0, sticky="ew", pady=(0, padding['section']))
            progress_frame.grid_columnconfigure(0, weight=1)
            
            section_label = ctk.CTkLabel(
                progress_frame,
                text="Conversion Progress",
                font=ctk.CTkFont(size=fonts['section'], weight="bold")
            )
            section_label.grid(row=0, column=0, pady=(padding['inner'], padding['inner']//2))
            
            self.progress_bar = ctk.CTkProgressBar(progress_frame)
            self.progress_bar.grid(row=1, column=0, sticky="ew", padx=padding['inner'], pady=(0, padding['inner']//2))
            self.progress_bar.set(0)
            
            self.status_label = ctk.CTkLabel(
                progress_frame,
                textvariable=self.status_var,
                font=ctk.CTkFont(size=fonts['normal']),
                wraplength=400 if not self.screen_info['is_small'] else 300
            )
            self.status_label.grid(row=2, column=0, pady=(0, padding['inner']))
        else:
            progress_frame = ttk.LabelFrame(self.container, text="Conversion Progress", padding=str(padding['inner']))
            progress_frame.grid(row=row_num, column=0, sticky="ew", pady=(0, padding['section']))
            progress_frame.grid_columnconfigure(0, weight=1)
            
            self.progress_bar = ttk.Progressbar(
                progress_frame,
                variable=self.progress_var,
                maximum=100,
                mode='determinate'
            )
            self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, padding['inner']))
            
            self.status_label = ttk.Label(
                progress_frame,
                textvariable=self.status_var,
                font=("Arial", fonts['normal']),
                wraplength=400 if not self.screen_info['is_small'] else 300
            )
            self.status_label.grid(row=1, column=0)
    
    def create_responsive_action_buttons(self, fonts, padding):
        """Create responsive action buttons"""
        row_num = 4
        
        button_frame = ctk.CTkFrame(self.container) if self.using_ctk else ttk.Frame(self.container)
        button_frame.grid(row=row_num, column=0, sticky="ew", pady=(0, padding['outer']))
        
        # Responsive button layout
        if self.screen_info['is_small']:
            # Vertical layout for small screens
            button_frame.grid_columnconfigure(0, weight=1)
            
            button_height = 40
            button_width = 200
            
            if self.using_ctk:
                self.convert_btn = ctk.CTkButton(
                    button_frame,
                    text="🚀 Convert Files",
                    command=self.start_conversion,
                    height=button_height,
                    width=button_width,
                    font=ctk.CTkFont(size=fonts['normal']+2, weight="bold")
                )
                self.convert_btn.grid(row=0, column=0, pady=padding['inner']//2)
                
                self.info_btn = ctk.CTkButton(
                    button_frame,
                    text="ℹ️ About",
                    command=self.show_about_info,
                    height=button_height,
                    width=button_width
                )
                self.info_btn.grid(row=1, column=0, pady=padding['inner']//2)
                
                self.exit_btn = ctk.CTkButton(
                    button_frame,
                    text="❌ Exit",
                    command=self.on_closing,
                    height=button_height,
                    width=button_width
                )
                self.exit_btn.grid(row=2, column=0, pady=padding['inner']//2)
            else:
                self.convert_btn = ttk.Button(
                    button_frame,
                    text="🚀 Convert Files",
                    command=self.start_conversion
                )
                self.convert_btn.grid(row=0, column=0, pady=padding['inner']//2)
                
                self.info_btn = ttk.Button(
                    button_frame,
                    text="ℹ️ About",
                    command=self.show_about_info
                )
                self.info_btn.grid(row=1, column=0, pady=padding['inner']//2)
                
                self.exit_btn = ttk.Button(
                    button_frame,
                    text="❌ Exit",
                    command=self.on_closing
                )
                self.exit_btn.grid(row=2, column=0, pady=padding['inner']//2)
        else:
            # Horizontal layout for larger screens
            button_frame.grid_columnconfigure(1, weight=1)  # Center space
            
            button_height = 50
            
            if self.using_ctk:
                self.convert_btn = ctk.CTkButton(
                    button_frame,
                    text="🚀 Convert Files",
                    command=self.start_conversion,
                    height=button_height,
                    font=ctk.CTkFont(size=fonts['normal']+2, weight="bold")
                )
                self.convert_btn.grid(row=0, column=0, padx=(0, padding['inner']), pady=padding['inner'])
                
                self.info_btn = ctk.CTkButton(
                    button_frame,
                    text="ℹ️ About",
                    command=self.show_about_info,
                    height=button_height
                )
                self.info_btn.grid(row=0, column=2, padx=(0, padding['inner']), pady=padding['inner'])
                
                self.exit_btn = ctk.CTkButton(
                    button_frame,
                    text="❌ Exit",
                    command=self.on_closing,
                    height=button_height
                )
                self.exit_btn.grid(row=0, column=3, pady=padding['inner'])
            else:
                self.convert_btn = ttk.Button(
                    button_frame,
                    text="🚀 Convert Files",
                    command=self.start_conversion
                )
                self.convert_btn.grid(row=0, column=0, padx=(0, padding['inner']), pady=padding['inner'])
                
                self.info_btn = ttk.Button(
                    button_frame,
                    text="ℹ️ About",
                    command=self.show_about_info
                )
                self.info_btn.grid(row=0, column=2, padx=(0, padding['inner']), pady=padding['inner'])
                
                self.exit_btn = ttk.Button(
                    button_frame,
                    text="❌ Exit",
                    command=self.on_closing
                )
                self.exit_btn.grid(row=0, column=3, pady=padding['inner'])
        
    def select_files(self):
        """Open file dialog to select MDF4 files with improved error handling"""
        try:
            file_types = [
                ("MDF4 files", "*.mf4 *.MF4 *.mdf *.MDF"),
                ("All files", "*.*")
            ]
            
            files = filedialog.askopenfilenames(
                title="Select MDF4 Files",
                filetypes=file_types,
                parent=self.root
            )
            
            if files:
                self.add_files(files)
        except Exception as e:
            logger.error(f"Error in file selection: {e}")
            messagebox.showerror("File Selection Error", f"Could not open file dialog: {str(e)}")
            
    def add_files(self, file_paths):
        """Add files to the file list with improved validation"""
        added_count = 0
        errors = []
        
        try:
            for file_path in file_paths:
                if file_path not in self.selected_files:
                    if validate_file_extension(file_path, ['.mf4', '.MF4', '.mdf', '.MDF']):
                        if self.converter.validate_mdf4_file(file_path):
                            self.selected_files.append(file_path)
                            added_count += 1
                        else:
                            errors.append(f"{os.path.basename(file_path)} - Invalid MDF4 file")
                    else:
                        errors.append(f"{os.path.basename(file_path)} - Invalid file extension")
                else:
                    logger.debug(f"File already selected: {file_path}")
            
            if added_count > 0:
                self.update_file_list()
                self.update_file_count()
                self.status_var.set(f"Added {added_count} file(s). Total: {len(self.selected_files)} files selected.")
            
            if errors:
                error_msg = "Some files could not be added:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    error_msg += f"\n... and {len(errors) - 5} more"
                messagebox.showwarning("File Validation Issues", error_msg)
                
        except Exception as e:
            logger.error(f"Error adding files: {e}")
            messagebox.showerror("Error", f"Error adding files: {str(e)}")
            
    def clear_files(self):
        """Clear all selected files with confirmation"""
        if self.selected_files:
            if messagebox.askyesno("Clear Files", f"Remove all {len(self.selected_files)} selected files?"):
                self.selected_files.clear()
                self.update_file_list()
                self.update_file_count()
                self.status_var.set("Ready - Select MDF4 files to begin")
        
    def update_file_count(self):
        """Update the file count label"""
        count = len(self.selected_files)
        if count == 0:
            text = "No files selected"
        elif count == 1:
            text = "1 file selected"
        else:
            text = f"{count} files selected"
        
        if hasattr(self, 'file_count_label'):
            if self.using_ctk:
                self.file_count_label.configure(text=text)
            else:
                self.file_count_label.config(text=text)
        
    def update_file_list(self):
        """Update the file list display with status information"""
        try:
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # Add files to tree
            for file_path in self.selected_files:
                try:
                    file_name = os.path.basename(file_path)
                    file_size = format_file_size(os.path.getsize(file_path))
                    status = "Ready"
                    
                    self.file_tree.insert("", "end", values=(file_name, file_size, status))
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {e}")
                    self.file_tree.insert("", "end", values=(os.path.basename(file_path), "Error", "Invalid"))
        except Exception as e:
            logger.error(f"Error updating file list: {e}")
        
    def select_output_directory(self):
        """Open dialog to select output directory"""
        try:
            directory = filedialog.askdirectory(
                title="Select Output Directory",
                parent=self.root
            )
            if directory:
                self.output_directory.set(directory)
                validation = validate_output_directory(directory)
                if validation['valid']:
                    self.status_var.set(f"Output directory set: {directory}")
                else:
                    messagebox.showwarning("Directory Issue", validation['error_message'])
        except Exception as e:
            logger.error(f"Error selecting output directory: {e}")
            messagebox.showerror("Directory Selection Error", f"Could not open directory dialog: {str(e)}")
                
    def validate_inputs(self) -> bool:
        """Validate user inputs before conversion with detailed feedback"""
        try:
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
            
            # Check disk space if available
            if validation.get('free_space', 0) > 0:
                estimated_size = len(self.selected_files) * 10 * 1024 * 1024  # Rough estimate: 10MB per file
                if validation['free_space'] < estimated_size:
                    result = messagebox.askyesno(
                        "Low Disk Space",
                        f"Available disk space may be insufficient.\n"
                        f"Available: {format_file_size(validation['free_space'])}\n"
                        f"Estimated needed: {format_file_size(estimated_size)}\n\n"
                        f"Continue anyway?"
                    )
                    if not result:
                        return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating inputs: {e}")
            messagebox.showerror("Validation Error", f"Error validating inputs: {str(e)}")
            return False
        
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
        """Start the conversion process with improved error handling"""
        if self.is_converting:
            messagebox.showwarning("Conversion in Progress", "A conversion is already in progress.")
            return
            
        if not self.validate_inputs():
            return
            
        try:
            # Update UI for conversion state
            self.set_conversion_state(True)
            
            # Create output directory if it doesn't exist
            create_output_directory(self.output_directory.get())
            
            # Start conversion in separate thread
            formats = self.get_selected_formats()
            self.conversion_thread = threading.Thread(
                target=self.run_conversion,
                args=(self.selected_files.copy(), self.output_directory.get(), formats),
                daemon=True
            )
            self.conversion_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting conversion: {e}")
            self.set_conversion_state(False)
            messagebox.showerror("Conversion Error", f"Could not start conversion: {str(e)}")
        
    def set_conversion_state(self, converting: bool):
        """Update UI elements for conversion state"""
        self.is_converting = converting
        state = "disabled" if converting else "normal"
        
        try:
            # Update button states and text
            widgets_to_update = [
                (self.convert_btn, "Converting..." if converting else "🚀 Convert Files"),
                (self.select_files_btn, None),
                (self.clear_files_btn, None),
                (self.dir_browse_btn, None)
            ]
            
            for widget, new_text in widgets_to_update:
                if hasattr(widget, 'configure'):
                    if self.using_ctk:
                        widget.configure(state=state)
                        if new_text:
                            widget.configure(text=new_text)
                    else:
                        widget.configure(state=state)
                        if new_text:
                            widget.configure(text=new_text)
            
            # Reset progress if starting conversion
            if converting:
                if self.using_ctk:
                    self.progress_bar.set(0)
                else:
                    self.progress_var.set(0)
                    
        except Exception as e:
            logger.error(f"Error updating UI state: {e}")
        
    def run_conversion(self, file_list: List[str], output_dir: str, formats: List[str]):
        """Run conversion in background thread with enhanced error handling"""
        try:
            # Update file statuses to "Processing"
            self.root.after(0, self.update_file_statuses, "Processing")
            
            results = self.converter.batch_convert(file_list, output_dir, formats)
            
            # Update UI in main thread
            self.root.after(0, self.conversion_completed, results)
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            error_msg = f"Conversion failed: {str(e)}"
            self.root.after(0, self.conversion_error, error_msg)
    
    def update_file_statuses(self, status: str):
        """Update status for all files in the tree"""
        try:
            for item in self.file_tree.get_children():
                values = list(self.file_tree.item(item, "values"))
                if len(values) >= 3:
                    values[2] = status
                    self.file_tree.item(item, values=values)
        except Exception as e:
            logger.error(f"Error updating file statuses: {e}")
            
    def conversion_completed(self, results: dict):
        """Handle conversion completion with detailed results"""
        try:
            # Re-enable UI
            self.set_conversion_state(False)
            
            # Update progress to 100%
            if self.using_ctk:
                self.progress_bar.set(1.0)
            else:
                self.progress_var.set(100)
            
            # Update file statuses
            self.update_completion_statuses(results)
            
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
                    f"Output directory: {self.output_directory.get()}\n"
                    f"Total size: {format_file_size(results['summary']['total_output_size'])}\n\n"
                    f"You can now open the output directory to view your converted files."
                )
            else:
                self.status_var.set(f"⚠️ Conversion completed with errors ({successful}/{total} successful)")
                
                # Create detailed error message
                error_details = []
                for failed_conv in results['failed'][:3]:  # Show first 3 errors
                    file_name = os.path.basename(failed_conv['input_file'])
                    error_details.append(f"• {file_name}: {failed_conv.get('error', 'Unknown error')}")
                
                error_msg = (
                    f"Conversion completed with some errors.\n\n"
                    f"Successful: {successful}\n"
                    f"Failed: {failed}\n"
                    f"Total: {total}\n\n"
                    f"Output directory: {self.output_directory.get()}\n\n"
                    f"Recent errors:\n" + "\n".join(error_details)
                )
                
                if len(results['failed']) > 3:
                    error_msg += f"\n... and {len(results['failed']) - 3} more errors"
                
                messagebox.showwarning("Conversion Complete with Errors", error_msg)
                
        except Exception as e:
            logger.error(f"Error handling conversion completion: {e}")
            
    def update_completion_statuses(self, results: dict):
        """Update file statuses based on conversion results"""
        try:
            # Create lookup for results
            success_files = {os.path.basename(r['input_file']): r for r in results['successful']}
            failed_files = {os.path.basename(r['input_file']): r for r in results['failed']}
            
            for item in self.file_tree.get_children():
                values = list(self.file_tree.item(item, "values"))
                if len(values) >= 3:
                    file_name = values[0]
                    
                    if file_name in success_files:
                        values[2] = "✅ Complete"
                    elif file_name in failed_files:
                        values[2] = "❌ Failed"
                    else:
                        values[2] = "⚠️ Unknown"
                    
                    self.file_tree.item(item, values=values)
                    
        except Exception as e:
            logger.error(f"Error updating completion statuses: {e}")
            
    def conversion_error(self, error_msg: str):
        """Handle conversion error with cleanup"""
        try:
            # Re-enable UI
            self.set_conversion_state(False)
            
            # Reset progress
            if self.using_ctk:
                self.progress_bar.set(0)
            else:
                self.progress_var.set(0)
                
            self.status_var.set("❌ Conversion failed")
            
            # Update file statuses
            self.update_file_statuses("❌ Error")
            
            # Show error message
            messagebox.showerror("Conversion Error", error_msg)
            
        except Exception as e:
            logger.error(f"Error handling conversion error: {e}")
        
    def update_progress(self, message: str, percentage: float):
        """Update progress bar and status (called from converter)"""
        try:
            # Update UI in main thread
            self.root.after(0, self._update_progress_ui, message, percentage)
        except Exception as e:
            logger.error(f"Error scheduling progress update: {e}")
        
    def _update_progress_ui(self, message: str, percentage: float):
        """Update progress UI elements safely"""
        try:
            if self.using_ctk:
                self.progress_bar.set(percentage / 100.0)
            else:
                self.progress_var.set(percentage)
                
            self.status_var.set(message)
            self.root.update_idletasks()
            
        except Exception as e:
            logger.error(f"Error updating progress UI: {e}")
    
    def show_about_info(self):
        """Show enhanced information about the application"""
        try:
            from converter_engine import ASAMMDF_AVAILABLE
            
            # Get system info
            sys_info = get_system_info()
            
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
            
            about_text = (
                f"MF4Bridge v1.0 Enhanced\n"
                f"MDF4 File Converter\n\n"
                f"Status: {mode_info}\n\n"
                f"Features:\n{feature_text}\n\n"
                f"Supported Output Formats:\n"
                f"• CSV - Comma Separated Values\n"
                f"• ASC - Vector CANoe/CANalyzer\n"
                f"• TRC - PEAK PCAN-View\n\n"
                f"Interface: {'CustomTkinter' if self.using_ctk else 'Standard Tkinter'}\n"
                f"Screen: {self.screen_info['width']}×{self.screen_info['height']}\n"
                f"Platform: {sys_info.get('platform', 'Unknown')}\n"
                f"Memory: {sys_info.get('memory_total_formatted', 'Unknown')}"
            )
            
            messagebox.showinfo("About MF4Bridge Enhanced", about_text)
            
        except Exception as e:
            logger.error(f"Error showing about info: {e}")
            messagebox.showerror("Error", f"Could not display about information: {str(e)}")
    
    def setup_cleanup(self):
        """Setup automatic cleanup and memory management"""
        def cleanup_task():
            try:
                # Clean up temporary files
                from utils import cleanup_temp_files
                cleanup_temp_files()
                
                # Schedule next cleanup in 30 minutes
                self.root.after(30 * 60 * 1000, cleanup_task)
            except Exception as e:
                logger.debug(f"Cleanup task error: {e}")
        
        # Start cleanup task
        self.root.after(5 * 60 * 1000, cleanup_task)  # First cleanup after 5 minutes
    
    def on_closing(self):
        """Handle window closing with cleanup"""
        try:
            # Check if conversion is in progress
            if self.is_converting:
                result = messagebox.askyesno(
                    "Conversion in Progress",
                    "A conversion is currently in progress. Are you sure you want to exit?\n\n"
                    "This will stop the conversion and may leave incomplete files."
                )
                if not result:
                    return
                
                # Cancel conversion if possible
                if hasattr(self.converter, 'cancel_conversion'):
                    self.converter.cancel_conversion()
            
            # Cleanup
            try:
                from utils import cleanup_temp_files
                cleanup_temp_files()
            except Exception as e:
                logger.debug(f"Cleanup on exit failed: {e}")
            
            # Close application
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during application closing: {e}")
            # Force close if cleanup fails
            try:
                self.root.quit()
            except:
                pass