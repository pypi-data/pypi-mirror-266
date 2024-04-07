from subprocess import Popen, PIPE#, check_call, CalledProcessError
import shutil
from . import * # read in config file, basic functions (logging)

class CompileBkgrnd():
    """
    Compile background routine for spectrum normalization, write to file

    Parameters:
        module_name (str): name of module (arbitrary)
        cc_bkgrnd_dir (str): directory containing bkgrnd.cc, and to which binary will be written

    Returns:
        bool: 'True' if compile was successful
    """

    def __init__(self, module_name, cc_bkgrnd_dir):

        self.name = module_name
        self.cc_bkgrnd_dir = cc_bkgrnd_dir

    def run_step(self, attribs = None):

        cc_bkgrnd_file_path_abs = str(self.cc_bkgrnd_dir + "bkgrnd.cc")
        compiled_bkgrnd_file_path_abs = str(self.cc_bkgrnd_dir + "bkgrnd")

        logging.info("## Making directories ##")

        _COMPILE_BKGRND = True
        if _COMPILE_BKGRND:
            if True:

                logging.info("--------------------------")
                logging.info("Compiling background normalization script...")
                bkgrnd_compile = Popen(["g++", "-o",
                                        compiled_bkgrnd_file_path_abs,
                                        cc_bkgrnd_file_path_abs],
                                        stdout=PIPE, stderr=PIPE)

                output, error = bkgrnd_compile.communicate()
                if bkgrnd_compile.returncode != 0:
                    logging.error("Compile error %d %s %s" % (bkgrnd_compile.returncode, output, error))
                    success_val = bool(False)
                else:
                    logging.info("Binary for spectrum normalization saved to")
                    logging.info(compiled_bkgrnd_file_path_abs)
                    logging.info("--------------------------")
                    success_val = bool(True)

        return success_val
