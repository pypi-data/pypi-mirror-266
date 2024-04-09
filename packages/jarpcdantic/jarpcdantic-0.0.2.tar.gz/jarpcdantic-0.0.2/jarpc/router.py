import inspect
from inspect import _empty
from typing import Any, Type, OrderedDict

from pydantic import create_model, BaseModel

from jarpc import JarpcClient, AsyncJarpcClient


class JarpcClientRouter:
    def __init__(
        self,
        prefix: str | None = None,
        client: AsyncJarpcClient | JarpcClient | None = None,
        is_absolute_prefix: bool = False,
    ):
        self._client: AsyncJarpcClient | JarpcClient | None = client
        self._prefix: str | None = prefix
        self._is_absolute_prefix: bool = is_absolute_prefix
        self._method_map: dict = {}

        self._decorate_methods()

    def _decorate_methods(self):
        for attr_name, attr_value in self.__class__.__dict__.items():
            if attr_name.startswith("_") or isinstance(attr_value, property):
                continue

            if isinstance(attr_value, JarpcClientRouter):
                self._proceed_nested_router(attr_name, attr_value)

            if (
                not attr_name.startswith("_")
                and hasattr(attr_value, "__annotations__")
                and "return" in attr_value.__annotations__
            ):
                self._proceed_endpoint(attr_name, attr_value)

    def _proceed_endpoint(self, endpoint_name, endpoint_method):
        attr_signature = inspect.signature(endpoint_method)
        ordered_parameters_signature = [
            (k, v) for k, v in attr_signature.parameters.items()
        ]
        clear_parameters = {
            k: v
            for k, v in attr_signature.parameters.items()
            if k not in ["self", "args", "kwargs"] and not k.startswith("_")
        }

        model: Type[BaseModel] | None = None

        if "_model" in attr_signature.parameters:
            model: Type[BaseModel] = attr_signature.parameters["_model"].default
        elif len(clear_parameters) == 1:
            parameter = clear_parameters[list(clear_parameters.keys())[0]]
            model = parameter.annotation if parameter.annotation is not _empty else None
        elif len(clear_parameters) > 1:
            model = create_model(
                "DynamicModel",
                **{
                    k: (
                        Any if v.annotation is _empty else v.annotation,
                        ... if v.default is _empty else v.default,
                    )
                    for k, v in clear_parameters.items()
                },
            )

        wrapped_attr = self._wrap(self, endpoint_name, model, attr_signature.parameters)
        wrapped_attr.__annotations__ = endpoint_method.__annotations__

        self._method_map[endpoint_name] = wrapped_attr
        setattr(self, endpoint_name, wrapped_attr)

    def _proceed_nested_router(
        self, attr_router_name, nested_router: "JarpcClientRouter"
    ) -> None:
        if nested_router._prefix is None:
            nested_router._prefix = attr_router_name

        if nested_router._is_absolute_prefix:
            return

        if self._prefix is None:
            prefix = ""
        else:
            prefix = self._prefix

        if not nested_router._prefix.startswith(prefix):
            nested_router._prefix = (
                prefix
                + ("." if prefix and nested_router._prefix else "")
                + nested_router._prefix
            )

        if nested_router._client is None and self._client is not None:
            nested_router._client = self._client

    @staticmethod
    def _wrap(
        self,
        method: str,
        model: Type[BaseModel] | None,
        attr_signature_parameters: OrderedDict,
    ):
        async def wrapped(*args, **kwargs):
            service_kwargs = {k: v for k, v in kwargs.items() if k.startswith("_")}
            clear_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_")}

            if model is not None:
                if issubclass(model, BaseModel):
                    args_with_default = {
                        k: v.default for k, v in attr_signature_parameters.items()
                    }
                    for index, value in enumerate(args):
                        args_with_default[
                            list(attr_signature_parameters.items())[index + 1][0]
                        ] = value
                    params = model(**(args_with_default | clear_kwargs))
                else:
                    params = [*args, *kwargs.values()][0]
            else:
                params = None

            if self._client is not None:
                await self._client(method=method, params=params, **service_kwargs)
            else:
                print("client is None, call", method, params)

        return wrapped


class CustomModel(BaseModel):
    name: str
    a: Any
    age: int
    b: float


if __name__ == "__main__":
    import asyncio

    class TestRouter(JarpcClientRouter):
        async def register(
            self, name: str, a, age: int = 33, b=44, _model=CustomModel, **kwargs
        ) -> None:
            """
            params=CustomModel(name, a, age, b)
            """
            ...

    class PassportRouter(JarpcClientRouter):
        test = TestRouter()

        async def register(
            self, name: str, a, age: int = 33, b=44, _model=CustomModel, **kwargs
        ) -> None:
            """
            params=CustomModel(name, a, age, b)
            """
            ...

        async def get_status(self, b=22, **kwargs) -> None:
            """
            params=22
            """
            ...

        async def invalidate(self, data: str, a, **kwargs) -> None:
            """
            params=DynamicModel(data, a)
            """
            ...

    class MvdRouter(JarpcClientRouter):
        passport = PassportRouter()

        async def get_status(self) -> None:
            """
            params=None
            """
            ...

    async def main():
        router = MvdRouter(prefix="mvd")
        await router.get_status()
        print("---")
        await router.passport.register("eugene", 1, 33, 55)
        await router.passport.get_status("eugene")
        await router.passport.invalidate(data="22", a="33")
        await router.passport.test.register("22", a="33")

    asyncio.run(main())
