from layoutscribe.layout.validate import build_default_validator


def test_schema_loads():
  v = build_default_validator()
  assert v is not None


def test_minimal_page_validates():
  v = build_default_validator()
  page = {"page_number": 1, "width_px": 100, "height_px": 100, "blocks": []}
  errs = [e.message for e in v.iter_errors(page)]
  assert not errs


