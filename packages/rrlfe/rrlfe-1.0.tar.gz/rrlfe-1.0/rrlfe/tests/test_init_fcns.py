from configparser import ConfigParser, ExtendedInterpolation

import sys, os, io

current_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(current_dir, "../"))
print(current_dir)
print(target_dir)
sys.path.insert(0, target_dir)

from rrlfe import *
from conf import *
from configparser import ConfigParser, ExtendedInterpolation
from conf import *

# configuration data for reduction
config_gen = ConfigParser(interpolation=ExtendedInterpolation()) # for parsing values in .init file
# config for reduction to find a, b, c, d
config_gen.read(os.path.join(os.path.dirname(__file__), '../conf', 'config_gen.ini'))

# check if the directory-making function works
def test_make_dir(monkeypatch):

    # loop over directories in reduction config file, make directories,
    # and check they do exist 

    # pre-set stdin to skip over user prompts
    monkeypatch.setattr('sys.stdin', io.StringIO(''))

    for vals in config_gen["data_dirs"]:
        abs_path_name = str(config_gen["data_dirs"][vals])
        make_dir(abs_path_name)
        assert os.path.exists(abs_path_name)


# test if the phase region boundaries are being read in correctly (obsolete)
'''
def test_phase_regions():

    min_good_phase, max_good_phase = phase_regions()

    # is min smaller than max
    assert min_good_phase < max_good_phase

    # are the phases interpreted as floats
    assert isinstance(min_good_phase,float)
'''
    

def test_MakeDirsConfig():

    make_dirs_instance = MakeDirsConfig(module_name="test1")

    check = make_dirs_instance.run_step(attribs = config_gen)

    assert check==True


def test_ConfigInit():

    config_init_instance = ConfigInit(module_name="test1")

    check = config_init_instance.run_step(attribs = config_gen)

    assert check==True
