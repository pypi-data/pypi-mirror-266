from . import logger
import requests
import tqdm
import os
import crm1


__all__ = (
    "BLOCK_SIZE",
    "download",
    "get_data",
    "get_json",
    "download_crm1_mod",
)


BLOCK_SIZE = 1024


def download(url: str, dest: str):
    stream = requests.get(url, stream = True)
    size = int(stream.headers.get("content-length", 0))

    logger.debug("Downloading: " + url)

    with tqdm.tqdm(total = size, unit = "B", unit_scale = True) as bar:
        folder = dest.removesuffix("/" + dest.split("/")[-1])
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        with open(dest, "wb") as file:
            for data in stream.iter_content(BLOCK_SIZE):
                bar.update(len(data))
                file.write(data)

    if size != 0 and bar.n != size:
        logger.warn("Failed to download file: " + url)


def get_data(url: str) -> str:
    return requests.get(url).text


def get_json(url: str) -> dict:
    return requests.get(url).json()


def download_crm1_mod(repo: str, mod: str, dest_folder: str):
    # TODO: When/if https://github.com/CRModders/CRM-1/pull/3 is pulled the get_all_repos call should not be required.
    pool = crm1.make_pool(crm1.autorepotools.get_all_repos())
    pool.add_repository(repo)

    mod = pool.get_mod(mod)

    if mod is None:
        logger.error(f"Failed to find mod '{mod}' in repo '{repo}'")
        return

    download(mod.meta.url, os.path.join(dest_folder, mod.id + ".jar"))

    for dep_data in mod.depends:
        dep = dep_data.resolve(pool)
        download(dep.meta.url, dest)
