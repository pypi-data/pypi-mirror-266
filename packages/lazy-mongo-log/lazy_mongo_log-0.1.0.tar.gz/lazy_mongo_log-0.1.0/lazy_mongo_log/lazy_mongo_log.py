from typing import Optional, Callable
import sys
from io import StringIO
from pymongo.collection import Collection
from .schemas import log_schema


class LazyMongoLog:
    def __init__(
        self,
        collection: Collection = None,  # type: ignore
        type: str = "info",
        keyword: Optional[str] = None,
        use_console: bool = True,
        log_selector: Callable[[dict, ...], dict] = None,  # type: ignore
    ):
        self.collection = collection
        self.type = type
        self.keyword = keyword
        self.use_console = use_console
        self.log_selector = log_selector

    def __call__(
        self,
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        **kwargs,
    ):
        return self.__write(
            *values,
            sep=sep,
            end=end,
            **kwargs,
        )

    def set(
        self,
        **kwargs,
    ):
        if "collection" in kwargs:
            self.collection = kwargs["collection"]

        if "type" in kwargs:
            self.type = kwargs["type"]

        if "keyword" in kwargs:
            self.keyword = kwargs["keyword"]

        if "use_console" in kwargs:
            self.use_console = kwargs["use_console"]

        if "log_selector" in kwargs:
            self.log_selector = kwargs["log_selector"]

        return self

    def using(
        self,
        **kwargs,
    ):
        return LazyMongoLog(
            collection=kwargs.get("collection", self.collection),
            type=kwargs.get("type", self.type),
            keyword=kwargs.get("keyword", self.keyword),
            use_console=kwargs.get("use_console", self.use_console),
            log_selector=kwargs.get("log_selector", self.log_selector),
        )

    def info(
        self,
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        **kwargs,
    ):
        return self.__write(
            *values,
            sep=sep,
            end=end,
            type="info",
            **kwargs,
        )

    def warn(
        self,
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        **kwargs,
    ):
        return self.__write(
            *values,
            sep=sep,
            end=end,
            type="warning",
            **kwargs,
        )

    def error(
        self,
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
        **kwargs,
    ):
        return self.__write(
            *values,
            sep=sep,
            end=end,
            type="error",
            **kwargs,
        )

    def __write(
        self,
        *values: object,
        sep: Optional[str],
        end: Optional[str],
        **kwargs,
    ):
        type: str = kwargs.get(
            "type",
            self.type,
        )
        keyword: str = kwargs.get(
            "keyword",
            self.keyword,
        )
        use_console: bool = kwargs.get(
            "use_console",
            self.use_console,
        )
        collection: Collection = kwargs.get(
            "collection",
            self.collection,
        )
        log_selector: Callable[[dict], dict] = kwargs.get(
            "log_selector",
            self.log_selector,
        )

        message = self.__get_message(
            *values,
            sep=sep,
            end=end,
        )

        if use_console:
            print(
                *values,
                sep=sep,
                end=end,
            )

        if collection != None:
            try:
                document = log_schema(
                    message=message,
                    type=type,
                    keyword=keyword,
                )

                if log_selector != None:
                    document = log_selector(document, **kwargs)

                result = self.collection.insert_one(document)

                return result.acknowledged
            except:
                return False

        return True

    def __get_message(
        self,
        *values: object,
        sep: Optional[str] = " ",
        end: Optional[str] = "\n",
    ):
        buffer = StringIO()

        prev = sys.stdout
        sys.stdout = buffer

        print(
            *values,
            sep=sep,
            end=end,
        )

        sys.stdout = prev

        return buffer.getvalue()
