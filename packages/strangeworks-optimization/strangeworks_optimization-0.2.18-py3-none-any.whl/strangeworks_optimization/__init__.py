import importlib.metadata

__version__ = importlib.metadata.version("strangeworks-optimization")

from .optimizer import StrangeworksOptimizer  # noqa: F401
