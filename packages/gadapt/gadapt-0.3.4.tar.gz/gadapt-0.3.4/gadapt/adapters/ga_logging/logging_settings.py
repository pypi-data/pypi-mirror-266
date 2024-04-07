import logging
import os
from os.path import isfile, join
from gadapt.utils.TimeStampFormatter import TimestampFormatter


def init_logging(is_logging: bool):
    """
    Initializes logging for genetic algorithm
    """

    def get_last_num(s: str) -> int:
        try:
            if not s.startswith("log.log"):
                return -1
            if s == "log.log":
                return 0
            s_last_number = s.rsplit(".", 1)[-1]
            n_last_number = int(s_last_number)
            s.rsplit(".", 1)[-1]
            return n_last_number
        except Exception:
            return -1

    if not is_logging:
        logging.disable(logging.INFO)
        return
    path = os.getcwd() + "\log"
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        onlyfiles = [f for f in os.listdir(path) if isfile(join(path, f))]
        onlyfiles.sort(reverse=True, key=get_last_num)
        for f in onlyfiles:
            if f == "log.log":
                try:
                    os.rename(path + "\\" + f, path + "\\" + "log.log.1")
                except Exception:
                    # print("Unable to rename log file: " + path + "\\" + f)
                    # traceback.print_exc()
                    break
            elif f.startswith("log.log."):
                n_last_number = get_last_num(f)
                if n_last_number == -1:
                    continue
                n_last_number += 1
                try:
                    os.rename(path + "\\" + f, path + "\\log.log." + str(n_last_number))
                except Exception:
                    # print("Unable to rename log file: " + path + "\\" + f)
                    # traceback.print_exc()
                    break
    logpath = path + "\log.log"
    logging.basicConfig(filename=logpath, level=logging.INFO)
    logger = logging.getLogger("")
    handler = logging.FileHandler(logpath)
    handler.setFormatter(
        TimestampFormatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
