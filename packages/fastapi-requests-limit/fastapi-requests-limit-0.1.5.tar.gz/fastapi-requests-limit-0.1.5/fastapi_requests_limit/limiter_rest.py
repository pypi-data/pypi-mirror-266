import datetime
from datetime import timedelta
from functools import wraps

from fastapi import Request, Response

from .configuration import Limiter

count = {}


class LimiterDecorator:
    def __init__(self, time, count_target, status_return_error=405):
        self.time = time
        self.count_target = count_target
        self.status_return_error = status_return_error

    def __call__(self, func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            self.limiter = Limiter()  # I need to inject this depend
            self.storage = storage = self.limiter.storage
            ip = request.headers.get("host")
            time = self.time
            count_target = self.count_target
            history = storage.get_register(ip)
            if history:
                history["count"] = int(history["count"]) + 1
                last = datetime.datetime.strptime(
                    history["last"], "%Y-%m-%d %H:%M:%S.%f"
                )
                if (
                    datetime.datetime.now() - last <= timedelta(seconds=time)
                    and int(history["count"]) > count_target
                ):
                    return Response(status_code=self.status_return_error)
                elif (
                    datetime.datetime.now() - last > timedelta(seconds=time)
                    and int(history["count"]) > count_target
                ):
                    history["count"] = 1
                    history["date"] = str(datetime.datetime.now())
                elif (
                    datetime.datetime.now() - last > timedelta(seconds=time)
                    and int(history["count"]) <= count_target
                ):
                    history["count"] = 1
                    history["date"] = str(datetime.datetime.now())
                history["last"] = str(datetime.datetime.now())
                storage.update_register(ip, history)

            else:
                storage.create_register(ip)

            response = await func(request)
            return response

        return wrapper
