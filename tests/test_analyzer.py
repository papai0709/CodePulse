import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os
from analyzer.test_analyzer import TestAnalyzer

class TestTestAnalyzer(unittest.TestCase):
    """Test cases for TestAnalyzer"""
    
    def setUp(self):
        self.analyzer = TestAnalyzer()
    
    def test_init(self):
        """Test TestAnalyzer initialization"""
        self.assertIsInstance(self.analyzer.supported_languages, dict)
        self.assertIn('python', self.analyzer.supported_languages)
        self.assertIn('javascript', self.analyzer.supported_languages)
    
    @patch('analyzer.test_analyzer.os.walk')
    def test_detect_primary_language_python(self, mock_walk):
        """Test detection of Python as primary language"""
        mock_walk.return_value = [
            ('/repo', ['src'], ['main.py', 'utils.py', 'config.js']),
            ('/repo/src', [], ['app.py', 'models.py'])
        ]
        
        result = self.analyzer._detect_primary_language('/repo')
        self.assertEqual(result, 'python')
    
    @patch('analyzer.test_analyzer.os.walk')
    def test_detect_primary_language_javascript(self, mock_walk):
        """Test detection of JavaScript as primary language"""
        mock_walk.return_value = [
            ('/repo', ['src'], ['index.js', 'app.js', 'main.py']),
            ('/repo/src', [], ['component.jsx', 'utils.ts'])
        ]
        
        result = self.analyzer._detect_primary_language('/repo')
        self.assertEqual(result, 'javascript')
    
    @patch('analyzer.test_analyzer.os.walk')
    def test_detect_primary_language_unknown(self, mock_walk):
        """Test detection when no known languages found"""
        mock_walk.return_value = [
            ('/repo', [], ['README.md', 'LICENSE'])
        ]
        
        result = self.analyzer._detect_primary_language('/repo')
        self.assertEqual(result, 'unknown')
    
    @patch('analyzer.test_analyzer.os.walk')
    def test_find_test_files_python(self, mock_walk):
        """Test finding Python test files"""
        mock_walk.return_value = [
            ('/repo', ['tests'], ['main.py']),
            ('/repo/tests', [], ['test_main.py', 'test_utils.py', '__init__.py'])
        ]
        
        result = self.analyzer._find_test_files('/repo', 'python')
        expected = ['tests/test_main.py', 'tests/test_utils.py']
        
        # Sort both lists for comparison
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)
    
    @patch('analyzer.test_analyzer.os.walk')
    def test_find_test_files_javascript(self, mock_walk):
        """Test finding JavaScript test files"""
        mock_walk.return_value = [
            ('/repo', ['__tests__'], ['index.js']),
            ('/repo/__tests__', [], ['app.test.js', 'utils.spec.js'])
        ]
        
        result = self.analyzer._find_test_files('/repo', 'javascript')
        expected = ['__tests__/app.test.js', '__tests__/utils.spec.js']
        
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)
    
    def test_matches_pattern(self):
        """Test pattern matching for test files"""
        # Test Python patterns
        self.assertTrue(self.analyzer._matches_pattern('test_main.py', 'test_*.py'))
        self.assertTrue(self.analyzer._matches_pattern('main_test.py', '*_test.py'))
        self.assertFalse(self.analyzer._matches_pattern('main.py', 'test_*.py'))
        
        # Test JavaScript patterns
        self.assertTrue(self.analyzer._matches_pattern('app.test.js', '*.test.js'))
        self.assertTrue(self.analyzer._matches_pattern('utils.spec.ts', '*.spec.ts'))
        self.assertFalse(self.analyzer._matches_pattern('app.js', '*.test.js'))
    
    def test_classify_test_type(self):
        """Test classification of test types"""
        # Unit tests
        self.assertEqual(
            self.analyzer._classify_test_type('tests/unit/test_main.py', '/fake/path'),
            'unit'
        )
        
        # Integration tests
        self.assertEqual(
            self.analyzer._classify_test_type('tests/integration/test_api.py', '/fake/path'),
            'integration'
        )
        
        # E2E tests
        self.assertEqual(
            self.analyzer._classify_test_type('tests/e2e/test_selenium.py', '/fake/path'),
            'e2e'
        )
    
    @patch('builtins.open', new_callable=mock_open, read_data='import pytest\nfrom unittest import TestCase')
    def test_detect_test_frameworks(self, mock_file):
        """Test detection of test frameworks"""
        result = self.analyzer._detect_test_frameworks('/fake/test_file.py')
        self.assertIn('pytest', result)
        self.assertIn('unittest', result)
    
    @patch('analyzer.test_analyzer.os.walk')
    def test_find_source_files(self, mock_walk):
        """Test finding source files (excluding tests)"""
        mock_walk.return_value = [
            ('/repo', ['src', 'tests'], ['main.py']),
            ('/repo/src', [], ['app.py', 'utils.py']),
            ('/repo/tests', [], ['test_app.py'])
        ]
        
        # Mock the _find_test_files method to return test files
        with patch.object(self.analyzer, '_find_test_files', return_value=['tests/test_app.py']):
            result = self.analyzer._find_source_files('/repo', 'python')
            expected = ['main.py', 'src/app.py', 'src/utils.py']
            
            result.sort()
            expected.sort()
            self.assertEqual(result, expected)
    
    def test_has_corresponding_test(self):
        """Test checking if source file has corresponding test"""
        test_files = ['tests/test_main.py', 'tests/test_utils.py', 'tests/api_test.py']
        
        self.assertTrue(self.analyzer._has_corresponding_test('src/main.py', test_files))
        self.assertTrue(self.analyzer._has_corresponding_test('src/utils.py', test_files))
        self.assertTrue(self.analyzer._has_corresponding_test('src/api.py', test_files))
        self.assertFalse(self.analyzer._has_corresponding_test('src/config.py', test_files))
    
    def test_is_core_file(self):
        """Test identification of core files"""
        self.assertTrue(self.analyzer._is_core_file('src/main.py'))
        self.assertTrue(self.analyzer._is_core_file('app.py'))
        self.assertTrue(self.analyzer._is_core_file('server.js'))
        self.assertFalse(self.analyzer._is_core_file('utils.py'))
        self.assertFalse(self.analyzer._is_core_file('config.py'))
    
    def test_estimate_coverage(self):
        """Test coverage estimation"""
        # Mock finding source and test files
        with patch.object(self.analyzer, '_find_source_files', return_value=['a.py', 'b.py', 'c.py', 'd.py']):
            with patch.object(self.analyzer, '_find_test_files', return_value=['test_a.py', 'test_b.py']):
                result = self.analyzer._estimate_coverage('/repo', 'python')
                
                # With 2 test files for 4 source files (50% ratio), coverage should be reasonable
                self.assertGreater(result['overall'], 30)
                self.assertLess(result['overall'], 80)
                self.assertIn('line_coverage', result)
                self.assertIn('branch_coverage', result)
    
    def test_generate_test_recommendations_low_coverage(self):
        """Test recommendations for low coverage"""
        structure = {'test_types': {'integration': 0}, 'test_frameworks': []}
        metrics = {'overall': 25}
        
        recommendations = self.analyzer._generate_test_recommendations(structure, metrics)
        
        # Should recommend improving coverage and adding frameworks
        recommendation_types = [rec['type'] for rec in recommendations]
        self.assertIn('critical', recommendation_types)
        self.assertIn('warning', recommendation_types)
    
    def test_generate_test_recommendations_good_coverage(self):
        """Test recommendations for good coverage"""
        structure = {'test_types': {'integration': 5}, 'test_frameworks': ['pytest']}
        metrics = {'overall': 85}
        
        recommendations = self.analyzer._generate_test_recommendations(structure, metrics)
        
        # Should have fewer or no critical recommendations
        critical_recs = [rec for rec in recommendations if rec.get('type') == 'critical']
        self.assertEqual(len(critical_recs), 0)

if __name__ == '__main__':
    unittest.main()