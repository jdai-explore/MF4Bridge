# MF4Bridge

**Professional MDF4 file converter with modern GUI**

MF4Bridge is a robust desktop application designed to convert MDF4 (Measurement Data Format 4) files from CANedge loggers to industry-standard analysis formats used by Vector CANoe/CANalyzer and PEAK PCAN tools.

## ✨ Features

### Core Conversion Capabilities
- **MDF4 → CSV**: Convert to comma-separated values for spreadsheet analysis
- **MDF4 → ASC**: Convert to Vector CANoe/CANalyzer ASCII format  
- **MDF4 → TRC**: Convert to PEAK PCAN-View trace format

### User Experience
- **Modern GUI**: Clean interface with CustomTkinter support and standard tkinter fallback
- **Batch Processing**: Convert multiple files and formats simultaneously
- **Real-time Progress**: Live progress tracking with detailed status updates
- **Smart Error Handling**: Clear error messages and graceful fallbacks
- **File Validation**: Automatic MDF4 file validation before conversion

### Technical Features
- **Lossless Conversion**: Preserves all timing and data integrity
- **Encryption Support**: Handles encrypted MDF4 files natively
- **Compression Support**: Processes compressed MDF4 files automatically
- **Large File Support**: Efficiently handles datasets over 100MB
- **Demo Mode**: Test functionality without real MDF4 files

## 🚀 Quick Start

### Installation

1. **Download or clone the repository**
   ```bash
   git clone <your-repository-url>
   cd mf4bridge
   ```

2. **Set up the environment (recommended)**
   ```bash
   python setup_environment.py
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

### Alternative Manual Setup

```bash
# Install core dependencies
pip install asammdf>=7.0.0 numpy>=1.20.0,<2.0.0

# Install optional GUI enhancement
pip install customtkinter>=5.0.0

# Run the application
python main.py
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended for large files)
- **Storage**: 100MB free space for installation

### Dependencies

**Required:**
- `asammdf>=7.0.0` - MDF4 file processing engine
- `numpy>=1.20.0,<2.0.0` - Numerical computations (compatibility constrained)

**Optional:**
- `customtkinter>=5.0.0` - Enhanced GUI components
- `pandas>=1.5.0,<3.0.0` - Data manipulation support

**Built-in (no installation needed):**
- `tkinter` - GUI framework
- `threading` - Multi-threading support  
- `pathlib` - Modern path operations
- `csv` - CSV file operations

## 🎯 Usage

### GUI Application

1. **Launch**: Run `python main.py`
2. **Select Files**: Click "Select MDF4 Files" or use the file browser
3. **Choose Formats**: Check desired output formats (CSV, ASC, TRC)
4. **Set Output**: Select or create an output directory
5. **Convert**: Click "Convert Files" and monitor progress

### File Structure
```
MF4Bridge/
├── main.py                    # Application entry point
├── converter_engine.py        # Core conversion logic
├── gui_components.py         # Unified GUI implementation
├── utils.py                  # Utility functions
├── setup_environment.py      # Dependency management
├── requirements.txt          # Python dependencies
├── README.md                 # This documentation
└── LICENSE                   # MIT license
```

## 📊 Output Formats

### CSV Format
- **Structure**: Timestamp, Channel, ID, DLC, Data, Data_Hex
- **Use Case**: Excel analysis, custom data processing
- **Compatibility**: Universal spreadsheet applications, Python pandas

### ASC Format  
- **Structure**: Vector CANoe/CANalyzer ASCII format
- **Use Case**: CAN bus simulation and replay
- **Compatibility**: Vector CANoe, CANalyzer, CANdb++

### TRC Format
- **Structure**: PEAK PCAN-View trace format
- **Use Case**: CAN message analysis and debugging  
- **Compatibility**: PEAK PCAN-View, PCAN tools

## 🔧 Troubleshooting

### Common Issues

**"Demo Mode" Message**
- **Cause**: asammdf library not installed or incompatible
- **Solution**: Run `python setup_environment.py` to fix dependencies

**NumPy Compatibility Errors**
- **Cause**: NumPy 2.x conflicts with asammdf
- **Solution**: The setup script automatically handles this

**GUI Not Displaying Properly**
- **Cause**: Missing CustomTkinter or display issues
- **Solution**: Application automatically falls back to standard tkinter

**Permission Errors**
- **Cause**: Insufficient permissions for output directory
- **Solution**: Choose a different output directory or run with appropriate permissions

### Getting Help

1. **Check the logs**: Look in `logs/conversion.log` for detailed error information
2. **Verify dependencies**: Run `python setup_environment.py --check-only`
3. **Test with demo data**: Use demo mode to verify functionality

## 🛠️ Development

### Building from Source
```bash
# Clone repository
git clone <your-repository-url>
cd mf4bridge

# Set up development environment
python setup_environment.py

# Run tests (if available)
python -m pytest tests/

# Build executable (optional)
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

### Project Structure
- **main.py**: Clean application entry point with robust startup logic
- **converter_engine.py**: Enhanced MDF4 processing with comprehensive error handling
- **gui_components.py**: Unified GUI supporting both CustomTkinter and standard tkinter
- **utils.py**: Comprehensive utility functions with logging and validation
- **setup_environment.py**: Intelligent dependency management and environment setup

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper error handling and logging
4. Add tests if applicable
5. Update documentation as needed
6. Submit a pull request

## 📈 Version History

### Version 1.0.0
- Complete rewrite with enhanced error handling
- Unified GUI supporting CustomTkinter and standard tkinter
- Intelligent dependency management
- Comprehensive logging and validation
- Improved file format support
- Demo mode for testing without real MDF4 files

---

**MF4Bridge** - Professional MDF4 conversion made simple.