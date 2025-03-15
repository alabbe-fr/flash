import csv
import requests

DEBUG = True
PROD = False
URL = "https://flash-api.alabbe.fr" if PROD else "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}
PROXIES = (
    {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080",
    }
    if DEBUG
    else {}
)


class Deck:
    def __init__(self):
        self.name = ""
        self.level = ""
        self.words: list[dict[str, str]] = []

    def __repr__(self):
        return ({"level": self.level, "words": len(self.words)}).__repr__()


class Profile:
    def __init__(self):
        self.name = ""
        self.decks: dict[tuple[str, str], Deck] = {}

    def __repr__(self):
        return self.decks.__repr__()


data: dict[str, Profile] = {}
current_profile = Profile()
current_deck = Deck()


with open("data.csv", newline="") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=":", quotechar='"')
    for row in spamreader:
        if row[0].strip() == "":
            if current_deck.name:
                current_profile.decks[
                    (
                        current_deck.name,
                        current_deck.level,
                    )
                ] = current_deck

                current_deck = Deck()
            else:
                data[current_profile.name] = current_profile
                current_profile = Profile()

        if current_profile.name == "":
            current_profile.name = row[0]

        elif current_deck.name == "":
            current_deck.name = row[0]
            current_deck.level = row[1]

        else:
            word = {
                "verso": row[0],
                "recto": row[1],
            }

            if len(row) >= 3:
                word["picture"] = row[2]

            if len(row) >= 4:
                word["description"] = "\n".join(row[3:])

            current_deck.words.append(word)

    current_profile.decks[
        (
            current_deck.name,
            current_deck.level,
        )
    ] = current_deck
    data[current_profile.name] = current_profile

print(f"Found {len(data.keys())} profiles: {', '.join(data.keys())}\n")


def get_existing_profiles() -> dict[str, int]:
    res = requests.get(
        f"{URL}/profiles",
        headers=HEADERS,
        proxies=PROXIES,
    )

    return {profile["name"]: profile["id"] for profile in res.json()}


def get_existing_decks(profile_id: int) -> dict[tuple[str, str], int]:
    res = requests.get(
        f"{URL}/decks/{profile_id}",
        headers=HEADERS,
        proxies=PROXIES,
    )

    return {(deck["name"], deck["level"]): deck["id"] for deck in res.json()}


def add_word(word: dict[str, str]):
    res = requests.post(
        f"{URL}/word",
        json=word,
        headers=HEADERS,
        proxies=PROXIES,
    )

    if res.status_code == 201:
        return res.json()["id"]

    raise ValueError(f"Word could not be created")


def add_deck(deck: Deck) -> int:
    print(f"New deck: {deck.name} - {deck.level}")
    words_ids = [add_word(word) for word in deck.words]

    res = requests.post(
        f"{URL}/deck",
        json={
            "name": deck.name,
            "level": deck.level,
            "words": words_ids,
        },
        headers=HEADERS,
        proxies=PROXIES,
    )

    if res.status_code == 201:
        return res.json()["id"]

    raise ValueError(f"Deck could not be created")


def add_profile(profile: Profile) -> int:
    print(f"New profile: {profile.name}")
    decks_ids = [add_deck(deck) for deck in profile.decks.values()]

    res = requests.post(
        f"{URL}/profile",
        json={
            "name": profile.name,
            "decks": decks_ids,
        },
        headers=HEADERS,
        proxies=PROXIES,
    )

    if res.status_code == 201:
        return res.json()["id"]

    raise ValueError(f"Profile could not be created")


def update_profile(profile_id: int, profile: Profile, decks_ids: list[int]) -> None:
    res = requests.post(
        f"{URL}/profile/{profile_id}",
        json={
            "name": profile.name,
            "decks": decks_ids,
        },
        headers=HEADERS,
        proxies=PROXIES,
    )

    if not res.status_code == 204:
        raise ValueError(f"Profile could not be updated")


reverse_profiles = get_existing_profiles()

for profile_key, profile in data.items():
    print(f"\n### {profile.name} ###\n")
    if profile_key in reverse_profiles:  # Profile already saved
        profile_id = reverse_profiles[profile_key]

        decks_ids = [
            add_deck(deck)
            for deck_key, deck in data[profile_key].decks.items()
            if deck_key not in get_existing_decks(profile_id)
        ]
        update_profile(profile_id, profile, decks_ids)

    else:  # New profile
        add_profile(profile)
