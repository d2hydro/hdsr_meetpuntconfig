"""Runner script for checking consistency HDSR meetpuntconfig."""

from meetpuntconfig.config import MeetpuntConfig

# initieer meetpunt_config
config_json = r"..\config\config.json"
meetpunt_config = MeetpuntConfig(config_json)

# voer tests uit
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

# schrijf naar Excel
meetpunt_config.write_excel()

# schrijf CSV's
meetpunt_config.write_csvs()
