from subprocess import check_call
import setuptools
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        check_call(
            "cd aup_manager/static && npm install && npm run compile_sass", shell=True
        )
        install.run(self)


setuptools.setup(
    name="aup_manager",
    python_requires=">=3.9",
    url="https://gitlab.ics.muni.cz/perun/perun-proxyidp/aup-manager.git",
    description="app for management of acceptable use policies with API for approving them",
    include_package_data=True,
    package_data={"": ["openapi-specification.yaml"]},
    packages=setuptools.find_packages(),
    install_requires=[
        "setuptools",
        "pymongo==4.6.1",  # for compatibility with proxyidp-gui
        "jsonpatch==1.33",
        "connexion[swagger-ui]==2.14.2",
        "markdown2==2.4.12",
        "Flask-pyoidc==3.14.3",
        "jwcrypto==1.5.1",
    ],
    extras_require={
        "perun": ["perun.connector==3.8.1"],
    },
    cmdclass={
        "install": PostInstallCommand,
    },
)
