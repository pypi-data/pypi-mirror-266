import json
from dataclasses import dataclass, field
from typing import Callable, Optional

import streamlit as st

from rhdzmota.settings import logger_manager
from rhdzmota.wrappers.sentry import SentrySDKConfig
from rhdzmota.ext.streamlit_webapps.backend import BackendRequestHandler


logger = logger_manager.get_logger(name=__name__)


class PageViewDescriptorRefname:

    def __get__(self, obj, objtype=None):
        # We should be able to always get the class
        cls = objtype or type(obj)
        default = getattr(
            cls,
            "overwrite_refname",
        ) or cls.__name__
        if not obj:
            return default
        return getattr(
            obj,
            "overwrite_instance_refname",
        ) or default


class PageViewSessionKeys:
    session_key_page_history = "page_history"
    session_key_page_current = "page_current"
    session_key_page_current_input_kwargs = "page_current_input_kwargs"

    @classmethod
    def history_exists(cls) -> bool:
        records = st.session_state.get(
            cls.session_key_page_history,
            [],
        )
        return len(records) > 0


class PageViewDescriptors:
    overwrite_refname: Optional[str] = None
    refname = PageViewDescriptorRefname()


@dataclass(frozen=True, slots=True, kw_only=True)
class PageViewHeader(PageViewSessionKeys):
    def on_start(self):
        pass


@dataclass(frozen=True, slots=True, kw_only=True)
class PageView(PageViewDescriptors, PageViewSessionKeys):
    page_title: Optional[str] = None
    page_layout: Optional[str] = None
    favicon_path: Optional[str] = None
    initial_sidebar_state: Optional[str] = None
    menu_items: dict = field(default_factory=dict)
    page_configs_path: Optional[str] = None
    overwrite_instance_refname: Optional[str] = None
    page_configs_kwargs: dict = field(default_factory=dict)
    disable_sentry: bool = False
    backend_request_handler: Optional[BackendRequestHandler] = None
    backend_request_handler_overwrite_alias: Optional[str] = None
    backend_request_handler_overwrite_base_uri: Optional[str] = None
    backend_request_handler_use_empty_fallback: Optional[str] = None

    def __post_init__(self):
        if self.backend_request_handler:
            self.backend_request_handler.register(
                overwrite_base_uri=self.backend_request_handler_overwrite_base_uri,
                overwrite_alias=self.backend_request_handler_overwrite_alias,
                use_empty_fallback=self.backend_request_handler_use_empty_fallback,
            )

    @classmethod
    def inline(cls, view_name: str, func: Callable, **kwargs) -> 'PageView':
        return type(view_name, (cls, ), {"view": func, **kwargs})

    @property
    def configs_page(self) -> dict:
        page_configs_constructor = {
            "page_title": self.page_title,
            "page_icon": self.favicon_path,
            "menu_items": self.menu_items,
            # TODO: Add enum validation
            "layout": self.page_layout or "centered",
            "initial_sidebar_state": self.initial_sidebar_state or "auto",
        }
        if not self.page_configs_path:
            return page_configs_constructor
        with open(self.page_configs_path, "r") as file:
            content = file.read()
        return {
            **json.loads(content),
            **page_configs_constructor,
        }

    def enable_sentry(self):
        # Early exit is sentry is explicitly disabled.
        if self.disable_sentry:
            return
        # Configure Sentry SDK... if credentials are available.
        session_key = "sentry_enabled"
        if st.session_state.get(session_key) is None and SentrySDKConfig.configure_with_defaults():
            st.session_state["sentry_enabled"] = "success"
            logger.info("SentrySDK Correctly configured!")
        elif st.session_state.get(session_key) is None:
            st.session_state["sentry_enabled"] = "failure"
            logger.warning("SentrySDK was configuration failure due to missing DNS...")

    def __enter__(self) -> 'PageView':
        # Page config should only be executed ONCE and
        # must be the first streamlit command.
        st.set_page_config(**self.configs_page)
        # Sentry performance tracing
        self.enable_sentry()
        # Register the current page in the sesion state
        st.session_state[self.session_key_page_current] = self.refname
        # Register the current page as the first page in history
        key_page_history = self.session_key_page_history
        if key_page_history not in st.session_state:
            st.session_state[key_page_history] = []
        # Execute on-start method (you can use this as a page header)
        if isinstance(self, PageViewHeader):
            self.on_start()
        return self

    def __exit__(self, *args):
        # TODO: To be defined...
        pass

    def forward(
            self,
            page_key: str,
            exclude_from_history: bool = False,
            **kwargs,
    ):
        # Get the current page
        page_source = st.session_state[self.session_key_page_current]
        page_source_kwargs = st.session_state.get(self.session_key_page_current_input_kwargs) or {}
        # Set the next page flow stage and propagate kwargs
        st.session_state[self.session_key_page_current] = page_key
        st.session_state[self.session_key_page_current_input_kwargs] = kwargs
        # Set the page-source as part of the page-history
        if not exclude_from_history:
            st.session_state[self.session_key_page_history].append((page_source, page_source_kwargs))
        # Rerun to apply changes
        st.rerun()

    def backward(self):
        page_before, page_before_kwargs = st.session_state[self.session_key_page_history].pop(-1)
        self.forward(
            page_key=page_before,
            exclude_from_history=True,
            **page_before_kwargs,
        )

    def view(self, **kwargs):
        st.markdown("# Not Implemented :shrug:")


class CanonicalErrorView(PageView):
    overwrite_refname: Optional[str] = "canonical_error"

    def view(self, **kwargs):
        st.error("An issue was detected")
        if st.button("Return"):
            self.backward()
