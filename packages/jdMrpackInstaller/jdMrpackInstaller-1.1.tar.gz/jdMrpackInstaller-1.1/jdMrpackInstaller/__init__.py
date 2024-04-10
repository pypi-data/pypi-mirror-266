from PyQt6.QtWidgets import QApplication, QWidget, QWizard, QWizardPage, QLabel, QLineEdit, QPushButton, QGroupBox, QListWidget, QListWidgetItem, QCheckBox, QProgressBar, QPlainTextEdit, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt, QThread, QTranslator, QLocale, QLibraryInfo, QCoreApplication, pyqtSignal
from PyQt6.QtGui import QIcon
import minecraft_launcher_lib
import traceback
import argparse
import sys
import os



def is_flatpak() -> bool:
    return os.path.isfile("/.flatpak-info")


class Environment():
    def __init__(self) -> None:
        self.minecraft_directory: str = minecraft_launcher_lib.utils.get_minecraft_directory()
        self.information: minecraft_launcher_lib.types.MrpackInformation = {}
        self.add_vanilla_launcher_profile: bool = False
        self.install_dependencies: bool = True
        self.optional_files: list[str] = []
        self.mrpack_path: str = ""
        self.install_path: str = ""

    def load_mrpack(self, path: str, parent: QWidget | None) -> bool:
        try:
            self.information = minecraft_launcher_lib.mrpack.get_mrpack_information(path)
        except FileNotFoundError:
            QMessageBox.critical(parent, QCoreApplication.translate("Environment", "File not found"), QCoreApplication.translate("Environment", "{{path}} was not found").replace("{{path}}", path))
            return False
        except Exception:
            QMessageBox.critical(parent, QCoreApplication.translate("Environment", "Invalid file"), QCoreApplication.translate("Environment", "{{path}} is not a valid Modrinth modpack").replace("{{path}}", path))
            return False

        self.mrpack_path = path
        return True


class InstallThread(QThread):
    progress_max = pyqtSignal("int")
    progress = pyqtSignal("int")
    text = pyqtSignal("QString")

    def __init__(self, env: Environment) -> None:
        QThread.__init__(self)

        self.is_ok = True
        self._env = env

        self._callback_dict = {
            "setStatus": lambda text: self.text.emit(text),
            "setMax": lambda max_progress: self.progress_max.emit(max_progress),
            "setProgress": lambda progress: self.progress.emit(progress),
        }

    def run(self) -> None:
        try:
            minecraft_launcher_lib.mrpack.install_mrpack(self._env.mrpack_path, self._env.minecraft_directory, self._env.install_path, callback=self._callback_dict, mrpack_install_options={"optionalFiles": self._env.optional_files, "skipDependenciesInstall": not self._env.install_dependencies})
        except Exception:
             print(traceback.format_exc(), end="", file=sys.stderr)
             self.is_ok = False


class WelcomePage(QWizardPage):
    def __init__(self, env: Environment) -> None:
        super().__init__()

        self._env = env

        text = "<b>" + QCoreApplication.translate("WelcomePage", "Welcome") + "</b><br><br>"
        text += QCoreApplication.translate("WelcomePage", "jdMrpackInstaller installs Modpacks that you've download from Modrinth for you, so you don't need a special Launcher") + "<br><br>"
        text += QCoreApplication.translate("WelcomePage", "To get started, select an .mrpack file") + "<br><br>"

        label = QLabel(text)
        self._path_edit = QLineEdit()
        browse_button = QPushButton(QCoreApplication.translate("WelcomePage", "Browse"))

        label.setWordWrap(True)

        if is_flatpak():
            self._path_edit.setReadOnly(True)

        self._path_edit.textChanged.connect(lambda: self.completeChanged.emit())
        browse_button.clicked.connect(self._browse_button_clicked)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self._path_edit)
        path_layout.addWidget(browse_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addLayout(path_layout)

        self.setLayout(main_layout)

    def _browse_button_clicked(self) -> None:
        filter = QCoreApplication.translate("WelcomePage", "Modrinth modpacks") + " (*.mrpack);;" +   QCoreApplication.translate("WelcomePage", "All Files") + " (*)"

        path = QFileDialog.getOpenFileName(self, directory=self._path_edit.text(), filter=filter)[0]

        if path == "":
            return

        self._path_edit.setText(path)

    def validatePage(self) -> bool:
        return self._env.load_mrpack(self._path_edit.text().strip(), self)

    def isComplete(self) -> bool:
        return self._path_edit.text().strip() != ""


class InformationPage(QWizardPage):
    def __init__(self, env: Environment) -> None:
        super().__init__()

        self._env = env

        self._text_label = QLabel()
        self._optional_box = QGroupBox()
        self._optional_list = QListWidget()

        self._optional_box.setTitle(QCoreApplication.translate("InformationPage", "Optional files"))

        optional_label = QLabel(QCoreApplication.translate("InformationPage", "This Modpacks contains some optional files. Select which of them you want to install."))
        optional_label.setWordWrap(True)

        optional_layout = QVBoxLayout()
        optional_layout.addWidget(optional_label)
        optional_layout.addWidget(self._optional_list)

        self._optional_box.setLayout(optional_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._text_label)
        main_layout.addWidget(self._optional_box)

        self.setLayout(main_layout)

    def initializePage(self) -> None:
        text = QCoreApplication.translate("InformationPage", "This file includes the following Modpack:") + "<br><br>"
        text += QCoreApplication.translate("InformationPage", "Name:") + " "
        text += self._env.information["name"] + "<br>"

        if self._env.information["summary"] != "":
            text += QCoreApplication.translate("InformationPage", "Summary:") + " "
            text += self._env.information["summary"] + "<br>"

        text += QCoreApplication.translate("InformationPage", "Minecraft version:") + " "
        text += self._env.information["minecraftVersion"] + "<br>"
        self._text_label.setText(text)

        if len(self._env.information["optionalFiles"]) == 0:
            self._optional_box.setVisible(False)
            return

        self._optional_list.clear()
        for i in self._env.information["optionalFiles"]:
            item = QListWidgetItem(i)
            item.setCheckState(Qt.CheckState.Unchecked)
            self._optional_list.addItem(item)

    def validatePage(self) -> bool:
        for i in range(self._optional_list.count()):
            item = self._optional_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self._env.optional_files.append(item.text())
        return True


class InstallPage(QWizardPage):
    def __init__(self, env: Environment) -> None:
        super().__init__()

        self._env = env

        self._path_edit = QLineEdit()
        browse_button = QPushButton(QCoreApplication.translate("InstallPage", "Browse"))
        self._install_dependencies_check_box = QCheckBox(QCoreApplication.translate("InstallPage", "Install needed Minecraft version and Modloader"))
        self._add_vanilla_launcher_profile_check_box = QCheckBox(QCoreApplication.translate("InstallPage", "Add Profile to Launcher"))

        self._path_edit.setText(env.minecraft_directory)
        self._install_dependencies_check_box.setChecked(True)
        self._add_vanilla_launcher_profile_check_box.setEnabled(minecraft_launcher_lib.vanilla_launcher.do_vanilla_launcher_profiles_exists(env.minecraft_directory))

        if is_flatpak():
            self._path_edit.setReadOnly(True)

        browse_button.clicked.connect(self._browse_button_clicked)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self._path_edit)
        path_layout.addWidget(browse_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(QCoreApplication.translate("InstallPage", "Choose the directory where you want to install this modpack")))
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self._install_dependencies_check_box)
        main_layout.addWidget(self._add_vanilla_launcher_profile_check_box)

        self.setLayout(main_layout)

    def _browse_button_clicked(self) -> None:
        path = QFileDialog.getExistingDirectory(self, directory=self._path_edit.text().strip())

        if path == "":
            return

        self._path_edit.setText(path)

    def validatePage(self) -> bool:
        path = self._path_edit.text().strip()

        if not os.path.isdir(path):
            QMessageBox.critical(self, QCoreApplication.translate("InstallPage", "Not a Directory"), QCoreApplication.translate("InstallPage", "{{path}} is not a Directory").replace("{{path}}", path))
            return False

        self._env.install_path = path
        self._env.install_dependencies = self._install_dependencies_check_box.isChecked()
        self._env.add_vanilla_launcher_profile= self._add_vanilla_launcher_profile_check_box.isChecked()
        return True


class ProgressPage(QWizardPage):
    def __init__(self, env: Environment) -> None:
        super().__init__()

        self._install_thread = InstallThread(env)
        self._env = env

        self._progress_bar = QProgressBar()
        self._text_output = QPlainTextEdit()

        self._text_output.setReadOnly(True)

        self._install_thread.progress_max.connect(lambda maximum: self._progress_bar.setMaximum(maximum))
        self._install_thread.progress.connect(lambda value: self._progress_bar.setValue(value))
        self._install_thread.finished.connect(self._installation_finished)
        self._install_thread.text.connect(self._write_text)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(QCoreApplication.translate("ProgressPage", "jdMrpackInstaller is installing your modpack. Please wait ...")))
        main_layout.addWidget(self._progress_bar)
        main_layout.addWidget(self._text_output)

        self.setLayout(main_layout)

    def _write_text(self, text: str) -> None:
        cursor = self._text_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text + "\n")
        self._text_output.moveCursor(cursor.MoveOperation.End)

    def _installation_finished(self) -> None:
        if not self._install_thread.is_ok:
            QMessageBox.critical(self, QCoreApplication.translate("ProgressPage", "Error"), QCoreApplication.translate("ProgressPage", "An error occurred while installing the modpack. There may be an error in the modpack."))
            sys.exit(0)

        if self._env.add_vanilla_launcher_profile:
            profile: minecraft_launcher_lib.types.VanillaLauncherProfile = {}
            profile["name"] = self._env.information["name"]
            profile["version"] = minecraft_launcher_lib.mrpack.get_mrpack_launch_version(self._env.mrpack_path)
            profile["versionType"] = "custom"
    
            if self._env.install_path != self._env.minecraft_directory:
                profile["gameDirectory"] = self._env.install_path

            minecraft_launcher_lib.vanilla_launcher.add_vanilla_launcher_profile(self._env.minecraft_directory, profile)

        self.completeChanged.emit()

    def initializePage(self) -> None:
        self._install_thread.start()

    def isComplete(self) -> bool:
        return self._install_thread.isFinished()


class FinishedPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()

        text = "<b>" + QCoreApplication.translate("FinishedPage", "All done!") + "</b><br><br>"
        text += QCoreApplication.translate("FinishedPage", "Your modpack has been successfully installed")

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(text))

        self.setLayout(main_layout)


class MrpackWizard(QWizard):
    def __init__(self, env: Environment) -> None:
        super().__init__()

        if env.mrpack_path == "":
            self.addPage(WelcomePage(env))

        self.addPage(InformationPage(env))
        self.addPage(InstallPage(env))
        self.addPage(ProgressPage(env))
        self.addPage(FinishedPage())

        self.setButtonLayout((QWizard.WizardButton.Stretch, QWizard.WizardButton.NextButton, QWizard.WizardButton.FinishButton))

        self.setWindowTitle("jdMrpackInstaller")


class WizardWrapper(QWidget):
    def __init__(self) -> None:
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.addWidget(MrpackWizard())

        self.setLayout(main_layout)


def main() -> None:
    app = QApplication(sys.argv)

    env = Environment()
    program_dir = os.path.dirname(__file__)

    app.setDesktopFileName("page.codeberg.JakobDev.jdMrpackInstaller")
    app.setWindowIcon(QIcon(os.path.join(program_dir, "Icon.png")))
    app.setApplicationName("jdMrpackInstaller")

    qt_translator = QTranslator()
    app_translator = QTranslator()
    system_language = QLocale.system().name().split("_")[0]
    qt_translator.load(os.path.join(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath), "qt_" + system_language + ".qm"))
    app_translator.load(os.path.join(program_dir, "translations", "jdMrpackInstaller_" + system_language + ".qm"))
    app.installTranslator(app_translator)
    app.installTranslator(qt_translator)

    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs='?')
    parser.add_argument("--minecraft-dir", help="Set a custom Minecraft directory")
    args = parser.parse_known_args()[0]

    if args.file is not None:
        env.load_mrpack(args.file, None)

    if args.minecraft_dir is not None:
        env.minecraft_dir = args.minecraft_dir

    w = MrpackWizard(env)
    w.show()

    sys.exit(app.exec())
