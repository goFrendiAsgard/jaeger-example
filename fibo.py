from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.shim import opentracing_shim

resource = Resource.create(attributes={"service.name": "percobaan"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer_provider = trace.get_tracer_provider()

# Configure the tracer to export traces to Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
tracer_provider.add_span_processor(span_processor)

# Create an OpenTracing shim. This implements the OpenTracing tracer API, but
# forwards calls to the underlying OpenTelemetry tracer.
opentracing_tracer = opentracing_shim.create_tracer(tracer_provider)

tracer = trace.get_tracer(__name__)

def fibo_recursive(n):
    with opentracing_tracer.start_active_span('call fibo-recursive') as scope:
        scope.span.set_tag("func", 'fibo_recursive')
        scope.span.set_tag("args", str(n))
        result = 1 if n <=2 else fibo_recursive(n-1) + fibo_recursive(n-2)
        scope.span.set_tag("val", str(result))
        return result

def fibo_iterative(n):
    if n <= 2:
        with opentracing_tracer.start_active_span('call fibo-iterative') as scope:
            scope.span.set_tag("func", 'fibo_iterative')
            scope.span.set_tag("args", str(n))
            result = 1
            scope.span.set_tag("val", str(result))
            return result
    # iterative beneran
    with opentracing_tracer.start_active_span('call fibo-iterative') as scope:
        scope.span.set_tag("func", 'fibo_iterative')
        scope.span.set_tag("args", str(n))
        a, b, c = 1, 1, 0
        for i in range(3, n+1):
            c = a + b
            with opentracing_tracer.start_active_span('loop fibo-iterative') as iterative_scope:
                iterative_scope.span.set_tag("iteration", 'fibo_iterative')
                iterative_scope.span.set_tag("index", str(i))
            a, b = b, c
        scope.span.set_tag("val", str(c))
        return c
         

with tracer.start_as_current_span("Fibonacci") as span:
    span.set_attribute("is_example", "yes :)")
    print('fibo recursive', fibo_recursive(10))
    print('fibo iterative', fibo_iterative(10))