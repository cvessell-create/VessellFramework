import pytest

from vessell.source_readers import audit_opm, audit_opm_rows, audit_pdf


def row(**changes):
    return {"count": "2", "agency_code": "A",
            "personnel_action_effective_date_yyyymm": "202409", **changes}


def test_withheld_cells_are_not_zero_counts_or_negative_evidence():
    result = audit_opm_rows([
        row(pay="REDACTED"), row(count="REDACTED"), row(count=None, agency_code=""),
    ], "202409")
    assert result["known_count_subtotal"] == 2
    assert result["unknown_count_rows"] == 2
    assert result["redacted_cells_by_column"] == {"count": 1, "pay": 1}
    assert result["missing_cells_by_column"] == {"agency_code": 1, "count": 1}
    assert result["agency_unknown_count_rows"] == {"A": 1, "UNKNOWN": 1}


@pytest.mark.parametrize("rows,period", [
    ([], "202409"), ([row()], "202413"), ([row()], "2024"),
    ([row(count="-1")], "202409"), ([row(count="2.5")], "202409"),
    ([row(count=True)], "202409"),
    ([row(personnel_action_effective_date_yyyymm="202413")], "202409"),
    ([{"count": "1"}], "202409"),
])
def test_invalid_opm_population_is_rejected(rows, period):
    with pytest.raises(ValueError):
        audit_opm_rows(rows, period)


def test_unknown_periods_and_redaction_collapsed_rows_remain_explicit():
    record = row(personnel_action_effective_date_yyyymm="REDACTED")
    result = audit_opm_rows([record, record], "202409")
    assert result["records"] == 2
    assert result["unknown_period_rows"] == 2
    assert result["known_count_subtotal"] == 4


def test_file_reference_period_does_not_relabel_action_dates():
    result = audit_opm_rows([
        row(), row(personnel_action_effective_date_yyyymm="202209"),
    ], "202409")
    assert result["outside_reference_period_rows"] == 1
    assert result["known_count_subtotal"] == 4
    assert result["reference_period_known_count_subtotal"] == 2
    assert result["period_counts"] == {"202409": 1, "202209": 1}


def test_real_parquet_round_trip_decodes_all_rows(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    path = tmp_path / "source.parquet"
    with duckdb.connect(":memory:") as connection:
        connection.execute("""
            CREATE TABLE accessions AS SELECT '2' AS count, 'A' AS agency_code,
            '202409' AS personnel_action_effective_date_yyyymm
        """)
        connection.execute("COPY accessions TO ? (FORMAT PARQUET)", [str(path)])
    result = audit_opm(path, "202409")
    assert result["records"] == 1
    assert result["known_count_subtotal"] == 2
    assert result["validation"] == "ALL_ROWS_DECODED_AND_REQUIRED_FIELDS_CHECKED"


def test_pdf_decodes_every_page_and_reports_image_only_gap(tmp_path):
    pypdf = pytest.importorskip("pypdf")
    path = tmp_path / "blank.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    writer.write(path)
    result = audit_pdf(path)
    assert result["page_count"] == 2
    assert result["empty_text_pages"] == [1, 2]
    assert result["text_characters"] == 0


def test_malformed_pdf_is_not_reported_as_success(tmp_path):
    pytest.importorskip("pypdf")
    path = tmp_path / "bad.pdf"
    path.write_bytes(b"%PDF-1.7\ninvalid")
    with pytest.raises(ValueError, match="PDF decoding failed"):
        audit_pdf(path)
