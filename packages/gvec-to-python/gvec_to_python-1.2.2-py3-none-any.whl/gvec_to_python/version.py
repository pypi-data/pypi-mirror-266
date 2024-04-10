"""
Module specifying the current version string for gvec_to_python.
"""

__version__ = "1.0.2"

def display_version():
    print(f'gvec_to_python {__version__}\n\
Copyright 2022 (c) T.K. Cheng, F. Hindenlang, S. Possanner | Max Planck Institute for Plasma Physics\n\
MIT license\n\
This is free software, no warranty.')

if __name__ == "__main__":
    display_version()