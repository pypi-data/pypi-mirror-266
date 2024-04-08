import os


def main():
    api_host = os.environ.get("POETRY_API_HOST", "https://api.deploymodel.com")

    with open("deploymodel/settings.py", "w") as f:
        f.write(f"API_HOST = '{api_host}'\n")


if __name__ == "__main__":
    main()
