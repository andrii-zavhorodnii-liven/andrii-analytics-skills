# When to Mock

Mock at **system boundaries** only:

- Source APIs you ingest from
- The warehouse (sometimes — prefer a scratch dataset, or an in-memory store)
- Object storage and secret managers
- Time and randomness
- Anything billed per call (Vertex AI endpoints, third-party enrichment APIs)

Don't mock:

- Your own transformation functions
- Internal collaborators
- Anything you control

## Prefer a fake over a mock

For a source API or a warehouse, a small **fake** — a real implementation backed by a dict or a list — beats a mock almost every time. A mock asserts on calls, which couples the test to how you called things. A fake lets you assert on the *result*, which is the behaviour you actually care about.

```python
# GOOD: a fake you can assert results against
class FakeOrdersApi:
    def __init__(self, pages): self._pages = pages
    def pages(self, since): return iter(self._pages)

# Weaker: a mock, which can only tell you what was called
client = mocker.Mock()
```

## Designing for testability

**1. Use dependency injection**

Pass external dependencies in rather than constructing them inside:

```python
# Easy to test
def load_orders(orders, client):
    return client.insert_rows("staging.orders", orders)

# Hard to test
def load_orders(orders):
    client = bigquery.Client(project=os.environ["GCP_PROJECT"])
    return client.insert_rows("staging.orders", orders)
```

**2. Keep transformation pure and I/O at the edges**

The bug-prone part of a pipeline is almost never the read or the write — it's the shaping in between. Extract that into pure functions over plain data and it needs no mocking at all:

```python
# The part worth testing, needing nothing mocked
def to_staging_rows(api_payload: dict) -> list[dict]: ...

# The thin edges, mocked or faked at the boundary
def run(client, api): client.insert_rows("staging.orders", to_staging_rows(api.fetch()))
```

If a test needs a mock to reach your transformation logic, that's usually a design signal, not a testing problem.

**3. Prefer specific operations over one generic caller**

Create a function per external operation instead of one generic fetcher with conditional logic:

```python
# GOOD: each operation is independently fakeable
class OrdersApi:
    def get_order(self, order_id): ...
    def list_orders(self, since): ...
    def get_customer(self, customer_id): ...

# BAD: faking this requires conditional logic inside the fake
class Api:
    def request(self, path, params): ...
```

The specific approach means:

- Each fake returns one specific shape
- No conditional logic in test setup
- It's obvious from the test which source operations it exercises
- Types can be precise per operation

**4. Inject the clock**

Anything that windows, partitions, or watermarks depends on "now", and a test that depends on the real clock is a test that fails at midnight. Pass `now` in as an argument, or inject a clock function — never call `datetime.now()` inside the logic under test.

This is the same rule `/code-review`'s data baseline flags as **Hidden clock dependency** — if the rule changes, change it in both places.
