from typing import Callable
import time as t


def explicit(
    condition: Callable,
    timeout: int = 9,
    poll_frequency: float = 0.5,
    withReturn: bool = False,
    raiseError: bool = False,
):
    start = t.monotonic()
    while (t.monotonic() - start) < timeout:
        try:
            res = condition()
            if withReturn:
                if res:
                    return res
            else:
                return
        except:
            pass
        t.sleep(poll_frequency)
    if not raiseError:
        return False
    raise TimeoutError("Condition not met within the specified timeout.")
