from pathlib import Path

EXPECTED_FIT_COLUMNS = [
    'accumulated_power', # Watts
    'activity_type', # String 'running'
    'cadence', # RPM
    'distance', # Meters
    'enhanced_altitude', # Meters
    'enhanced_speed', # Meters per second
    'fractional_cadence', # RPM
    'heart_rate', # BPM
    'position_lat', # Degrees in semicircles
    'position_long', # Degrees in semicircles
    'power', # Watts
    'stance_time', # Milliseconds
    'stance_time_balance',
    'stance_time_percent',
    'step_length', # Millimeters
    'temperature', # Celsius
    'timestamp', # YYYY-MM-DD HH:MM:SS in UTC
    'vertical_oscillation', # Millimeters
    'vertical_ratio', # Percent
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
    'unknown_137': 'stamina_potential', # Integer 0-100
    'unknown_138': 'stamina', # Integer 0-100
    'unknown_140': 'grade_adjusted_pace', # Millimeters per second
    'unknown_143': 'body_battery', # Integer 0-100
    'unknown_145': 'unknown_145', # Integer
    'unknown_146': 'unknown_146', # Nones
    'unknown_147': 'unknown_147', # Nones
    'unknown_87': 'cycle_length', # Millimeters
    'unknown_90': 'performance_condition' # Integer
}
ADDITIONAL_COLUMNS = [
    'sport',
    'sub_sport',
    'complete_cadence', # SPM
    'elapsed_seconds', # Seconds since start of activity
    'altitude_change', # Meters
    'altitude_gain', # Meters
    'cum_altitude_gain', # Meters
    'gradient',
    'percent_grade', # Percent
    'grade_degrees', # Degrees
    'origin_file_name'
]

M_TO_KM_MULTIPLIER = 0.001 # Meters to Kilometers
MIPS_TO_MPH_MULTIPLIER = 3600 # Miles per second to Miles per Hour
M_TO_FT_MULTIPLIER = 3.28084 # Meters to Feet
MM_TO_FT_MULTIPLIER = 0.00328084 # Millimeters to Feet
M_TO_MI_MULTIPLIER = 0.000621371 # Meters to Miles
MPS_TO_MPH_MULTIPLIER = 2.23694 # Meters per Second to Miles per Hour
FT_TO_M_MULTIPLIER = 0.3048 # Feet to Meters
FT_TO_MI_MULTIPLIER = 5280 # Feet in a Mile
MI_TO_M_MULTIPLIER = 1609.34 # Meters in a Mile
