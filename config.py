from pathlib import Path

EXPECTED_FIT_COLUMNS = [
        'accumulated_power', 'activity_type', 'cadence', 'distance',
        'enhanced_altitude', 'enhanced_speed', 'fractional_cadence',
        'heart_rate', 'position_lat', 'position_long', 'power', 'stance_time',
        'stance_time_balance', 'stance_time_percent', 'step_length',
        'temperature', 'timestamp', 'vertical_oscillation', 'vertical_ratio',
        'unknown_107', 'unknown_134', 'unknown_135', 'unknown_136',
        'unknown_137', 'unknown_138', 'unknown_140', 'unknown_143',
        'unknown_87', 'unknown_90',
        # teadmill
        'unknown_145', 'unknown_146', 'unknown_147'
]
UNKNOWN_COLUMN_MAP = {
    'unknown_107': 'is_moving', # Boolean
    'unknown_134': 'unknown_134', # Nones
    'unknown_135': 'unknown_135', # Integer
    'unknown_136': 'wrist_heart_rate', # BPM
    'unknown_137': 'stamina_potential', # 0-100
    'unknown_138': 'stamina', # 0-100
    'unknown_140': 'grade_adjusted_pace', # mm/s
    'unknown_143': 'body_battery', # 0-100
    'unknown_145': 'unknown_145', # Integer
    'unknown_146': 'unknown_146', # Nones
    'unknown_147': 'unknown_147', # Nones
    'unknown_87': 'cycle_length', # MM
    'unknown_90': 'performance_condition' # Integer
}

DATA_PATH = Path('data')
GARMIN_FIT_ACTIVITIES_PATH = DATA_PATH / 'garmin_fit_activities'
PARQUET_RUN_ACTIVITIES_PATH = DATA_PATH / 'parquet_run_activities'

PLT_STYLE = 'seaborn-v0_8'

DISTANCE_M_COL = 'distance_m'
ELEVATION_M_COL = 'elevation_m'

DISTANCE_MI_COL = 'distance_mi'
ELEVATION_FT_COL = 'elevation_ft'

LATITUDE_COL = 'position_lat'
LONGITUDE_COL = 'position_long'
ELAPSED_TIME_S_COL = 'elapsed_time_s'

M_TO_KM_MULTIPLIER = 0.001 # Meters to Kilometers
MIPS_TO_MPH_MULTIPLIER = 3600 # Miles per second to Miles per Hour
M_TO_FT_MULTIPLIER = 3.28084 # Meters to Feet
MM_TO_FT_MULTIPLIER = 0.00328084 # Millimeters to Feet
M_TO_MI_MULTIPLIER = 0.000621371 # Meters to Miles
MPS_TO_MPH_MULTIPLIER = 2.23694 # Meters per Second to Miles per Hour
FT_TO_M_MULTIPLIER = 0.3048 # Feet to Meters
