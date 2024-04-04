# try is used here to import this file in setup.py and don't break the setup process
try:
    from .converter import Converter
except ModuleNotFoundError as e:
    print(e)

package_name = 'aixblock_converter'
__version__ = '0.0.1'
