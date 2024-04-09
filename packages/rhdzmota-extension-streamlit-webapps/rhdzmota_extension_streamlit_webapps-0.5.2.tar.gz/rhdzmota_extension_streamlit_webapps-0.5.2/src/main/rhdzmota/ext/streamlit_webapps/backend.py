import posixpath
from functools import cache
from typing import Optional

from tornado.routing import Rule, PathMatches
from tornado.web import Application, RequestHandler

from rhdzmota.settings import logger_manager


logger = logger_manager.get_logger(name=__name__)


class TornadoApplicationWrapper:
    singleton: Optional = None
    app_instance: Optional[Application] = None

    def __new__(cls, *args, **kwargs):
        if cls.singleton is None:
            logger.info("Tornado Application Wrapper: Creating singleton instance!")
            cls.singleton = super(TornadoApplicationWrapper, cls).__new__(cls)
            cls.app_instance = cls.get_tornado_application_instance()
        return cls.singleton

    def register_handler(self, uri: str, handler: RequestHandler) -> bool:
        if not handler:
            return False
        self.app_instance.wildcard_router.rules.insert(0, Rule(PathMatches(uri), handler))
        return True

    @classmethod
    @cache
    def get_tornado_application_instance(cls) -> Application:
        import gc

        return next(
            obj
            for obj in gc.get_referrers(Application)
            if obj.__class__ is Application
        )


class BackendRequestHandler(RequestHandler):
    alias: str = ""
    base_uri: str = "/api"

    @classmethod
    def get_uri(
            cls,
            overwrite_base_uri: Optional[str] = None,
            overwrite_alias: Optional[str] = None,
            fallback_alias: Optional[str] = None,
            use_empty_fallback: bool = False,
    ) -> str:
        fallback_alias = fallback_alias or (
            "" if use_empty_fallback else cls.__name__
        )
        return posixpath.join(
            overwrite_base_uri or cls.base_uri,
            overwrite_alias or cls.alias or fallback_alias
        ).rstrip("/")

    @classmethod
    def register(
            cls,
            overwrite_base_uri: Optional[str] = None,
            overwrite_alias: Optional[str] = None,
            fallback_alias: Optional[str] = None,
            use_empty_fallback: bool = False,
    ) -> bool:
        return TornadoApplicationWrapper().register_handler(
            uri=cls.get_uri(
                overwrite_base_uri=overwrite_base_uri,
                overwrite_alias=overwrite_alias,
                fallback_alias=fallback_alias,
                use_empty_fallback=use_empty_fallback,
            ),
            handler=cls,
        )
