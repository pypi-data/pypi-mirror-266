"""Authorization handler."""

import json
from urllib.parse import unquote

from jupyter_server.base.handlers import JupyterHandler
from tornado.web import RequestHandler

DATALAYER_IAM_USER_KEY = 'DATALAYER_IAM_USER_KEY'
DATALAYER_IAM_TOKEN_KEY = 'DATALAYER_IAM_TOKEN_KEY'


class CallbackOAuth(JupyterHandler):
    def check_xsrf_cookie(self) -> None:
        # Call grand parent method because parent method skip that check
        # when the user is authenticated (from the point of view of the Jupyter Server)
        RequestHandler.check_xsrf_cookie(self)

    def get(self):
        """Callback for the IAM service when using a OAuth2 identity provider.

        It will set the user profile and JWT token in the local storage. Then
        it will redirect the user to the Jupyter application where the information
        will be pulled from the local storage.
        """
        # We enforce XSRF validation to forbid external party
        # to request this endpoint without coming from the OAuth flow
        self.check_xsrf_cookie()
        error = self.get_argument("error", "")
        if error:
            provider = self.get_argument("provider", "<unknown>")
            self.set_status(401)
            self.write("""<!DOCTYPE html>
<html>
<body>
  <p>Failed to authenticate with {provider}.</p>
  <p>Error: {error}</p>
  <button id="return-btn">Return to Jupyter</button>
  <script type="module">
    const btn = document.getElementById("return-btn")
    btn.addEventListener("click", () => {{
      // Redirect to default page
      window.location.replace('{base_url}');           
    }})
  </script>
</body>
</html>""".format(
                error=error,
                provider=provider,
                base_url=self.base_url)
            )
            return

        user_raw = self.get_argument("user", "")
        token = self.get_argument("token", "")
        if not user_raw or not token:
            self.set_status(400, "user and token must be provided.")
        user = json.loads(unquote(user_raw))

        self.write("""<!DOCTYPE html>
<html>
<body>
  <script type="module">
    // Store the user information
    window.localStorage.setItem(
      '{user_key}',
      JSON.stringify({{
        uid: '{uid}',
        handle: '{handle}',
        firstName: '{first_name}',
        lastName: '{last_name}',
        email: '{email}',
        displayName: '{display_name}'
      }})
    );
    // Store the token
    localStorage.setItem('{token_key}', '{token}');
    // Redirect to default page
    window.location.replace('{base_url}');
  </script>
</body>
</html>""".format(
            user_key=DATALAYER_IAM_USER_KEY,
            uid=user.get("uid"),
            handle=user["handle"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            display_name=" ".join(
                (user["first_name"], user["last_name"])).strip(),
            token_key=DATALAYER_IAM_TOKEN_KEY,
            token=token,
            base_url=self.base_url
        )
        )
