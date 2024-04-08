import asyncio
import inspect
from functools import wraps

import typer


class UTyper(typer.Typer):
    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)

        def add_runner(f):

            @wraps(f)
            def runner(*args, **kwargs):
                asyncio.run(f(*args, **kwargs))

            if inspect.iscoroutinefunction(f):
                return decorator(runner)
            return decorator(f)

        return add_runner
