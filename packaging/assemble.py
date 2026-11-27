"""
Makes the release package from the PyInstaller output, the Java runtime and the licenses, then archives it.

    python packaging/assemble.py <target name, such as windows-x64>

It reads dist/ (PyInstaller), build/runtime (jlink) and build/licenses/python-packages.txt, and writes:
- package/AssemblyStdio/, the folder that users get
- release/AssemblyStdio-<target>.zip on Windows and macOS, or .tar.gz on Linux

On macOS the folder holds AssemblyStdio.app, with the runtime in Contents/Resources/runtime, and licenses/.
"""
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
NAME = "AssemblyStdio"
MACOS = sys.platform == "darwin"
WINDOWS = sys.platform == "win32"


def path(*parts: str) -> str:
    return os.path.join(ROOT, *parts)


def copy_licenses(destination: str) -> None:
    os.makedirs(destination, exist_ok=True)
    folder = path("packaging", "licenses")
    for name in os.listdir(folder):
        shutil.copy2(os.path.join(folder, name), destination)
    shutil.copy2(path("build", "licenses", "python-packages.txt"), destination)
    shutil.copy2(path("LICENSE"), os.path.join(destination, "AssemblyStdio-LICENSE.txt"))
    shutil.copy2(path("resources", "fonts", "JetBrainsMono", "OFL.txt"), os.path.join(destination, "JetBrainsMono-OFL.txt"))


def is_mach_o(location: str) -> bool:
    with open(location, "rb") as f:
        magic = f.read(4)
    # 64 and 32 bit Mach-O. Each runtime is thin: universal binaries would share CAFEBABE with Java classes.
    return magic in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf")


def sign_macos_app(app: str) -> None:
    """
    Signs the app bundle again, ad hoc, after the runtime was added to the bundle that PyInstaller signed.
    Apple Silicon runs only signed code, and a bundle whose seal no longer matches is reported as damaged.
    The libraries of the runtime are signed one by one; the bundle is then sealed without --deep, which would
    sign again the code that PyInstaller already signed.
    """
    runtime = os.path.join(app, "Contents", "Resources", "runtime")
    for folder, _dirs, files in os.walk(runtime):
        for name in files:
            full = os.path.join(folder, name)
            if not os.path.islink(full) and is_mach_o(full):
                subprocess.run(["codesign", "--force", "--sign", "-", full], check=True)
    subprocess.run(["codesign", "--force", "--sign", "-", app], check=True)
    subprocess.run(["codesign", "--verify", "--deep", "--strict", "--verbose=2", app], check=True)


def assemble() -> str:
    """ Builds package/AssemblyStdio and returns the path of the executable. """
    package = path("package", NAME)
    shutil.rmtree(path("package"), ignore_errors=True)
    os.makedirs(package)

    if MACOS:
        app = os.path.join(package, f"{NAME}.app")
        shutil.copytree(path("dist", f"{NAME}.app"), app, symlinks=True)
        shutil.copytree(path("build", "runtime"), os.path.join(app, "Contents", "Resources", "runtime"), symlinks=True)
        copy_licenses(os.path.join(package, "licenses"))
        sign_macos_app(app)
        return os.path.join(app, "Contents", "MacOS", NAME)

    shutil.copytree(path("dist", NAME), package, symlinks=True, dirs_exist_ok=True)
    shutil.copytree(path("build", "runtime"), os.path.join(package, "runtime"), symlinks=True)
    copy_licenses(os.path.join(package, "licenses"))
    return os.path.join(package, f"{NAME}.exe" if WINDOWS else NAME)


def archive(target: str) -> str:
    """ Archives package/AssemblyStdio, keeping the folder as the root of the archive. """
    release = path("release")
    shutil.rmtree(release, ignore_errors=True)
    os.makedirs(release)
    source = path("package", NAME)

    if MACOS:
        # ditto keeps the symbolic links and the attributes of the app bundle, as the Finder does.
        output = os.path.join(release, f"{NAME}-{target}.zip")
        subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", source, output], check=True)
    elif WINDOWS:
        output = os.path.join(release, f"{NAME}-{target}.zip")
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive_file:
            for folder, _dirs, files in os.walk(source):
                for name in files:
                    full = os.path.join(folder, name)
                    archive_file.write(full, os.path.relpath(full, os.path.dirname(source)))
    else:
        # A tar archive keeps the executable permission, which a ZIP made here would lose.
        output = os.path.join(release, f"{NAME}-{target}.tar.gz")
        with tarfile.open(output, "w:gz") as archive_file:
            archive_file.add(source, arcname=NAME)
    return output


def size_mb(location: str) -> float:
    if os.path.isfile(location):
        return os.path.getsize(location) / 2 ** 20
    total = 0
    for folder, _dirs, files in os.walk(location):
        for name in files:
            full = os.path.join(folder, name)
            if not os.path.islink(full):
                total += os.path.getsize(full)
    return total / 2 ** 20


def main() -> int:
    target = sys.argv[1]
    executable = assemble()
    if not os.path.isfile(executable):
        print(f"Executable not found: {executable}")
        return 1
    output = archive(target)
    print(f"Package: {size_mb(path('package', NAME)):.0f} MB, archive: {size_mb(output):.0f} MB")
    print(f"Archive: {output}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"archive={output}\n")
            f.write(f"executable={executable}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
