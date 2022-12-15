from aiohttp import web
from aiohttp.web_exceptions import HTTPError


@web.middleware
class StatsdMiddleware:
    async def __call__(self, request: web.Request, handler):
        client = request.config_dict['statsd_client']

        with client.pipeline() as pip, \
                pip.timer(f"request.time"),\
                pip.timer(f"request.{request.path}.time"):
            try:
                pip.incr(f"request.{request.path}.count")

                for_print_input = await request.text()
                #print("start:", for_print_input)
                response = await handler(request)
                #print("done:", for_print_input)

                pip.incr(f"request.status.{request.path}.{response.status}.count")
                pip.incr(f"request.status.{response.status}.count")

                return response
            except HTTPError as http_err:
                pip.incr(f"request.status.{request.path}.{http_err.status_code}.count")
                pip.incr(f"request.status.{http_err.status_code}.count")
                print("error : ", http_err, "json : ", for_print_input)
                raise http_err
            except Exception as e:
                pip.incr(f"request.failed.{request.path}.{type(e).__name__}.count")
                pip.incr(f"request.failed.{type(e).__name__}.count")
                print("error : ", e, "json : ", for_print_input)
                raise e
