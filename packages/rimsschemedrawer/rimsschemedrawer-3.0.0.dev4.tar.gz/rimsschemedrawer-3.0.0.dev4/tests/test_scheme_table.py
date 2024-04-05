# Tests for ConfigParser scheme table creation.

import rimsschemedrawer.json_parser as jp
from rimsschemedrawer.utils import term_to_string as tts


def test_ti_new_json(data_path):
    """Return the correct table for the new Ti scheme."""
    json_file = data_path.joinpath("ti_new.json")
    data = jp.json_reader(json_file)

    parser = jp.ConfigParser(data)

    header_exp = [
        "Step",
        "λ (nm)",
        "From (cm⁻¹)",
        "To (cm⁻¹)",
    ]

    table_exp = [
        ["1", "465.777", f"0 ({tts('3F2')})", f"21469.500 ({tts('3G3')})"],
        ["1", "469.498", f"170.150 ({tts('3F3')})", f"21469.500 ({tts('3G3')})"],
        ["1", "474.324", f"386.880 ({tts('3F4')})", f"21469.500 ({tts('3G3')})"],
        ["2", "416.158", f"21469.500 ({tts('3G3')})", f"45498.850 ({tts('3G4')})"],
        ["3", "881.399", f"45498.850 ({tts('3G4')})", "56844.450"],
    ]

    header, table = parser.scheme_table()

    assert header == header_exp
    assert table == table_exp


def test_raised_ground(data_path):
    """Return the correct table for a scheme with a raised ground level."""
    json_file = data_path.joinpath("raised_ground_cm.json")
    data = jp.json_reader(json_file)

    parser = jp.ConfigParser(data)

    header_exp = [
        "Step",
        "λ (nm)",
        "From (cm⁻¹)",
        "To (cm⁻¹)",
        "Forbidden",
        "Strength (s⁻¹)",
    ]

    table_exp = [
        [
            "1",
            "400.262",
            f"1000.000 ({tts('5D0')})",
            f"25983.609 ({tts('5F1')})",
            "",
            "$1.0 \\times 10^{6}$",
        ],
        [
            "2",
            "407.469",
            f"25983.609 ({tts('5F1')})",
            f"50525.354 ({tts('5D2')})",
            "x",
            "",
        ],
        [
            "3",
            "771.908",
            f"50525.354 ({tts('5D2')})",
            f"63480.266 ({tts('AI')})",
            "",
            "$3.0 \\times 10^{5}$",
        ],
    ]

    header, table = parser.scheme_table()

    assert header == header_exp
    assert table == table_exp
