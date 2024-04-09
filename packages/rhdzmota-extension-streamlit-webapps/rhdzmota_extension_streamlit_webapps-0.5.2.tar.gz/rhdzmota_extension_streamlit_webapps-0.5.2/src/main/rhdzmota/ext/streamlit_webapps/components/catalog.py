import enum

from .comp_simple_email_access_request import SimpleEmailAccessRequest


class CompCatalog(enum.Enum):
    SIMPLE_EMAIL_ACCESS_REQUEST = SimpleEmailAccessRequest

    def configure(self, **kwargs):
        return self.value(**kwargs)
