import contextlib
from typing import Any, Dict, Iterator, Optional, Union

from haystack.lazy_imports import LazyImport
from haystack.tracing import Span, Tracer, tracer
from haystack.tracing import utils as tracing_utils

import langfuse


class LangfuseSpan(Span):
    def __init__(self, span: "Union[langfuse.client.StatefulSpanClient, langfuse.client.StatefulTraceClient]") -> None:
        self._span = span

    def set_tag(self, key: str, value: Any) -> None:
        coerced_value = tracing_utils.coerce_tag_value(value)
        self._span.update(metadata={key: coerced_value})

    def set_content_tag(self, key: str, value: Any) -> None:
        if not tracer.is_content_tracing_enabled:
            return

        if key.endswith(".input"):
            self._span.update(input=value)
        elif key.endswith(".output"):
            self._span.update(output=value)

    def raw_span(self) -> Any:
        return self._span

    def get_correlation_data_for_logs(self) -> Dict[str, Any]:
        return {}


class LangfuseTracer(Tracer):
    def __init__(self, tracer: "langfuse.Langfuse", name: str = "Haystack") -> None:
        self._tracer = tracer
        self._context: list[LangfuseSpan] = []
        self._name = name

    @contextlib.contextmanager
    def trace(self, operation_name: str, tags: Optional[Dict[str, Any]] = None) -> Iterator[Span]:
        tags = tags or {}
        span_name = tags.get("haystack.component.name", operation_name)

        if tags.get("haystack.component.type") in ["OpenAIGenerator"]:
            span = LangfuseSpan(self.current_span().raw_span().generation(name=span_name))
        else:
            span = LangfuseSpan(self.current_span().raw_span().span(name=span_name))

        self._context.append(span)
        span.set_tags(tags)

        yield span

        span.raw_span().end()
        self._context.pop()
        self._tracer.flush()

    def current_span(self) -> Span:
        if not self._context:
            # The root span has to be a trace
            self._context.append(LangfuseSpan(self._tracer.trace(name=self._name)))
        return self._context[-1]
