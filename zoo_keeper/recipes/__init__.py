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
    elif species == "filing_cabinet":
        from . import filing_cabinet as mod
    elif species == "table":
        from . import table as mod
    elif species == "crt_tv":
        from . import crt_tv as mod
    elif species == "atm":
        from . import atm as mod
    elif species == "vending_machine":
        from . import vending_machine as mod
    elif species == "briefcase":
        from . import briefcase as mod
    elif species == "cash_stack":
        from . import cash_stack as mod
    elif species == "soda_cup":
        from . import soda_cup as mod
    elif species == "cheesesteak":
        from . import cheesesteak as mod
    else:
        raise KeyError(f"No recipe for species '{species}'")
    return mod.build
