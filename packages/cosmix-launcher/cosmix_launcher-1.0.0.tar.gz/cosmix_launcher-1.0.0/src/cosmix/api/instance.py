from . import paths
from . import net
from . import maven
from . import logger
from . import mod
from . import versions
from typing import Optional
import hjson
import os
import re
import java_manifest
import shutil


__all__ = (
    "VALID_INSTANCE_NAME",
    "COSMIC_ARCHIVE_RAW_URL",
    "COSMIC_QUILT_ARGS",
    "Instance",
)


VALID_INSTANCE_NAME = re.compile(r"[a-zA-Z0-9_-]*")
COSMIC_ARCHIVE_RAW_URL = "https://raw.githubusercontent.com/CRModders/CosmicArchive/main"
COSMIC_QUILT_ARGS = [
    "-classpath",
    "./deps/*",
    "org.quiltmc.loader.impl.launch.knot.KnotClient"
]


class Instance:
    def __init__(self, instance_name: str, cosmic_reach_version: str, args: list[str], quilt_version: Optional[str] = None):
        self.name = instance_name
        self.version = cosmic_reach_version
        self.args = args
        self.quilt_version = quilt_version
        self.path = os.path.join(paths.INSTANCES, self.name)

    def is_modded(self) -> bool:
        return self.quilt_version is not None

    def path_to(self, path: str) -> str:
        return os.path.join(self.path, path)

    def launch(self):
        os.chdir(self.path)

        args = ["java"]
        if not self.is_modded():
            args.extend(["-jar", paths.path_to_cr(self.version)])
        else:
            args.append("-Dloader.gameJarPath=" + paths.path_to_cr(self.version))
            args.extend(COSMIC_QUILT_ARGS)
        args.extend(self.args)

        logger.info(f"Launching \"{self.name}\" with args {args} in folder {self.path}")
        os.execvp("java", args)

    def download(self, is_updating: bool = False):
        cr_path = paths.path_to_cr(self.version)
        if not os.path.isfile(cr_path):
            net.download(f"{COSMIC_ARCHIVE_RAW_URL}/Cosmic Reach-{self.version}.jar", cr_path)

        if self.is_modded():
            logger.info("Downloading Cosmic Quilt dependencies...")

            pom = self.path_to("pom.xml")
            deps = self.path_to("deps/")
            had_existing_pom = True
            if not os.path.isfile(pom):
                maven.make_pom(pom, self.quilt_version)
                had_existing_pom = False
            if is_updating and os.path.exists(deps):
                shutil.rmtree(deps)
            maven.copy_deps(self.path, deps)
            if not had_existing_pom:
                os.remove(pom)

            self.save()

    def save(self):
        os.makedirs(self.path, exist_ok = True)
        with open(self.path_to("config.hjson"), "w") as f:
            hjson.dump(Instance.get_hjson(self), f)

    def get_mods(self) -> list[str]:
        mods = []
        mods_dir = self.path_to("mods/")
        if os.path.exists(mods_dir):
            for mod_file in os.listdir(mods_dir):
                manifest = java_manifest.from_jar(os.path.join(mods_dir, mod_file))
                mods.append(mod.Mod.from_data(manifest, mod_file))
        return mods

    # Static Methods
    @staticmethod
    def from_config_file(instance_name: str) -> "Instance":
        data = None
        path = os.path.join(paths.INSTANCES, instance_name, "config.hjson")
        with open(path, "r") as f:
            data = hjson.load(f)
        if data is None:
            logger.error(f"Failed to load config at {path}")
            exit(1)

        ins = Instance(data["name"], data["version"], data["args"])
        if "quilt-version" in data:
            ins.quilt_version = data["quilt-version"]

        return ins

    @staticmethod
    def make_instance(instance_name: str, cosmic_reach_version: str, quilt_version: Optional[str] = None) -> "Instance":
        if not VALID_INSTANCE_NAME.match(instance_name):
            logger.error("Instance name must match `[a-zA-Z0-9_-]*`")
            exit(1)

        cosmic_reach_version = versions.get_version_or_latest_of("reach", cosmic_reach_version)
        quilt_version = versions.get_version_or_latest_of("quilt", quilt_version)

        path = paths.INSTANCES + instance_name
        os.makedirs(path, exist_ok = True)

        instance = Instance(instance_name, cosmic_reach_version, [], quilt_version)
        instance.save()
        return instance

    @staticmethod
    def get_hjson(instance: "Instance") -> dict:
        d = {
            "name": instance.name,
            "version": instance.version,
            "args": instance.args
        }
        if instance.is_modded():
            d["quilt-version"] = instance.quilt_version
        return d

    @staticmethod
    def exists(instance_name: str) -> bool:
        return os.path.exists(os.path.join(paths.INSTANCES, instance_name))

    @staticmethod
    def get_or_throw(instance_name: str) -> Optional["Instance"]:
        if not Instance.exists(instance_name):
            logger.error("Instance does not exist.")
            exit(1)
        return Instance.from_config_file(instance_name)
