from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "HTTP requests",
    ["path", "method", "code"]
)
http_request_duration = Histogram(
    "http_request_duration_seconds",
    "Latency",
    ["path", "method"]
)

items_ingested = Counter(
    "items_ingested_total",
    "Ingested items",
    ["source"]
)
answers_generated = Counter(
    "answers_generated_total",
    "Generated answers",
    ["provider"]
)
answers_sent = Counter(
    "answers_sent_total",
    "Sent answers",
    ["source"]
)
wb_responses = Counter(
    "wb_responses_total",
    "WB responses",
    ["endpoint", "code"]
)