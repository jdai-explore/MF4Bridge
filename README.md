# MF4Bridge

**Professional MDF4 file converter with modern GUI**

MF4Bridge is a robust desktop application designed to convert MDF4 (Measurement Data Format 4) files from CANedge loggers to industry-standard analysis formats used by Vector CANoe/CANalyzer and PEAK PCAN tools.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

## ✨ Features

### Core Conversion Capabilities
- **MDF4 → CSV**: Convert to comma-separated values for spreadsheet analysis
- **MDF4 → ASC**: Convert to Vector CANoe/CANalyzer ASCII format  
- **MDF4 → TRC**: Convert to PEAK PCAN-View trace format

### User Experience
- **Modern GUI**: Clean, responsive interface with CustomTkinter support and standard tkinter fallback
- **Batch Processing**: Convert multiple files and formats simultaneously
- **Real-time Progress**: Live progress tracking with detailed status updates and ETA
- **Smart Error Handling**: Clear error messages and graceful fallbacks
- **File Validation**: Automatic MDF4 file validation before conversion
- **Responsive Design**: Adapts to different screen sizes and resolutions

### Technical Features
- **Lossless Conversion**: Preserves all timing and data integrity
- **Encryption Support**: Handles encrypted MDF4 files natively
- **Compression Support**: Processes compressed MDF4 files automatically
- **Large File Support**: Efficiently handles datasets over 100MB with memory optimization
- **Demo Mode**: Test functionality without real MDF4 files when dependencies are missing

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)

```bash
# Clone or download the repository
git clone <your-repository-url>
cd mf4bridge

# Run the smart setup (automatically detects and fixes issues)
python smart_fix.py

# Launch the application
python main.py
```

### Method 2: Manual Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd mf4bridge

# Install dependencies
pip install asammdf>=7.0.0 'numpy>=1.20.0,<2.0.0' customtkinter>=5.0.0

# Run the application
python main.py
```

### Method 3: Environment Setup Script

```bash
# Run the comprehensive setup script
python setup_environment.py

# Launch the application
python main.py
```

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended for large files)
- **Storage**: 100MB free space for installation
- **Display**: 1024×768 minimum resolution

### Dependencies

**Core Dependencies (Required):**
- `asammdf>=7.0.0` - MDF4 file processing engine
- `numpy>=1.20.0,<2.0.0` - Numerical computations (version constrained for compatibility)

**Optional Dependencies (Enhanced Experience):**
- `customtkinter>=5.0.0` - Enhanced GUI components
- `pandas>=1.5.0,<3.0.0` - Data manipulation support
- `psutil>=5.8.0` - System resource monitoring

**Built-in (No Installation Needed):**
- `tkinter` - GUI framework
- `threading` - Multi-threading support  
- `pathlib` - Modern path operations
- `csv` - CSV file operations

## 🎯 Usage

### GUI Application

1. **Launch**: Run `python main.py`
2. **Select Files**: Click "📁 Select MDF4 Files" or drag files into the interface
3. **Choose Formats**: Check desired output formats (CSV, ASC, TRC)
4. **Set Output**: Select or create an output directory
5. **Convert**: Click "🚀 Convert Files" and monitor progress with ETA

### File Structure
```
MF4Bridge/
├── main.py                    # Application entry point
├── converter_engine.py        # Core conversion logic
├── gui_components.py         # Responsive GUI implementation
├── utils.py                  # Utility functions and helpers
├── setup_environment.py      # Dependency management
├── smart_fix.py              # Automated setup and fixes
├── requirements.txt          # Python dependencies
├── tests/                    # Test suite
│   └── test_mf4bridge.py    # Comprehensive tests
├── logs/                     # Application logs
├── README.md                 # This documentation
└── LICENSE                   # MIT license
```

## 📊 Output Formats

### CSV Format
- **Structure**: Timestamp, Channel, ID, DLC, Data, Data_Hex
- **Use Case**: Excel analysis, custom data processing, Python pandas
- **Compatibility**: Universal spreadsheet applications, data analysis tools

### ASC Format  
- **Structure**: Vector CANoe/CANalyzer ASCII format with proper headers
- **Use Case**: CAN bus simulation, replay, and analysis
- **Compatibility**: Vector CANoe, CANalyzer, CANdb++, Vector tools

### TRC Format
- **Structure**: PEAK PCAN-View trace format with timestamps
- **Use Case**: CAN message analysis, debugging, and visualization
- **Compatibility**: PEAK PCAN-View, PCAN tools, PEAK utilities

## 🔧 Troubleshooting

### Quick Fixes

**🚨 Syntax Errors or Import Failures**
```bash
# Run the smart fix script
python smart_fix.py
```

**⚠️ "Demo Mode" Message**
- **Cause**: asammdf library not installed or incompatible
- **Solution**: Run `python setup_environment.py` or `python smart_fix.py`

**🐍 NumPy Compatibility Errors**
- **Cause**: NumPy 2.x conflicts with asammdf
- **Quick Fix**: `pip install 'numpy>=1.20.0,<2.0.0'`
- **Auto Fix**: `python smart_fix.py`

**🖥️ GUI Not Displaying Properly**
- **Cause**: Missing CustomTkinter or display issues
- **Solution**: Application automatically falls back to standard tkinter
- **Enhancement**: `pip install customtkinter>=5.0.0`

**📁 Permission Errors**
- **Cause**: Insufficient permissions for output directory
- **Solution**: Choose a different output directory (e.g., Desktop, Documents)

### Advanced Troubleshooting

**📊 Performance Issues**
- Large files (>100MB): Application automatically optimizes memory usage
- Multiple files: Use batch processing for better efficiency
- Low memory: Reduce file count per batch

**🔍 Debugging**
1. Check logs in `logs/mf4bridge.log`
2. Run with verbose output: `python main.py --debug` (if implemented)
3. Test with demo data using "Demo Mode"

**🧪 Testing Installation**
```bash
# Run the test suite
python tests/test_mf4bridge.py

# Quick verification
python test_fix.py
```

### Getting Help

1. **Check the logs**: Look in `logs/conversion.log` for detailed error information
2. **Verify setup**: Run `python setup_environment.py --check-only`
3. **Test functionality**: Use demo mode to verify the interface works
4. **Report issues**: Include log files and system information

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone repository
git clone <your-repository-url>
cd mf4bridge

# Set up development environment
python setup_environment.py

# Install development dependencies (optional)
pip install pytest black flake8

# Run tests
python -m pytest tests/

# Run with development logging
python main.py  # Logs automatically saved to logs/
```

### Project Architecture

- **main.py**: Clean application entry point with robust startup logic and error handling
- **converter_engine.py**: Enhanced MDF4 processing with comprehensive error handling and demo mode
- **gui_components.py**: Responsive GUI supporting both CustomTkinter and standard tkinter with adaptive layouts
- **utils.py**: Comprehensive utility functions with logging, validation, and performance monitoring
- **setup_environment.py**: Intelligent dependency management and environment setup
- **smart_fix.py**: Automated problem detection and resolution

### Code Quality

- **Error Handling**: Comprehensive try-catch blocks with meaningful error messages
- **Logging**: Detailed logging for debugging and performance monitoring
- **Testing**: Unit tests covering core functionality
- **Documentation**: Inline documentation and type hints
- **Performance**: Memory optimization for large files and batch processing

## 📈 Version History

### Version 1.1.0 (Current)
- **Fixed**: Critical syntax error in utils.py that prevented application startup
- **Enhanced**: Responsive GUI design that adapts to different screen sizes
- **Improved**: Error handling and user feedback throughout the application
- **Added**: Automated setup and fix scripts (smart_fix.py)
- **Optimized**: Memory usage for large file processing
- **Updated**: Comprehensive logging and debugging capabilities

### Version 1.0.0
- Complete rewrite with enhanced error handling
- Unified GUI supporting CustomTkinter and standard tkinter
- Intelligent dependency management
- Comprehensive logging and validation
- Improved file format support
- Demo mode for testing without real MDF4 files

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper error handling and logging
4. Add tests for new functionality
5. Update documentation as needed
6. Ensure code passes existing tests: `python tests/test_mf4bridge.py`
7. Submit a pull request

### Coding Standards
- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Include comprehensive error handling
- Write tests for new features
- Update documentation for user-facing changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Tools

- **Vector CANoe/CANalyzer**: Professional CAN bus analysis tools
- **PEAK PCAN-View**: CAN message visualization and analysis
- **asammdf**: Python library for MDF file processing
- **CANedge**: CAN bus data loggers that generate MDF4 files

## 📞 Support

- **Documentation**: This README and inline code documentation
- **Issue Tracking**: Use GitHub issues for bug reports and feature requests
- **Logs**: Check `logs/mf4bridge.log` for detailed error information
- **Testing**: Use `test_fix.py` for quick verification of setup

---

**MF4Bridge** - Professional MDF4 conversion made simple and reliable.