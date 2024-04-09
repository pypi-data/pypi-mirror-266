from . import api
from .api.instance import Instance
from .api import paths
from .api import logger
from .api import net
from .api import versions
import sys
import click
import os
import send2trash
import shutil


@click.group()
def cosmix():
    pass


@cosmix.command()
def version():
    logger.info("Cosmix " + api.VERSION)


@cosmix.command()
def debug():
    logger.info("Cosmix " + api.VERSION)
    logger.info("Paths:")
    logger.info("  Local Path: " + paths.LOCAL_PATH)
    logger.info("  Work Dir:   " + paths.WORK_DIR)
    logger.info("  Instances:  " + paths.INSTANCES)
    logger.info("  Deps:       " + paths.DEPS)
    logger.info("Latest Available Versions: (these may take a second)")
    logger.info("  Cosmic Reach: " + versions.get_latest_of("reach"))
    logger.info("  Cosmic Quilt: " + versions.get_latest_of("quilt"))


@cosmix.command()
@click.option("--version", "-v", default="latest", type=str, help="The version of Cosmic Reach to use. Defaults to 'latest'")
@click.option("--quilt-version", "-q", default="none", type=str, help="The Cosmic Quilt version to use.")
@click.argument("name")
def add(version: str, quilt_version: str, name: str):
    if Instance.exists(name):
        logger.error("Instance already exists.")
        exit(1)
    Instance.make_instance(name, version, None if quilt_version == "none" else quilt_version).download()
    logger.info("Made instance " + name)


@cosmix.command()
@click.option("--version", "-v", default="none", type=str, help="The version of Cosmic Reach to update to. Defaults to 'none'")
@click.option("--quilt-version", "-q", default="none", type=str, help="The Cosmic Quilt version to update to. Defaults to 'none'")
@click.argument("name")
def update(version: str, quilt_version: str, name: str):
    instance = Instance.get_or_throw(name)

    if version != "none":
        instance.version = versions.get_version_or_latest_of("reach", version)
    if quilt_version != "none":
        instance.quilt_version = versions.get_version_or_latest_of("quilt", quilt_version)

    instance.save()
    instance.download(is_updating = True)

    logger.info("Updated instance " + name)


@cosmix.command()
@click.argument("name")
def launch(name: str):
    Instance.from_config_file(name).launch()


@cosmix.command()
def instances():
    if not os.path.exists(paths.INSTANCES) or len(os.listdir(paths.INSTANCES)) <= 0:
        logger.error("No instances found.")
        exit(0)

    for instance_name in os.listdir(paths.INSTANCES):
        instance = Instance.get_or_throw(instance_name)
        s = f" - {instance.name} ({instance.version})"
        if instance.quilt_version is not None:
            s += f" (Quilt: {instance.quilt_version})"
        print(s)


@cosmix.command()
@click.argument("name")
def trash(name: str):
    instance = Instance.get_or_throw(name)
    send2trash.send2trash(instance.path)


@cosmix.command()
@click.argument("name")
def info(name: str):
    i = Instance.get_or_throw(name)
    print("Instance: " + i.name + (" (modded)" if i.is_modded() else ""))
    print("Path:     " + i.path.replace(os.path.expanduser("~"), "~", 1))
    print("Version:  " + i.version)
    if i.is_modded():
        print("Quilt:    " + i.quilt_version)
        mods = i.get_mods()
        if (l := len(mods)) > 0:
            print(f"{l} Mods:")
            for mod in mods:
                print(f"  - {mod}")


@cosmix.command("add-mod")
@click.argument("name")
@click.argument("mod", type=click.Path(exists = True))
def add_mod(name: str, mod):
    i = Instance.get_or_throw(name)
    if not i.is_modded():
        logger.error("Instance is not modded")
        exit(1)

    os.makedirs(i.path + "/mods/", exist_ok = True)
    shutil.copyfile(mod, i.path + "/mods/" + mod.split("/")[-1])


@cosmix.command("add-crm1-mod")
@click.argument("name")
@click.argument("repo")
@click.argument("mod")
def add_crm1_mod(name: str, repo: str, mod: str):
    i = Instance.get_or_throw(name)

    if not i.is_modded():
        logger.error("Instance is not modded")
        exit(1)

    os.makedirs(i.path + "/mods/", exist_ok = True)
    net.download_crm1_mod(repo, mod, i.path + "/mods/")


if __name__ == "__main__":
    cosmix()
