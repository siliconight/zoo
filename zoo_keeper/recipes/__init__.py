"""DNA recipe registry: species name -> build(plan, streams, collection)."""
from __future__ import annotations


def get(species):
    if species == "desk":
        from . import desk as mod
    elif species == "chair":
        from . import chair as mod
    elif species == "helmet":
        from . import helmet as mod
    elif species == "boots":
        from . import boots as mod
    elif species == "simple_car":
        from . import simple_car as mod
    else:
        raise KeyError(f"No recipe for species '{species}'")
    return mod.build
