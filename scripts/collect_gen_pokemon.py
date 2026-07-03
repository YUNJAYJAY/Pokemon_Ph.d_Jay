from pathlib import Path
import json
import time
import requests

BASE_URL = "https://pokeapi.co/api/v2"
RAW_DIR = Path("data/raw/pokeapi")

START_ID = 1
END_ID = 151

REQUEST_DELAY = 0.2
TIMEOUT = 20

def get_json(url: str) -> dict:
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()

def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def collect_resource(endpoint: str, pokemon_id: int) -> None:
    url = f"{BASE_URL}/{endpoint}/{pokemon_id}"
    data = get_json(url)

    name = data["name"]
    save_path = RAW_DIR / endpoint / f"{pokemon_id:03d}_{name}.json"

    if save_path.exists():
        print(f"[SYSTEM][SKIP] {endpoint}/{save_path.name}")
        return
    
    save_json(save_path, data)
    print(f"[SYSTEM][SAVE] {endpoint}/{save_path.name}")

def main() -> None:
    for pokemon_id in range(START_ID, END_ID + 1):
        print(f"\n[SYSTEM][POKEMON ID] {pokemon_id}")

        try:
            collect_resource("pokemon", pokemon_id)
            time.sleep(REQUEST_DELAY)

            collect_resource("pokemon-species", pokemon_id)
            time.sleep(REQUEST_DELAY)

        except requests.HTTPError as e:
            print(f"[SYSTEM][HTTP ERROR] id={pokemon_id}: {e}")

        except requests.RequestException as e:
            print(f"[SYSTEM][REQUESTE ERROR] id={pokemon_id}: {e}")

        except Exception as e:
            print(f"[SYSTEM][ERROR] id={pokemon_id}: {e}")

if __name__ == "__main__":
    main()