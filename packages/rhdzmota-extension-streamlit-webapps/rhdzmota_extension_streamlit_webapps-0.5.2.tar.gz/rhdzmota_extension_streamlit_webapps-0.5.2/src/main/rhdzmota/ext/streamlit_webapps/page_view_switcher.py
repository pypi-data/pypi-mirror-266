import enum
from typing import List, Optional

import streamlit as st

from rhdzmota.ext.streamlit_webapps.backend import BackendRequestHandler
from rhdzmota.ext.streamlit_webapps.page_view import (
    PageView,
    CanonicalErrorView,
)


class PageViewSwitcher(enum.Enum):

    @classmethod
    def get_switcher_name(cls) -> str:
        return cls.__name__

    @classmethod
    def from_page_views(
            cls,
            switcher_name: str,
            page_views: List[PageView],
            disable_canonical_error: bool = False,
    ) -> 'PageViewSwitcher':
        canonical_error_item = ("canonical_error", CanonicalErrorView())
        return cls(
            value=switcher_name,
            names=[
                (page_view.refname, page_view)
                for page_view in page_views
            ] + ([] if disable_canonical_error else [canonical_error_item]),
        )

    @classmethod
    def run(
            cls,
            initial_page_key: str,
            backend_request_handler: Optional[BackendRequestHandler] = None,
            backend_request_handler_keep_alias: bool = False,
            **initial_page_kwargs
    ):
        if backend_request_handler:
            backend_request_handler.register(
                overwrite_alias=cls.get_switcher_name() if not backend_request_handler_keep_alias else None,
            )
        # On first execution, save the inital page key with their corresponding kwargs
        page_current = st.session_state.get(PageView.session_key_page_current, None)
        if not page_current:
            st.session_state[PageView.session_key_page_current] = initial_page_key
            st.session_state[PageView.session_key_page_current_input_kwargs] = initial_page_kwargs
        # Execute the page defined on the session-state

        with cls[page_current or initial_page_key].value as current_page_instance:
            current_page_instance.view(
                **st.session_state.get(
                    PageView.session_key_page_current_input_kwargs,
                    {}
                )
            )
