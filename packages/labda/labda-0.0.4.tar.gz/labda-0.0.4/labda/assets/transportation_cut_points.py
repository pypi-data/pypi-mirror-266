from ..structure.validation.subject import Column

CUT_POINTS = [
    {
        "id": 1,
        "name": "Carlson PALMS Validation (2015)",
        "reference": "https://doi.org/10.1249/MSS.0000000000000446",
        "required_data": Column.SPEED,
        "units": "km/h",
        "cut_points": [
            {"name": "walk/run", "max": 9},
            {"name": "bicycle", "max": 35},
            {"name": "vehicle", "max": float("inf")},
        ],
    },
]
