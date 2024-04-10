def compile_gvec_to_python():
    
    import subprocess
    import os
    import gvec_to_python
    import pyccel
    import argparse
    import importlib.metadata
    import argcomplete

    # setup argument parser
    parser = argparse.ArgumentParser(prog='gvec_to_python',
                                     description='3D MHD equilibria from GVEC in Python.')
    
    # version message
    __version__ = importlib.metadata.version("gvec_to_python")
    version_message = f'gvec_to_python {__version__}\n'
    version_message += 'Copyright 2022 (c) T.K. Cheng, F. Hindenlang, S. Possanner | Max Planck Institute for Plasma Physics\n'
    version_message += 'MIT license\n'

    # arguments
    parser.add_argument('-v', '--version', action='version',
                        version=version_message)
    
    parser.add_argument('--language',
                                type=str,
                                metavar='LANGUAGE',
                                help='either "c" (default) or "fortran"',
                                default='c')
    
    parser.add_argument('--compiler',
                                type=str,
                                metavar='COMPILER',
                                help='either "GNU" (default), "intel", "PGI", "nvidia" or the path to a JSON compiler file.',
                                default='GNU')

    parser.add_argument('-d', '--delete',
                                help='remove .f90/.c and .so files (for running pure Python code)',
                                action='store_true')

    parser.add_argument('--verbose',
                                help='call pyccel with --verbose compiler option',
                                action='store_true')
    
    # parse argument
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    kwargs = vars(args)

    libpath = gvec_to_python.__path__[0]
    
    if any([s == ' ' for s in libpath]):
        raise NameError(
            f'gvec-to.python installation path MUST NOT contain blank spaces. Please rename "{libpath}".')

    if kwargs['delete']:

        # (change dir not to be in source path)
        print('\nDeleting .f90/.c and .so files ...')
        subprocess.run(['make',
                        'clean',
                        '-f',
                        os.path.join(libpath, 'Makefile'),
                        ], check=True, cwd=libpath)
        print('Done.')
    
    else:
        # pyccel flags
        flags = '--language=' +  kwargs['language']
        flags += ' --compiler=' + kwargs['compiler']
        
        _li = pyccel.__version__.split('.')
        _num = int(_li[0])*100 + int(_li[1])*10 + int(_li[2])
        if _num >= 180:
            flags += ' --conda-warnings off'
            
        if kwargs['verbose']:
            flags += ' --verbose'
        
        print('\nCompiling gvec-to-python kernels ...')
        subprocess.run(['make', 
                        '-f', 
                        os.path.join(libpath, 'Makefile'),
                        'flags=' + flags,
                        'install_path=' + libpath,
                        ], check=True, cwd=libpath)
        print('Done.')

