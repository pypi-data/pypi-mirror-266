from .covid_qa import CovidQAParser
from .databricks_dolly import DollyParser
from .drop import DropParser
from .parser import Parser

BENCHMARKS = [
    CovidQAParser,
    DropParser,
    DollyParser
]


def benchmarks_for_UI():
    return [{'id': benchmark._id, 'display_name': benchmark.display_name} for benchmark in BENCHMARKS]


def get_benchmark(_id):
    for benchmark in BENCHMARKS:
        if benchmark._id == _id:
            return benchmark
