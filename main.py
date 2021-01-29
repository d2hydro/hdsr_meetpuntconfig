from meetpuntconfig.config import MeetpuntConfig

import logging
import sys
from pathlib import Path


if sys.version_info[0] < 3:
    raise AssertionError(f"current sys version={sys.version} is too old. Run app with >python3")


def setup_logging():
    """Adds a configured strearm handler to the root logger."""
    LOG_LEVEL = logging.INFO
    LOG_DATE_FORMAT = "%H:%M:%S"
    LOG_FORMAT = "%(asctime)s %(filename)s %(levelname)s %(message)s"

    _logger = logging.getLogger()
    _logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOG_LEVEL)
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)
    return _logger


if __name__ == "__main__":
    logger = setup_logging()

    meetpunt_config = MeetpuntConfig()

    # run checks
    meetpunt_config.check_idmap_sections()
    meetpunt_config.check_ignored_hist_tags()
    meetpunt_config.check_missing_hist_tags()
    meetpunt_config.check_double_idmaps()
    meetpunt_config.hist_tags_to_mpt()
    meetpunt_config.check_missing_pars()
    meetpunt_config.check_hloc_consistency()
    meetpunt_config.check_expar_errors_intloc_missing()
    meetpunt_config.check_expar_missing()
    meetpunt_config.check_exloc_intloc_consistency()
    meetpunt_config.check_timeseries_logic()
    meetpunt_config.check_validation_rules()
    meetpunt_config.check_intpar_expar_consistency()
    meetpunt_config.check_location_set_errors()

    # write excel file
    meetpunt_config.write_excel()

    # write csv files
    meetpunt_config.write_csvs()

    logger.info("shutting down")
