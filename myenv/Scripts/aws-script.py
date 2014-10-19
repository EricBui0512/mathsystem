#!c:\mathsystem\myenv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'aws==0.2.5','console_scripts','aws'
__requires__ = 'aws==0.2.5'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('aws==0.2.5', 'console_scripts', 'aws')()
    )
