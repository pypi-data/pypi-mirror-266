from ..structure.validation.subject import Column

CUT_POINTS = [
    {
        "id": 1,
        "name": "Freedson Adult (1998)",
        "reference": "https://journals.lww.com/acsm-msse/fulltext/1998/05000/calibration_of_the_computer_science_and.21.aspx",
        "sampling_frequency": 60,
        "category": "adult",
        "placement": "hip",
        "required_data": Column.VERTICAL_COUNTS,
        "cut_points": [
            {"name": "sedentary", "max": 99},
            {"name": "light", "max": 1951},
            {"name": "moderate", "max": 5724},
            {"name": "vigorous", "max": 9498},
            {"name": "very_vigorous", "max": float("inf")},
        ],
    },
    {
        "id": 2,
        "name": "Freedson Adult VM3 (2011)",
        "reference": "https://doi.org/10.1016/j.jsams.2011.04.003",
        "sampling_frequency": 60,
        "category": "adult",
        "placement": "hip",
        "required_data": Column.VM_COUNTS,
        "cut_points": [
            {"name": "light", "max": 2689},
            {"name": "moderate", "max": 6166},
            {"name": "vigorous", "max": 9642},
            {"name": "very_vigorous", "max": float("inf")},
        ],
    },
]
