# MF4Bridge

**Convert MDF4 files to ASC, CSV, and TRC formats with ease**

MF4Bridge is a user-friendly desktop application designed to convert MDF4 (Measurement Data Format 4) files from CANedge loggers to popular analysis formats used by Vector CANoe/CANalyzer and PEAK PCAN tools.

## Features

### Core Conversion Capabilities
- **MDF4 → CSV**: Convert to comma-separated values for spreadsheet analysis
- **MDF4 → ASC**: Convert to Vector CANoe/CANalyzer ASCII format
- **MDF4 → TRC**: Convert to PEAK PCAN-View trace format

### User Experience
- **Modern GUI**: Clean, intuitive interface built with CustomTkinter
- **Batch Processing**: Convert multiple files simultaneously
- **Real-time Progress**: Live progress tracking with status updates
- **Error Handling**: Clear error messages and validation
- **File Validation**: Automatic MDF4 file validation before conversion

### Technical Features
- **Lossless Conversion**: Preserves all timing and data integrity
- **Encryption Support**: Handles encrypted MDF4 files natively
- **Compression Support**: Processes compressed MDF4 files automatically
- **Large File Support**: Efficiently handles large datasets (100MB+)

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Quick Install
```bash
# Install from PyPI (when available)
pip install mf4bridge

# Or install from source
git clone https://github.com/mf4bridge/mf4bridge.git
cd mf4bridge
pip install -r requirements.txt
python main.py
```

### Dependencies
- `asammdf>=7.0.0` - MDF4 file processing
- `customtkinter>=5.0.0` - Modern GUI components

## Usage

### GUI Application
1. **Launch**: Run `python main.py` or `mf4bridge-gui`
2. **Select Files**: Click "Select MDF4 Files" or drag-and-drop files
3. **Choose Formats**: Check desired output formats (CSV, ASC, TRC)
4. **Set Output**: Select output directory
5. **Convert**: Click "Convert Files" and monitor progress

### File Structure
```
MF4Bridge/
├── main.py              # Application entry point
├── converter_engine.py  # Core conversion logic
├── gui_components.py    # GUI interface
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── setup.py           # Installation setup
└── README.md          # Documentation
```

## Output Formats

### CSV Format
- **Structure**: Timestamp, Channel, ID, DLC, Data
- **Use Case**: Excel analysis, custom processing
- **Compatibility**: Universal spreadsheet applications

### ASC Format
- **Structure**: Vector CANoe/CANalyzer ASCII format
- **Use Case**: CAN bus simulation and replay
- **Compatibility**: Vector tools, CANoe, CANalyzer

### TRC Format
- **Structure**: PEAK PCAN-View trace format
- **Use Case**: CAN message analysis and debugging
- **Compatibility**: PEAK PCAN-View, PCAN tools

## Supported Input Files

- **MDF4 Files**: `.mf4` extension
- **CANedge Data**: Raw CAN/LIN logging data
- **Encrypted Files**: Native support for encrypted MDF4
- **Compressed Files**: Automatic decompression handling

## Technical Specifications

### Performance
- **File Size**: Supports files up to several GB
- **Processing Speed**: Optimized for large datasets
- **Memory Usage**: Efficient streaming processing
- **Threading**: Non-blocking UI with background conversion

### Compatibility
- **Python**: 3.8, 3.9, 3.10, 3.11+
- **Operating Systems**: Windows, macOS, Linux
- **MDF Version**: MDF4 (version 4.00+)

## Development

### Building from Source
```bash
# Clone repository
git clone https://github.com/mf4bridge/mf4bridge.git
cd mf4bridge

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Build executable
pyinstaller --onefile --windowed main.py
```

### Project Structure
- **main.py**: Application entry point
- **converter_engine.py**: Core MDF4 conversion logic
- **gui_components.py**: CustomTkinter GUI implementation
- **utils.py**: Helper functions and utilities

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/mf4bridge/mf4bridge/issues)
- **Documentation**: [Read the Docs](https://mf4bridge.readthedocs.io/)
- **Email**: support@mf4bridge.com

## Changelog

### Version 1.0.0
- Initial release
- Core conversion functionality (CSV, ASC, TRC)
- Modern GUI with CustomTkinter
- Batch processing support
- Real-time progress tracking
- File validation and error handling

## Acknowledgments

- **asammdf**: Excellent MDF4 processing library
- **CustomTkinter**: Modern tkinter theming
- **CANedge**: Inspiration for MDF4 logging workflows

---

**MF4Bridge** - Bridging the gap between MDF4 logging and analysis tools.