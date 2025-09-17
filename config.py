EXPECTED_FIT_COLUMNS = [
    'accumulated_power', 'activity_type', 'cadence', 'distance',
    'enhanced_altitude', 'enhanced_speed', 'fractional_cadence',
    'heart_rate', 'position_lat', 'position_long', 'power', 'stance_time',
    'stance_time_balance', 'stance_time_percent', 'step_length',
    'temperature', 'timestamp', 'vertical_oscillation', 'vertical_ratio'
]

DATA_PATH = '../data/'

PLT_STYLE = 'seaborn-v0_8'


MIPS_TO_MPH_MULTIPLIER = 3600 # Miles per second to Miles per Hour
M_TO_FT_MULTIPLIER = 3.28084 # Meters to Feet
MM_TO_FT_MULTIPLIER = 0.00328084 # Millimeters to Feet
M_TO_MI_MULTIPLIER = 0.000621371 # Meters to Miles
MPS_TO_MPH_MULTIPLIER = 2.23694 # Meters per Second to Miles per Hour
FT_TO_M_MULTIPLIER = 0.3048 # Feet to Meters