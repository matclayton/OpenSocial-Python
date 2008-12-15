
import unittest

class ModuleTestRunner(object):
  
  def __init__(self, module_list=None, module_test_settings=None):
    self.modules = module_list or []
    self.settings = module_test_settings or {}
    
  def RunAllTests(self):
    """Executes all tests present in the list of modules.
    """
    runner = unittest.TextTestRunner()
    for module in self.modules:
      for setting, value in self.settings.iteritems():
        try:
          setattr(module, setting, value)
        except AttributeError:
          pass
      print '\nRunning all tests in module', module.__name__
      runner.run(unittest.defaultTestLoader.loadTestsFromModule(module))