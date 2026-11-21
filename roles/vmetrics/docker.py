from pyinfra.operations import apt, files, systemd

docker_excluded_packages = [
    "containerd",
    "docker-buildx",
    "docker-compose",
    "docker-doc",
    "docker.io",
    "podman-docker",
    "runc",
]

docker_packages = [
    "docker-ce",
    "docker-ce-cli",
    "containerd.io",
    "docker-buildx-plugin",
    "docker-compose-plugin",
]


def apply():
    apt.packages(
        name="Install GnuPG",
        packages=[
            "gnupg",
        ],
    )

    files.directory(
        name="Create apt keyrings directory",
        path="/etc/apt/keyrings",
        user="root",
        group="root",
        mode="0755",
    )

    apt.packages(
        name="Remove conflicting packages",
        packages=docker_excluded_packages,
        present=False,
    )

    apt.repo(
        name="Add docker repository",
        src="deb [signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian trixie stable",
        filename="docker",
    )

    apt.packages(
        name="Install Docker",
        packages=docker_packages,
    )

    systemd.service(
        name="Activate Docker",
        service="docker.service",
        enabled=True,
        running=True,
    )
