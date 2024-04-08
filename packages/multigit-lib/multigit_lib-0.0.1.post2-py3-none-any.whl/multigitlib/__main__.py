# -*- coding: utf-8 -*-

# See https://packaging.python.org/en/latest/specifications/version-specifiers
__version__ = '0.0.1-2'

# Import stuff
import sys

# "local" imports
from .subrepo import Subrepo

def main():
	print('RUNNING MULTIGIT LIB')
	local_subrepo = Subrepo()


if __name__ == '__main__':
	sys.exit(
		main()
	)
