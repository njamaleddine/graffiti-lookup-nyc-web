from graffiti_data_pipeline.geocode.sanitize import (
    get_ordinal_suffix,
    normalize_street_name,
)


class TestGetOrdinalSuffix:
    def test_returns_1st_for_number_1(self):
        assert get_ordinal_suffix(1) == "1ST"

    def test_returns_2nd_for_number_2(self):
        assert get_ordinal_suffix(2) == "2ND"

    def test_returns_3rd_for_number_3(self):
        assert get_ordinal_suffix(3) == "3RD"

    def test_returns_th_suffix_for_numbers_4_through_10(self):
        assert get_ordinal_suffix(4) == "4TH"
        assert get_ordinal_suffix(5) == "5TH"
        assert get_ordinal_suffix(10) == "10TH"

    def test_returns_th_suffix_for_11_12_13_as_special_cases(self):
        assert get_ordinal_suffix(11) == "11TH"
        assert get_ordinal_suffix(12) == "12TH"
        assert get_ordinal_suffix(13) == "13TH"

    def test_returns_st_nd_rd_for_21_22_23(self):
        assert get_ordinal_suffix(21) == "21ST"
        assert get_ordinal_suffix(22) == "22ND"
        assert get_ordinal_suffix(23) == "23RD"

    def test_returns_th_suffix_for_111_112_113_as_special_cases(self):
        assert get_ordinal_suffix(111) == "111TH"
        assert get_ordinal_suffix(112) == "112TH"
        assert get_ordinal_suffix(113) == "113TH"

    def test_converts_string_input_to_integer_before_processing(self):
        assert get_ordinal_suffix("5") == "5TH"


class TestNormalizeStreetName:
    def test_does_not_ordinalize_house_number_with_dash(self):
        # Should not ordinalize house numbers like 21-83
        assert (
            normalize_street_name("22-44 WILLOW STREET, BRONX")
            == "22-44 WILLOW STREET, BRONX"
        )

    def test_converts_3_street_to_3rd_street(self):
        assert normalize_street_name("3 STREET") == "3RD STREET"

    def test_converts_5_avenue_to_5th_avenue(self):
        assert normalize_street_name("5 AVENUE") == "5TH AVENUE"

    def test_handles_abbreviated_street_type_st(self):
        assert normalize_street_name("3 ST") == "3RD ST"

    def test_handles_abbreviated_street_type_ave(self):
        assert normalize_street_name("5 AVE") == "5TH AVE"

    def test_normalizes_numbered_street_within_full_address(self):
        assert (
            normalize_street_name("123 MAIN ST AND 3 AVENUE")
            == "123 MAIN ST AND 3RD AVENUE"
        )

    def test_preserves_original_case_of_street_type(self):
        assert normalize_street_name("3 street") == "3RD street"
        assert normalize_street_name("3 Street") == "3RD Street"

    def test_leaves_non_numbered_streets_unchanged(self):
        assert normalize_street_name("BROADWAY") == "BROADWAY"
        assert normalize_street_name("123 MAIN STREET") == "123 MAIN STREET"

    def test_normalizes_multiple_numbered_streets_in_same_address(self):
        result = normalize_street_name("3 STREET AND 5 AVENUE")
        assert result == "3RD STREET AND 5TH AVENUE"

    def test_handles_road_and_rd_street_types(self):
        assert normalize_street_name("1 ROAD") == "1ST ROAD"
        assert normalize_street_name("1 RD") == "1ST RD"

    def test_handles_drive_and_dr_street_types(self):
        assert normalize_street_name("2 DRIVE") == "2ND DRIVE"
        assert normalize_street_name("2 DR") == "2ND DR"

    def test_handles_place_and_pl_street_types(self):
        assert normalize_street_name("3 PLACE") == "3RD PLACE"
        assert normalize_street_name("3 PL") == "3RD PL"

    def test_handles_boulevard_and_blvd_street_types(self):
        assert normalize_street_name("4 BOULEVARD") == "4TH BOULEVARD"
        assert normalize_street_name("4 BLVD") == "4TH BLVD"

    def test_handles_lane_and_ln_street_types(self):
        assert normalize_street_name("5 LANE") == "5TH LANE"
        assert normalize_street_name("5 LN") == "5TH LN"

    def test_handles_court_and_ct_street_types(self):
        assert normalize_street_name("6 COURT") == "6TH COURT"
        assert normalize_street_name("6 CT") == "6TH CT"

    def test_terrace(self):
        assert normalize_street_name("7 TERRACE") == "7TH TERRACE"
        assert normalize_street_name("7 TER") == "7TH TER"

    def test_way(self):
        assert normalize_street_name("8 WAY") == "8TH WAY"
