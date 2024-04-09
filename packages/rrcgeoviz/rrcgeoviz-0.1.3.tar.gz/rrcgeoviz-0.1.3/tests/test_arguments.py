import pytest
from rrcgeoviz.arguments import Arguments

ACCIDENTS_DATA_FILE_PATH = "tests/data_files/small_accidents.csv"
ACCIDENTS_OPTIONS_FILE_PATH = "tests/options_files/test_options_accidents.json"

BAD_DATA_FILE_PATH = "tests/data_files/badly_formatted.csv"
BAD_JSON_FILE_PATH = "tests/options_files/bad_options.json"

NO_COLUMNS_FILE_PATH = "tests/options_files/no_columns.json"
NO_FEATURES_FILE_PATH = "tests/options_files/no_features.json"

BLANK_FILE_PATH = "tests/data_files/blankfile"

RANDOM_SECTIONS_PATH = "tests/options_files/random_sections.json"


def test_pass_not_file_objects():
    with (
        open(ACCIDENTS_DATA_FILE_PATH, "r") as data,
        open(ACCIDENTS_OPTIONS_FILE_PATH, "r") as options,
    ):
        with pytest.raises(TypeError) as wrong_type_error:
            _ = Arguments("not a file type", "not a file type")
        assert str(wrong_type_error.value) == "Wrong file types passed to Arguments."

        with pytest.raises(TypeError) as wrong_type_error:
            _ = Arguments(data, "not a file type")
        assert str(wrong_type_error.value) == "Wrong file types passed to Arguments."

        with pytest.raises(TypeError) as wrong_type_error:
            _ = Arguments("not a file type", options)
        assert str(wrong_type_error.value) == "Wrong file types passed to Arguments."


def test_bad_file_paths():
    with (
        open(BLANK_FILE_PATH, "r") as blank_file,
        open(ACCIDENTS_OPTIONS_FILE_PATH, "r") as options,
    ):
        with pytest.raises(TypeError) as wrong_type_error:
            _ = Arguments(blank_file, options)
        assert str(wrong_type_error.value) == "File is blank."
        with pytest.raises(TypeError) as wrong_type_error:
            _ = Arguments(blank_file, blank_file)
        assert str(wrong_type_error.value) == "File is blank."
        with pytest.raises(TypeError) as wrong_type_error:
            _ = Arguments(options, blank_file)
        assert str(wrong_type_error.value) == "File is blank."


def test_badly_formatted_files():
    with (
        open(BAD_DATA_FILE_PATH, "r") as datafile,
        open(ACCIDENTS_OPTIONS_FILE_PATH, "r") as options_file,
    ):
        with pytest.raises(TypeError) as bad_csv_error:
            _ = Arguments(datafile, options_file)
        assert (
            str(bad_csv_error.value)
            == "Error reading data: tests/data_files/badly_formatted.csv"
        )

    with (
        open(ACCIDENTS_DATA_FILE_PATH, "r") as datafile,
        open(BAD_JSON_FILE_PATH, "r") as options_file,
    ):
        with pytest.raises(TypeError) as bad_csv_error:
            _ = Arguments(datafile, options_file)
        assert (
            str(bad_csv_error.value)
            == "Error reading data: tests/options_files/bad_options.json"
        )


def test_missing_columns_section():
    with (
        open(ACCIDENTS_DATA_FILE_PATH, "r") as datafile,
        open(NO_COLUMNS_FILE_PATH, "r") as no_cols,
    ):
        with pytest.raises(TypeError) as bad_col_error:
            _ = Arguments(datafile, no_cols)
        assert (
            str(bad_col_error.value) == "JSON Config file missing 'columns' dictionary."
        )

    with (
        open(ACCIDENTS_DATA_FILE_PATH, "r") as datafile,
        open(NO_FEATURES_FILE_PATH, "r") as no_features,
    ):
        with pytest.raises(TypeError) as bad_col_error:
            _ = Arguments(datafile, no_features)
        assert str(bad_col_error.value) == "JSON Config file missing 'features' array."


def test_only_correct_json_sections():
    with (
        open(ACCIDENTS_DATA_FILE_PATH, "r") as datafile,
        open(RANDOM_SECTIONS_PATH, "r") as random_file,
    ):
        with pytest.raises(TypeError) as bad_col_error:
            _ = Arguments(datafile, random_file)
        assert (
            str(bad_col_error.value) == "Unrecognized section found in JSON: somerandom"
        )
