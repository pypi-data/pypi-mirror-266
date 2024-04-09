from pandera import Check, Column, DataFrameSchema

# TODO: Maybe just one linkage also for domains (timetable, geometries), information about the subjects etc.
# TODO: Refactor...

SCHEMA = DataFrameSchema(
    columns={
        "subject_id": Column(
            dtype="string",
            description="Unique ID of the dataframe (subject)",
        ),
        "sensor_id": Column(
            dtype="string",
            description="ID of the device (e.g. MAC address, serial number)",
        ),
        "start": Column(
            dtype="datetime64[ns]",
            description="Start time of the recording",
            required=False,
        ),
        "end": Column(
            dtype="datetime64[ns]",
            description="End time of the recording",
            required=False,
        ),
    },
    coerce=True,
)
