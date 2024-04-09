from . import paths
import hjson
import os


__all__ = (
    "DEFAULT_CONFIG",
    "get_config"
)


DEFAULT_CONFIG = """\
{
    logging: {
        # Valid values for sanatization_mode:
        # 'sanatize' - Replace username with SANATIZED_USERNAME
        # 'replace' - Replace path to home with ~
        # 'none' - No sanatization
        sanatization_mode: replace

        # No, it's not a random value. See this: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        sanatized_username: dQw4w9WgXcQ

        # Colors!
        colored_logs: true
    }

    crm1: {
        # If JoJoJux's autorepo mapping should be used (https://crm-repo.jojojux.de/repo_mapping.json)
        use_autorepo_mapping: true

        # Default repos to apply
        default_repos: [
            "https://crm-repo.jojojux.de/repo.json"
        ]
    }
}"""
_CACHED_CONFIG = None


def get_config() -> dict:
    global _CACHED_CONFIG
    if not os.path.exists(paths.WORK_DIR):
        os.makedirs(paths.WORK_DIR, exist_ok = True)

    path = os.path.join(paths.WORK_DIR, "config.hjson")
    if not os.path.isfile(path):
        with open(path, "w") as fp:
            fp.write(DEFAULT_CONFIG)

    if _CACHED_CONFIG is None:
        with open(path, "r") as fp:
            _CACHED_CONFIG = hjson.load(fp)

    return _CACHED_CONFIG
