import subprocess
import os


__all__ = (
    "QUILT_POM",
    "copy_deps",
    "make_pom",
)


QUILT_POM = """\
<?xml version="1.0" encoding="UTF-8"?>
<project
    xmlns="http://maven.apache.org/POM/4.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.foo</groupId>
  <artifactId>bar</artifactId>
  <version>0.0.1-SNAPSHOT</version>

  <repositories>
    <repository>
      <id>jitpack</id>
      <name>Jitpack</name>
      <url>https://jitpack.io</url>
    </repository>
    <repository>
      <id>quilt</id>
      <name>Quilt</name>
      <url>https://maven.quiltmc.org/repository/release/</url>
    </repository>
    <repository>
      <id>fabric</id>
      <name>Fabric</name>
      <url>https://maven.fabricmc.net/</url>
    </repository>
    <repository>
      <id>sponge</id>
      <name>Sponge</name>
      <url>https://repo.spongepowered.org/maven/</url>
    </repository>
  </repositories>

  <dependencies>
    <dependency>
      <groupId>org.codeberg.CRModders</groupId>
      <artifactId>cosmic-quilt</artifactId>
      <version>%s</version>
    </dependency>
  </dependencies>

  <build>
    <directory>lib</directory>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-dependency-plugin</artifactId>
        <configuration>
          <excludeGroupIds>finalforeach</excludeGroupIds>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
"""


def copy_deps(of: str, dest: str):
    old = os.getcwd()
    os.chdir(of)
    subprocess.run(["mvn", "dependency:copy-dependencies", "-DoutputDirectory=" + dest, "-Dsilent=true"])
    os.chdir(old)


def make_pom(dest: str, quilt_version: str):
    with open(dest, "w") as f:
        f.write(QUILT_POM % quilt_version)
