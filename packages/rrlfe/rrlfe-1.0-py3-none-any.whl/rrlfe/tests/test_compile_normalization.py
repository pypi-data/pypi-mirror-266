import sys, os

current_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, target_dir)

from rrlfe import *
from rrlfe import compile_normalization

#@patch('builtins.print')
def test_CompileBkgrnd():
    # does bkgrnd compile?

    '''
    Git Actions build does check out file bkgrnd.cc, but then does not find it at the
    compile step for some reason, even though the path names are apparently correct.
    From some message board comments, this *may* have something to do with the fact
    that the build it with Ubuntu, not this codebase's native MacOS.
    '''

    compile_status = compile_normalization.CompileBkgrnd(module_name="test1",cc_bkgrnd_dir=target_dir+"/src/")

    check = compile_status.run_step()

    assert check==True
