"""
Shared pytest fixtures/setup.

Sets required environment variables before any `app.*` module is imported,
since app.config.settings.Settings requires them at import time (fails fast
in production if misconfigured, which also means tests must supply dummy
values for anything not under test).
"""

import os

os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_ci")
os.environ.setdefault("FIREBASE_CREDENTIALS_PATH", "/tmp/fake_firebase_test.json")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")

# Create a syntactically-valid (but non-functional) fake service account file,
# so any accidental Firebase initialization during import doesn't crash on a
# missing file. Firebase calls themselves are mocked in tests that need them.
_fake_firebase_path = os.environ["FIREBASE_CREDENTIALS_PATH"]
if not os.path.exists(_fake_firebase_path):
    import json

    with open(_fake_firebase_path, "w") as f:
        json.dump(
            {
                "type": "service_account",
                "project_id": "test-project",
                "private_key_id": "test",
                "private_key": (
                    "-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQYDK2VwBCIEIA==\n-----END PRIVATE KEY-----\n"
                ),
                "client_email": "test@test-project.iam.gserviceaccount.com",
                "client_id": "1",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            },
            f,
        )
