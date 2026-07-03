from pathlib import Path
import json
import time
import requests

BASE_URL = "https://pokeapi.co/api/v2"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "pokeapi"

REQUEST_DELAY = 0.2
TIMEOUT = 20


def get_endpoints() -> list[str]:
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw PokeAPI directory not found: {RAW_DIR}")

    endpoints = sorted(
        path.name
        for path in RAW_DIR.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )

    if not endpoints:
        raise RuntimeError(f"No endpoint directories found in: {RAW_DIR}")

    return endpoints


def safe_filename(resource: dict) -> str:
    url = resource["url"].rstrip("/")
    resource_id = url.split("/")[-1]
    name = resource["name"]
    return f"{resource_id}_{name}.json"


def get_json(url: str) -> dict:
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_resource_list(endpoint: str) -> list[dict]:
    url = f"{BASE_URL}/{endpoint}?limit=100000&offset=0"
    data = get_json(url)
    return data["results"]


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def collect_endpoint(endpoint: str) -> None:
    print(f"[START] {endpoint}")

    resources = get_resource_list(endpoint)
    endpoint_dir = RAW_DIR / endpoint
    endpoint_dir.mkdir(parents=True, exist_ok=True)

    for idx, resource in enumerate(resources, start=1):
        filename = safe_filename(resource)
        save_path = endpoint_dir / filename

        if save_path.exists():
            continue

        try:
            data = get_json(resource["url"])
            save_json(save_path, data)
            print(f"[{idx}/{len(resources)}] saved {endpoint}/{filename}")
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"[ERROR] {endpoint} {resource['name']}: {e}")


def main() -> None:
    for endpoint in get_endpoints():
        collect_endpoint(endpoint)


if __name__ == "__main__":
    main()
