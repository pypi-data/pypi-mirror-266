import os
from . import policyapp, singlepageapp

def get_template_dirs():
    """
    Template search paths..
    """
    thisdir = os.path.dirname(os.path.abspath(__file__))
    return [
        os.path.join(thisdir, 'sharedapp', 'templates'),
        os.path.join(thisdir, 'policyapp', 'templates'),
        os.path.join(thisdir, 'singlepageapp', 'templates')
    ]
