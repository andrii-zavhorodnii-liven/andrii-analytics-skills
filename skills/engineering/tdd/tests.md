# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```python
# GOOD: Tests observable behaviour
def test_ingesting_a_page_of_orders_yields_one_row_per_order():
    source = FakeOrdersApi(pages=[[order("A-1"), order("A-2")]])
    rows = list(ingest_orders(source, since=date(2026, 1, 1)))
    assert [r["order_id"] for r in rows] == ["A-1", "A-2"]
```

Characteristics:

- Tests behaviour callers and downstream models care about
- Uses the public interface only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```python
# BAD: Tests implementation details
def test_ingest_orders_calls_the_client_paginator(mocker):
    client = mocker.Mock()
    ingest_orders(client, since=date(2026, 1, 1))
    client.paginate.assert_called_once_with(page_size=500)
```

Red flags:

- Mocking internal collaborators
- Testing private functions
- Asserting on call counts or call order
- Test breaks when refactoring without behaviour change
- Test name describes HOW, not WHAT
- Verifying through external means instead of the interface

```python
# BAD: Bypasses the interface to verify
def test_load_orders_writes_to_bigquery(bq):
    load_orders([order("A-1")])
    rows = bq.query("SELECT * FROM staging.orders WHERE order_id = 'A-1'").result()
    assert list(rows)

# GOOD: Verifies through the interface
def test_loaded_orders_are_readable_back():
    store = InMemoryOrderStore()
    load_orders([order("A-1")], store=store)
    assert store.get("A-1").order_id == "A-1"
```

**Tautological tests**: The expected value restates the implementation, so the test passes by construction.

```python
# BAD: Expected value is recomputed the way the code computes it
def test_revenue_sums_line_items():
    lines = [{"amount": 10.0}, {"amount": 5.0}]
    expected = sum(line["amount"] for line in lines)
    assert revenue(lines) == expected

# GOOD: Expected value is an independent, known literal
def test_revenue_sums_line_items():
    assert revenue([{"amount": 10.0}, {"amount": 5.0}]) == 15.0
```

## Testing transformations

A transformation — SQL or a dataframe step — is testable behaviour like anything else. Give it a handful of hand-written input rows whose correct output you worked out yourself, and assert on the output rows. The whole point is that the expected value comes from *you*, not from re-running the transformation.

```python
# GOOD: Fixed input rows, expected output worked out by hand
def test_sessionisation_splits_on_a_thirty_minute_gap():
    events = [
        event("u1", "2026-01-01T10:00:00Z"),
        event("u1", "2026-01-01T10:20:00Z"),  # same session
        event("u1", "2026-01-01T11:00:00Z"),  # 40min gap -> new session
    ]
    sessions = sessionise(events, gap=timedelta(minutes=30))
    assert [len(s.events) for s in sessions] == [2, 1]
```

For a Dataform model, the equivalent lives in the graph rather than in `pytest`: an **assertion** on the output (`uniqueKey`, `nonNull`, or a custom assertion that must return zero rows). A grain the model must guarantee belongs in an assertion, not in a comment.

Keep the two straight: `pytest` covers Python you wrote, assertions cover SQL the warehouse runs. Neither substitutes for the other.
