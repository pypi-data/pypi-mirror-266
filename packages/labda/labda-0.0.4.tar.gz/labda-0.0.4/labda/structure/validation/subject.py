from enum import StrEnum

import pandera as pr


class Column(StrEnum):
    SUBJECT_ID = "subject_id"
    DATETIME = "datetime"
    WEAR = "wear"
    TIMEDELTA = "timedelta"
    # ---
    VERTICAL_COUNTS = "vertical_counts"
    HORIZONTAL_COUNTS = "horizontal_counts"
    PERPENDICULAR_COUNTS = "perpendicular_counts"
    VM_COUNTS = "vm_counts"
    POSITION = "position"
    STEPS = "steps"
    # ---
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    NSAT_VIEWED = "nsat_viewed"
    NSAT_USED = "nsat_used"
    NSAT_RATIO = "nsat_ratio"
    SNR_VIEWED = "snr_viewed"
    SNR_USED = "snr_used"
    PDOP = "pdop"
    HDOP = "hdop"
    VDOP = "vdop"
    # ---
    DISTANCE = "distance"
    ELEVATION = "elevation"
    SPEED = "speed"
    ACCELERATION = "acceleration"
    DIRECTION = "direction"
    ENVIRONMENT = "environment"
    # ---
    SEGMENT_ID = "segment_id"
    TRIP_ID = "trip_id"
    TRIP_STATUS = "trip_status"
    TRIP_MODE = "trip_mode"
    STATIONARY_ID = "stationary_id"
    # ---
    HEART_RATE = "heart_rate"
    LUX = "lux"
    # ---
    ACTIVITY_INTENSITY = "activity_intensity"


SCHEMA = pr.DataFrameSchema(
    index=pr.Index(
        name=Column.DATETIME,
        dtype="datetime64[ns]",
        description="Datetime in timezone where data was collected.",
    ),
    columns={
        Column.SUBJECT_ID: pr.Column(
            dtype="string",
            description="Unique ID of the subject.",
            required=False,
            nullable=False,
        ),
        Column.WEAR: pr.Column(
            dtype="boolean",
            description="Devices worn or not.",
            required=False,
            nullable=True,
        ),
        Column.TIMEDELTA: pr.Column(
            dtype="timedelta",
            description="Time since last fix.",
            required=False,
            nullable=True,
        ),
        Column.VERTICAL_COUNTS: pr.Column(
            dtype="UInt16",
            description="Vertical counts.",
            required=False,
            nullable=True,
        ),
        Column.HORIZONTAL_COUNTS: pr.Column(
            dtype="UInt16",
            description="Horizontal counts.",
            required=False,
            nullable=True,
        ),
        Column.PERPENDICULAR_COUNTS: pr.Column(
            dtype="UInt16",
            description="Perpendicular counts.",
            required=False,
            nullable=True,
        ),
        Column.VM_COUNTS: pr.Column(
            dtype="Float32",
            description="Vector magnitude based on axes counts.",
            required=False,
            nullable=True,
        ),
        Column.POSITION: pr.Column(
            dtype="category",
            description="Position of subject.",
            required=False,
            nullable=True,
            checks=[
                pr.Check(
                    lambda s: s[s.notna()].isin(
                        [
                            "standing",
                            "sitting",
                            "lying",
                        ]
                    ),
                )
            ],
        ),
        Column.STEPS: pr.Column(
            dtype="UInt16",
            description="Steps since last fix.",
            required=False,
            nullable=True,
        ),
        Column.LATITUDE: pr.Column(
            dtype="Float64",
            description="Latitude in appropriate coordinate system where data was collected.",
            required=False,
            nullable=True,
            # checks=[Check.ge(-90), Check.le(90)],
        ),
        Column.LONGITUDE: pr.Column(
            dtype="Float64",
            description="Longitude in appropriate coordinate system where data was collected.",
            required=False,
            nullable=True,
            # checks=[Check.ge(-180), Check.le(180)],
        ),
        Column.NSAT_VIEWED: pr.Column(
            dtype="UInt8",
            description="Number of satellites viewed by device.",
            required=False,
            nullable=True,
        ),
        Column.NSAT_USED: pr.Column(
            dtype="UInt8",
            description="Number of satellites used by device.",
            required=False,
            nullable=True,
        ),
        Column.NSAT_RATIO: pr.Column(
            dtype="Float32",
            description="Satellites ratio (used/viewed).",
            required=False,
            nullable=True,
        ),
        Column.SNR_VIEWED: pr.Column(
            dtype="UInt16",
            description="Sum of satellites SNR.",
            required=False,
            nullable=True,
        ),
        Column.SNR_USED: pr.Column(
            dtype="UInt16",
            description="Sum of used satellites SNR.",
            required=False,
            nullable=True,
        ),
        Column.PDOP: pr.Column(
            dtype="Float32",
            description="GNSS PDOP (Position of Dilution of Precision).",
            required=False,
            nullable=True,
        ),
        Column.HDOP: pr.Column(
            dtype="Float32",
            description="GNSS HDOP (Horizontal Dilution of Precision).",
            required=False,
            nullable=True,
        ),
        Column.VDOP: pr.Column(
            dtype="Float32",
            description="GNSS VDOP (Vertical Dilution of Precision).",
            required=False,
            nullable=True,
        ),
        Column.ACCELERATION: pr.Column(
            dtype="Float32",
            description="Acceleration in m/s².",
            nullable=True,
            required=False,
        ),
        Column.DIRECTION: pr.Column(
            dtype="Float32",
            description="Direction (bearing) in degrees",
            required=False,
            nullable=True,
        ),
        Column.DISTANCE: pr.Column(
            dtype="Float32",
            description="Distance taken since last fix in metres.",
            required=False,
            nullable=True,
        ),
        Column.ELEVATION: pr.Column(
            dtype="Float32",
            description="Elevation in metres",
            required=False,
            nullable=True,
        ),
        Column.ENVIRONMENT: pr.Column(
            dtype="category",
            description="Type of environment",
            required=False,
            nullable=True,
            checks=[
                pr.Check(
                    lambda s: s[s.notna()].isin(
                        [
                            "indoor",
                            "outdoor",
                            "vehicle",
                            "unknown",
                        ]
                    ),
                )
            ],
        ),
        Column.SPEED: pr.Column(
            dtype="Float32",
            description="Speed in km/h.",
            required=False,
            nullable=True,
        ),
        Column.SEGMENT_ID: pr.Column(
            dtype="UInt32",
            description="ID of segment based on missing data or other criteria.",
            required=False,
            nullable=False,
        ),
        Column.TRIP_ID: pr.Column(
            dtype="UInt16",
            description="ID of trip.",
            required=False,
            nullable=True,
        ),
        Column.TRIP_MODE: pr.Column(
            dtype="category",
            description="Type of transportation mode.",
            required=False,
            nullable=True,
            checks=[
                pr.Check(
                    lambda s: s[s.notna()].isin(
                        [
                            "walk",
                            "run",
                            "walk/run",
                            "bicycle",
                            "scooter",
                            "vehicle",
                            "train",
                        ]
                    ),
                )
            ],
        ),
        Column.TRIP_STATUS: pr.Column(
            dtype="category",
            description="Status of trip",
            required=False,
            nullable=True,
            checks=[
                pr.Check(
                    lambda s: s[s.notna()].isin(
                        [
                            "start",
                            "end",
                            "start-end",
                            "transport",
                            "pause",
                            "stationary",
                        ]
                    ),
                )
            ],
        ),
        Column.STATIONARY_ID: pr.Column(
            dtype="UInt16",
            description="ID of stationary.",
            required=False,
            nullable=True,
        ),
        Column.HEART_RATE: pr.Column(
            dtype="UInt8",
            description="Heart rate in beats per minute.",
            required=False,
            nullable=True,
        ),
        Column.LUX: pr.Column(
            dtype="UInt16",
            description="Ambient light in lux.",
            required=False,
            nullable=True,
        ),
        Column.ACTIVITY_INTENSITY: pr.Column(
            dtype="category",
            description="Intensity of activity.",
            required=False,
            nullable=True,
            checks=[
                pr.Check(
                    lambda s: s[s.notna()].isin(
                        [
                            "sedentary",
                            "light",
                            "moderate",
                            "moderate-vigorous",
                            "vigorous",
                        ]
                    ),
                )
            ],
        ),
    },
    coerce=True,
    strict=False,
)
