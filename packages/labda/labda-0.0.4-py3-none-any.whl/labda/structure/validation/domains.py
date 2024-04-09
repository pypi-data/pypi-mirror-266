from pandera import Column, DataFrameSchema

# TODO: Refactor...

SCHEMA = DataFrameSchema(
    columns={
        "subject_id": Column(
            dtype="string",
            description="Unique ID of the dataframe (participant)",
            required=False,
            nullable=True,
        ),
        "domain": Column(
            dtype="string",
            description="Name of the domain",
        ),
        "start": Column(
            dtype="datetime64[ns]",
            description="Start time of the domain",
            required=False,
            nullable=True,
        ),
        "end": Column(
            dtype="datetime64[ns]",
            description="End time of the domain",
            required=False,
            nullable=True,
        ),
        "geometry": Column(
            dtype="geometry",
            description="Geometry of the domain",
            required=False,
            nullable=True,
        ),
    },
    coerce=True,
)
