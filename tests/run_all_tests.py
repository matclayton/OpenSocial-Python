import sys
import unittest
import getopt
import getpass
import module_test_runner
import opensocial_tests.client_test

def RunAllTests():
  test_runner = module_test_runner.ModuleTestRunner()
  test_runner.modules = [opensocial_tests.client_test,
                        ]
  test_runner.RunAllTests()
  pass

if __name__ == '__main__':
  RunAllTests()