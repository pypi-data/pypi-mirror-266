import time
from typing import Optional, TYPE_CHECKING


class Gist:
    URL_TEMPLATE = "https://gist.githubusercontent.com/{username}/{gist_id}/raw/{commit}/{filename}"

    def __init__(self, username: str, gist_id: str, filename: str, commit: Optional[str] = None):
        self.username = username
        self.gist_id = gist_id
        self.filename = filename
        self.commit = commit

    @property
    def url(self) -> str:
        return self.URL_TEMPLATE.format(
            username=self.username,
            gist_id=self.gist_id,
            filename=self.filename,
            commit=self.commit or ""
        )

    def get_code(self) -> str:
        if not TYPE_CHECKING:
            # For some reason, I cannot get mypy (mypy==0.971) on Python 3.8.10 to ignore type problems derived from
            # adding the requests library as a dependency. Therefore, this if-statement is just a quickfix until
            # we can safely integrate the requests library into the codebase with the corresponding type-checks.
            import requests  # type: ignore
        else:
            import importlib

            requests = importlib.import_module("requests")

        response = requests.get(url=self.url)
        return response.text

    def load(self):
        # Retrieve the code snippet
        code_snippet = self.get_code()
        # Define the user namespace
        try:
            import IPython  # type: ignore

            user_ns = getattr(IPython.get_ipython(), 'user_ns', globals())
        except ImportError:
            user_ns = {**locals(), **globals()}
        # Execute the snippet
        exec(compile(code_snippet, f"{int(time.time())}", "exec"), user_ns, user_ns)
