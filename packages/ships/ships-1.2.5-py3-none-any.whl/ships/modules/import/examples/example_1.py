

'''
	https://stackoverflow.com/questions/3012473/how-do-i-override-a-python-import
'''


import sys

class custom_importer (object):
    def find_module (self, module_name, package_path):
        return self

    def load_module (self, module_name):
        return self

sys.meta_path.append (custom_importer ())

import example_1_module
print (example_1_module)