"""Container health check for the Streamlit HTTP endpoint."""
from urllib.request import urlopen


def main() -> int:
    try:
        with urlopen("http://127.0.0.1:8501/_stcore/health", timeout=4) as response:
            return 0 if response.status == 200 else 1
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
