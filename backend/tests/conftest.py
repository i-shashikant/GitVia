import os

os.environ.setdefault("JWT_SECRET", "gitvia-test-secret")
os.environ.setdefault("ENCRYPTION_KEY", "")
os.environ.setdefault("GITHUB_CLIENT_ID", "test")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
