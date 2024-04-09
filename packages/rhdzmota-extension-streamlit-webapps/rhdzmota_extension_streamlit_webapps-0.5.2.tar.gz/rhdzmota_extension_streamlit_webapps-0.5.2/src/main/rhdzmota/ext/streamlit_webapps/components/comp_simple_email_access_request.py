from dataclasses import dataclass
from typing import Optional

import streamlit as st

from rhdzmota.ext.streamlit_webapps.page_view import PageView


@dataclass(frozen=True, slots=True, kw_only=True)
class SimpleEmailAccessRequest(PageView):
    reference_page_on_success: str
    reference_page_on_failure: str
    reference_page_request_email_verification_code: str
    overwrite_component_subtitle: Optional[str] = None
    overwrite_submit_button_label: Optional[str] = None

    @property
    def submit_button_label(self) -> str:
        return self.overwrite_submit_button_label or "Submit"

    @property
    def component_subtitle(self) -> str:
        return self.overwrite_component_subtitle or "Request Access Via Email"

    def view(self, **kwargs):
        st.markdown(f"## {self.component_subtitle}")
        with st.form("form-" + self.refname):
            email = st.text_input("Corporate email")
            passcode = st.text_input("Passcode (optional)")
            submitted = st.form_submit_button(self.submit_button_label)
        if not submitted:
            return
        st.session_state["email_main"] = email
        # TODO: Implement email validation
        if "@" not in email:
            return st.error(f"Email validation error.")
        # Verify that the email contains a valid domain
        _, domain = email.split("@")
        # TODO: Domain verification via environ
        if not passcode:
            # TODO: Implement email verification
            return self.forward("canonical_error")
        # TODO: Verify if passcode is valid
        elif True:
            return self.forward(self.reference_page_on_success)
