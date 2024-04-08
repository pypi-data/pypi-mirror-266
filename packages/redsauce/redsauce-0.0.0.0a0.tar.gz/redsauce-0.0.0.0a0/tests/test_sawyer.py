import unittest
from unittest.mock import MagicMock, patch, mock_open
import yaml as ym

from redsauce.utility.logging import Sawyer

class Test_Sawyer(unittest.TestCase):
    def setUp(self):
        self.config = ym.dump({
            'sawyer': {
            'version': 1,
            'formatters': {
                'simple': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
                'handlers': {
                    'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'DEBUG',
                    'formatter': 'simple',
                    'stream': 'ext://sys.stdout'
                    }
                },
                'loggers': {
                    'sawyer': {
                    'level': 'DEBUG',
                    'handlers': ['console']
                    }
                }
            }  
        })
        self.on_entry_response = None
        self.on_exit_response = None
        self.on_error_response = None
    def on_entry(self, logger, func_name, **kwargs):
        self.on_entry_response = f'{logger.name} - {func_name} - {kwargs}'
    def on_exit(self, logger, func_name, **kwargs):
        self.on_exit_response = f'{logger.name} - {func_name} - {kwargs}'
    def on_error(self, logger, func_name, **kwargs):
        self.on_error_response = f'{logger.name} - {func_name} - {kwargs}'
    
    def test_Sawyer_loadsOnLoggingDictConfig(self):
        with patch('builtins.open', mock_open(read_data=self.config)) as m:
            sawyer = Sawyer(config_yaml=self.config)
            self.assertIsInstance(sawyer, Sawyer)

    def test_Sawyer_trackDecoratesFunction_safe(self):
        self.on_entry_response, self.on_exit_response, self.on_error_response = None, None, None
        sawyer = Sawyer()
        @sawyer.track('sawyer', on_entry=self.on_entry, on_exit=self.on_exit, on_error=self.on_error)
        def test_func():
            return 1
        self.assertEqual(test_func(), 1)
        self.assertIsNotNone(self.on_entry_response)
        self.assertIsNotNone(self.on_exit_response)
        self.assertIsNone(self.on_error_response)
    
    def test_Sawyer_trackDecoratesFunction_error(self):
        self.on_entry_response, self.on_exit_response, self.on_error_response = None, None, None
        sawyer = Sawyer()
        @sawyer.track('sawyer', on_entry=self.on_entry, on_exit=self.on_exit, on_error=self.on_error)
        def test_func():
            raise Exception('test')
        with self.assertRaises(Exception):
            test_func()
        self.assertIsNotNone(self.on_entry_response)
        self.assertIsNone(self.on_exit_response)
        self.assertIsNotNone(self.on_error_response)
    
    def test_Sawyer_useLogger(self):
        import logging
        sawyer = Sawyer()
        logger = sawyer('sawyer')
        self.assertEqual(logger.name, 'sawyer')
        self.assertIsInstance(logger, logging.Logger)
    

if __name__ == '__main__':
    unittest.main()