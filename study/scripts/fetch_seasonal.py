"""Download versioned ARCHER2 allocations and GB historic estimates into a user-specified cache."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

ALLOCATION_URL = 'https://zenodo.org/records/14284189/files/Archer2SummaryData.csv?download=1'
ALLOCATION_SHA256 = 'd9487c2332fdca43ddae73d9f0640487c0c7587da3090d1c29c1273b9a0ca509'
INTENSITY_URL = 'https://api.carbonintensity.org.uk/intensity'
FIRST_DAY = date(2021, 12, 1)
LAST_DAY = date(2022, 10, 16)


def grid_windows():
    start = FIRST_DAY
    while start < LAST_DAY:
        stop = min(start + timedelta(days=14), LAST_DAY)
        yield f'{INTENSITY_URL}/{start}T00:00Z/{stop}T00:00Z', f'grid-{start}-{stop}.json'
        start = stop


def fetch_one(url, output):
    if output.is_file():
        return
    tmp = output.with_suffix(output.suffix + '.part')
    req = Request(url, headers={'User-Agent': 'ARCHER2-seasonal-replay/1.0'})
    with urlopen(req, timeout=180) as response, tmp.open('wb') as dst:
        while block := response.read(1 << 20):
            dst.write(block)
    tmp.replace(output)


def checksum(path):
    digest = hashlib.sha256()
    with path.open('rb') as src:
        for block in iter(lambda: src.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def obtain_grid(cache):
    def one(spec):
        url, filename = spec
        fetch_one(url, cache / filename)
        assert json.loads((cache / filename).read_text())['data'], filename
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(one, grid_windows()))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('cache', type=Path)
    p.add_argument('--grid-only', action='store_true')
    args = p.parse_args()
    args.cache.mkdir(exist_ok=True, parents=True)
    obtain_grid(args.cache)
    if not args.grid_only:
        alloc = args.cache / 'Archer2SummaryData.csv'
        fetch_one(ALLOCATION_URL, alloc)
        if checksum(alloc) != ALLOCATION_SHA256:
            raise ValueError('Allocation file checksum differs from the cited v1.0 download.')
