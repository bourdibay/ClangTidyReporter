
"""
Run clang-tidy on all the C/C++ files in the specified directory.
"""

import os
import subprocess

def generate_output(fd, file: str, compilation_db: str, clang_checks: str, logger):
    path = os.path.normpath(file)
    chunks = path.split(os.sep)
    del chunks[-1]

    logger.info("Run clang-tidy on {0}".format(file))
    fd.write("File scanned: {0}\n".format(file))
    _run_clang_tidy(fd, file, compilation_db, clang_checks, logger)

###############################################################

def _run_clang_tidy(fd, file: str, compilation_db: str, clang_checks: str, logger):
    try:
        cmd = "clang-tidy -extra-arg=\"--std=c++14\" -p {compilation_db} -checks=\"{checks}\" {file}".format(compilation_db=compilation_db,
                                                                                                             checks=clang_checks,
                                                                                                             file=file)
        logger.debug("Run {0}".format(cmd))
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            logger.error(result.stderr.decode('latin1'))
        if result.stdout:
            fd.write(result.stdout.decode('latin1'))
            fd.write("\n")
    except subprocess.CalledProcessError as err:
        logger.error("Exception caught: {0}".format(err))
