#!/usr/bin/env python3
"""
MF4Bridge Test Suite: Tests for all core functionality
Author: Jayadev Meka Name
Date: 2025-06-28
Version: 1.2
License: MIT
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
import shutil
import csv
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converter_engine import MF4Converter, ConversionError
from utils import (
    validate_file_extension, format_file_size, create_output_directory,
    get_safe_filename, validate_output_directory, check_dependencies
)

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestMF4Converter(unittest.TestCase):
    """Test cases for MF4Converter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = MF4Converter()
        self.progress_messages = []
        
        # Create test MDF4 file
        self.test_mdf4_file = os.path.join(self.temp_dir, "test.mf4")
        self._create_test_mdf4_file()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_test_mdf4_file(self):
        """Create a minimal test MDF4 file"""
        with open(self.test_mdf4_file, 'wb') as f:
            # Write minimal MDF4 header
            f.write(b'MDF     ')  # ID block
            f.write(b'4.10')     # Version
            f.write(b'\x00' * 1000)  # Padding for realistic file size
    
    def _progress_callback(self, message, percentage):
        """Capture progress messages for testing"""
        self.progress_messages.append((message, percentage))
    
    def test_converter_initialization(self):
        """Test converter initialization"""
        converter = MF4Converter(self._progress_callback)
        self.assertIsNotNone(converter)
        self.assertEqual(converter.progress_callback, self._progress_callback)
        
    def test_validate_mdf4_file_valid(self):
        """Test validation of valid MDF4 file"""
        result = self.converter.validate_mdf4_file(self.test_mdf4_file)
        self.assertTrue(result)
        
    def test_validate_mdf4_file_invalid_extension(self):
        """Test validation with invalid extension"""
        invalid_file = os.path.join(self.temp_dir, "test.txt")
        with open(invalid_file, 'w') as f:
            f.write("not an mdf4 file")
        
        result = self.converter.validate_mdf4_file(invalid_file)
        self.assertFalse(result)
        
    def test_validate_mdf4_file_nonexistent(self):
        """Test validation of non-existent file"""
        result = self.converter.validate_mdf4_file("nonexistent.mf4")
        self.assertFalse(result)
        
    def test_validate_mdf4_file_too_small(self):
        """Test validation of file that's too small"""
        small_file = os.path.join(self.temp_dir, "small.mf4")
        with open(small_file, 'wb') as f:
            f.write(b'tiny')
        
        result = self.converter.validate_mdf4_file(small_file)
        self.assertFalse(result)
        
    def test_csv_conversion(self):
        """Test CSV conversion functionality"""
        output_file = os.path.join(self.temp_dir, "output.csv")
        
        # Set up progress callback
        converter = MF4Converter(self._progress_callback)
        
        result = converter.mdf4_to_csv(self.test_mdf4_file, output_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify CSV structure
        with open(output_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertIn('Timestamp', header)
            self.assertIn('ID', header)
            self.assertIn('Data', header)
        
        # Check that progress was reported
        self.assertTrue(len(self.progress_messages) > 0)
        
    def test_asc_conversion(self):
        """Test ASC conversion functionality"""
        output_file = os.path.join(self.temp_dir, "output.asc")
        
        result = self.converter.mdf4_to_asc(self.test_mdf4_file, output_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify ASC structure
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn('base hex timestamps absolute', content)
            self.assertIn('Begin Triggerblock', content)
            self.assertIn('End TriggerBlock', content)
            
    def test_trc_conversion(self):
        """Test TRC conversion functionality"""
        output_file = os.path.join(self.temp_dir, "output.trc")
        
        result = self.converter.mdf4_to_trc(self.test_mdf4_file, output_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify TRC structure
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn(';$FILEVERSION=1.1', content)
            self.assertIn(';$COLUMNS=N,O,T,I', content)
            
    def test_batch_conversion(self):
        """Test batch conversion functionality"""
        # Create additional test files
        test_files = []
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"test_{i}.mf4")
            shutil.copy(self.test_mdf4_file, test_file)
            test_files.append(test_file)
        
        output_dir = os.path.join(self.temp_dir, "output")
        formats = ['csv', 'asc', 'trc']
        
        results = self.converter.batch_convert(test_files, output_dir, formats)
        
        # Verify results structure
        self.assertIn('successful', results)
        self.assertIn('failed', results)
        self.assertIn('summary', results)
        
        # Should have successful conversions
        self.assertTrue(len(results['successful']) > 0)
        
        # Check that output files exist
        for test_file in test_files:
            basename = Path(test_file).stem
            for format_type in formats:
                output_file = os.path.join(output_dir, f"{basename}.{format_type}")
                self.assertTrue(os.path.exists(output_file))
                
    def test_conversion_error_handling(self):
        """Test error handling during conversion"""
        # Try to convert to a read-only directory (should fail gracefully)
        if os.name != 'nt':  # Skip on Windows due to permission model differences
            readonly_dir = os.path.join(self.temp_dir, "readonly")
            os.makedirs(readonly_dir)
            os.chmod(readonly_dir, 0o444)  # Read-only
            
            output_file = os.path.join(readonly_dir, "output.csv")
            result = self.converter.mdf4_to_csv(self.test_mdf4_file, output_file)
            self.assertFalse(result)
            
    def test_demo_data_generation(self):
        """Test demo data generation"""
        messages = self.converter._generate_demo_can_data(100)
        
        self.assertEqual(len(messages), 100)
        
        # Verify message structure
        for msg in messages[:5]:  # Check first 5 messages
            self.assertIn('timestamp', msg)
            self.assertIn('id', msg)
            self.assertIn('data', msg)
            self.assertIn('dlc', msg)
            self.assertIsInstance(msg['data'], list)
            self.assertTrue(1 <= msg['dlc'] <= 8)

class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_validate_file_extension_valid(self):
        """Test file extension validation with valid extensions"""
        self.assertTrue(validate_file_extension("test.mf4", ['.mf4', '.MF4']))
        self.assertTrue(validate_file_extension("test.MDF", ['.mdf', '.MDF']))
        self.assertTrue(validate_file_extension("TEST.MF4", ['.mf4']))
        
    def test_validate_file_extension_invalid(self):
        """Test file extension validation with invalid extensions"""
        self.assertFalse(validate_file_extension("test.txt", ['.mf4', '.MF4']))
        self.assertFalse(validate_file_extension("test", ['.mf4']))
        self.assertFalse(validate_file_extension("test.csv", ['.mf4', '.mdf']))
        
    def test_format_file_size(self):
        """Test file size formatting"""
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(512), "512 B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1536), "1.5 KB")
        self.assertEqual(format_file_size(1048576), "1.0 MB")
        self.assertEqual(format_file_size(1073741824), "1.0 GB")
        
    def test_create_output_directory(self):
        """Test output directory creation"""
        new_dir = os.path.join(self.temp_dir, "new_output")
        
        # Directory shouldn't exist initially
        self.assertFalse(os.path.exists(new_dir))
        
        # Create directory
        result = create_output_directory(new_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
        
        # Should work if directory already exists
        result = create_output_directory(new_dir)
        self.assertTrue(result)
        
    def test_get_safe_filename(self):
        """Test safe filename generation"""
        # Test invalid characters
        self.assertEqual(get_safe_filename("test<>file.txt"), "test__file.txt")
        self.assertEqual(get_safe_filename("test:file|name.txt"), "test_file_name.txt")
        
        # Test empty filename
        self.assertEqual(get_safe_filename(""), "converted_file")
        self.assertEqual(get_safe_filename("   "), "converted_file")
        
        # Test reserved names (Windows)
        self.assertTrue(get_safe_filename("CON.txt").startswith("converted_"))
        self.assertTrue(get_safe_filename("aux.mf4").startswith("converted_"))
        
        # Test long filename
        long_name = "a" * 300 + ".txt"
        safe_name = get_safe_filename(long_name)
        self.assertTrue(len(safe_name) <= 255)
        self.assertTrue(safe_name.endswith(".txt"))
        
    def test_validate_output_directory(self):
        """Test output directory validation"""
        # Test existing writable directory
        validation = validate_output_directory(self.temp_dir)
        self.assertTrue(validation['valid'])
        self.assertTrue(validation['exists'])
        self.assertTrue(validation['writable'])
        
        # Test non-existent directory (should be created)
        new_dir = os.path.join(self.temp_dir, "new_validation_test")
        validation = validate_output_directory(new_dir)
        self.assertTrue(validation['valid'])
        self.assertTrue(validation['exists'])
        self.assertTrue(os.path.exists(new_dir))
        
        # Test file instead of directory
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        validation = validate_output_directory(test_file)
        self.assertFalse(validation['valid'])
        self.assertIn("not a directory", validation['error_message'])
        
    def test_check_dependencies(self):
        """Test dependency checking"""
        deps = check_dependencies()
        
        self.assertIn('required', deps)
        self.assertIn('optional', deps)
        self.assertIn('all_satisfied', deps)
        
        # Built-in modules should be available
        self.assertTrue(deps['required']['tkinter']['available'])
        self.assertTrue(deps['required']['csv']['available'])
        self.assertTrue(deps['required']['threading']['available'])

class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Create multiple test MDF4 files
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"integration_test_{i}.mf4")
            with open(test_file, 'wb') as f:
                f.write(b'MDF     4.10')
                f.write(b'\x00' * 1000)
            self.test_files.append(test_file)
            
    def tearDown(self):
        """Clean up integration test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_full_conversion_workflow(self):
        """Test complete conversion workflow"""
        converter = MF4Converter()
        output_dir = os.path.join(self.temp_dir, "integration_output")
        formats = ['csv', 'asc', 'trc']
        
        # Validate all input files
        for test_file in self.test_files:
            self.assertTrue(converter.validate_mdf4_file(test_file))
        
        # Validate output directory
        validation = validate_output_directory(output_dir)
        self.assertTrue(validation['valid'])
        
        # Perform batch conversion
        results = converter.batch_convert(self.test_files, output_dir, formats)
        
        # Verify results
        self.assertEqual(results['total_files'], len(self.test_files))
        self.assertEqual(results['total_conversions'], len(self.test_files) * len(formats))
        
        # Should have some successful conversions
        self.assertTrue(len(results['successful']) > 0)
        
        # Verify all output files exist and have content
        for test_file in self.test_files:
            basename = Path(test_file).stem
            for format_type in formats:
                output_file = os.path.join(output_dir, f"{basename}.{format_type}")
                self.assertTrue(os.path.exists(output_file))
                self.assertTrue(os.path.getsize(output_file) > 0)
        
        # Verify summary statistics
        summary = results['summary']
        self.assertIn('success_rate', summary)
        self.assertIn('total_messages_processed', summary)
        self.assertIn('formats_breakdown', summary)
        
    def test_error_resilience(self):
        """Test that the system handles errors gracefully"""
        converter = MF4Converter()
        
        # Mix of valid and invalid files
        mixed_files = self.test_files.copy()
        
        # Add invalid file
        invalid_file = os.path.join(self.temp_dir, "invalid.mf4")
        with open(invalid_file, 'w') as f:
            f.write("not a real mdf4 file")
        mixed_files.append(invalid_file)
        
        # Add non-existent file
        mixed_files.append(os.path.join(self.temp_dir, "nonexistent.mf4"))
        
        output_dir = os.path.join(self.temp_dir, "error_test_output")
        results = converter.batch_convert(mixed_files, output_dir, ['csv'])
        
        # Should have some successful and some failed conversions
        self.assertTrue(len(results['successful']) > 0)
        self.assertTrue(len(results['failed']) > 0)
        
        # Should not crash and should provide error information
        self.assertIn('summary', results)
        self.assertTrue(results['summary']['success_rate'] < 100)

class TestPerformance(unittest.TestCase):
    """Performance tests for large-scale operations"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up performance test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_large_demo_data_generation(self):
        """Test performance with large demo datasets"""
        converter = MF4Converter()
        
        import time
        start_time = time.time()
        
        # Generate large demo dataset
        messages = converter._generate_demo_can_data(10000)
        
        generation_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 5 seconds)
        self.assertTrue(generation_time < 5.0)
        self.assertEqual(len(messages), 10000)
        
        # Verify data quality
        timestamps = [msg['timestamp'] for msg in messages]
        self.assertTrue(all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1)))
        
    def test_batch_conversion_performance(self):
        """Test performance of batch conversions"""
        converter = MF4Converter()
        
        # Create multiple test files
        test_files = []
        for i in range(10):
            test_file = os.path.join(self.temp_dir, f"perf_test_{i}.mf4")
            with open(test_file, 'wb') as f:
                f.write(b'MDF     4.10')
                f.write(b'\x00' * 2000)  # Larger files
            test_files.append(test_file)
        
        output_dir = os.path.join(self.temp_dir, "perf_output")
        
        import time
        start_time = time.time()
        
        results = converter.batch_convert(test_files, output_dir, ['csv'])
        
        conversion_time = time.time() - start_time
        
        # Should complete in reasonable time
        self.assertTrue(conversion_time < 30.0)  # 30 seconds max
        
        # Should have reasonable success rate
        success_rate = results['summary']['success_rate']
        self.assertTrue(success_rate > 80)  # At least 80% success

def create_test_suite():
    """Create a comprehensive test suite"""
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTest(unittest.makeSuite(TestMF4Converter))
    suite.addTest(unittest.makeSuite(TestUtilityFunctions))
    suite.addTest(unittest.makeSuite(TestIntegration))
    suite.addTest(unittest.makeSuite(TestPerformance))
    
    return suite

def run_tests():
    """Run all tests with detailed reporting"""
    print("=" * 70)
    print("MF4Bridge Test Suite")
    print("=" * 70)
    
    # Create and run test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback.splitlines()[-1]}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)