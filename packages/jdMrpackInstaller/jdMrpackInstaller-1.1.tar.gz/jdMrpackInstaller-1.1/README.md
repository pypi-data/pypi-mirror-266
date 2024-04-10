<h1 align="center">jdMrpackInstaller</h1>

<h3 align="center">Install Modrinth modpacks</h3>

<p align="center">
    <img alt="jdMrpackInstaller" src="screenshots/WelcomePage.png"/>
</p>

With jdMrpackInstaller you can install modpacks that you've downloaded from Modrinth (.mrpack) with just a few clicks in an easy to use GUI.
That means you no longer need a special launcher to use your favourite modpack.

## Install

### Flatpak
You can get jdMrpackInstaller from [Flathub](https://flathub.org/apps/page.codeberg.JakobDev.jdMrpackInstaller)

### AUR
Arch Users can get jdMrpackInstaller from the [AUR](https://aur.archlinux.org/packages/jdMrpackInstaller)

### SourceForge
You can get Windows and AppImage Builds from [SourceForge](https://sourceforge.net/projects/jdmrpackinstaller)

### pip
You can install jdMrpackInstaller from [PyPI](https://pypi.org/project/jdMrpackInstaller) using `pip`:
```shell
pip install jdMrpackInstaller
```
Using this Method, it will not include a Desktop Entry or any other Data file, so you need to run jdMrpackInstaller from the Command Line.
Use this only, when nothing else works.

### From source
This is only for experienced Users and someone, who wants to package jdMrpackInstaller for a Distro.
jdMrpackInstallershould be installed as a Python package.
You can use `pip` or any other tool that can handle Python packages.
YOu need to have `lrelease` installed to build the Package.
After that, you should run `install-unix-datafiles.py` which wil install things like the Desktop Entry or the Icon in the correct place.
It defaults to `/usr`, but you can change it with the `--prefix` argument.
It also applies the translation to this files.
You need gettext installed to run `install-unix-datafiles.py`.

Here's a example of installing jdMrpackInstaller into `/usr/local`:
```shell
sudo pip install --prefix /usr/local .
sudo ./install-unix-datafiles.py --prefix /usr/local
```

## Translate
You can help translating jdMrpackInstaller on [Codeberg Translate](https://translate.codeberg.org/projects/jdMrpackInstaller)

## Develop
jdMrpackInstalleris written in Python and uses PyQt6 as GUI toolkit. You should have some experience in both.
You can run `jdMrpackInstaller.py`to start jdMrpackInstaller from source and test your local changes.
It ships with a few scripts in the tools directory that you need to develop.

#### BuildTranslations.py
This script takes all `.ts` files and compiles it to `.qm` files.
The `.ts` files are containing the translation source and are being used during the translation process.
The `.qm` contains the compiled translation and are being used by the Program.
You need to compile a `.ts` file to a `.qm` file to see the translations in the Program.

#### UpdateTranslations.py
This regenerates the `.ts` files. You need to run it, when you changed something in the source code.
The `.ts` files are contains the line in the source, where the string to translate appears,
so make sure you run it even when you don't changed a translatable string, so the location is correct.

####  UpdateUnixDataTranslations.py
This regenerates the translation files in `deploy/translations`. these files contains the translations for the Desktop Entry and the AppStream File.
It uses gettext, as it is hard to translate this using Qt.
These files just exists to integrate the translation with Weblate, because Weblate can't translate the Desktop Entry and the AppStream file.
Make sure you run this when you edited one of these files.
You need to have gettext installed to use it.
