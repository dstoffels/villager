# This script updates the release asset download link in the database (meta) whenever a new release is published. This url is used to download the cities.tsv fixture when a user loads cities in their project.

import argparse
from localis.data import MetaStore
from localis import CityRegistry


def main(repo_url: str, release: str):
    url = f"{repo_url}/releases/download/{release}/cities.tsv"

    meta = MetaStore()
    meta.set(CityRegistry.META_URL_KEY, url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_url", type=str)
    parser.add_argument("release", type=str)

    args = parser.parse_args()

    main(args.repo_url, args.release)
