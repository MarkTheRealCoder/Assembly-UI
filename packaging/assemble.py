"""
Makes the release package from the PyInstaller output, the Java runtime and the licenses, then archives it.

    python packaging/assemble.py <target name, such as windows-x64>

It reads dist/ (PyInstaller), build/runtime (jlink) and build/licenses/python-packages.txt, and writes:
- package/AssemblyStdio/, the folder that users get
- release/AssemblyStdio-<target>.zip on Windows, .tar.gz on Linux, or .pkg on macOS

On macOS the folder holds only AssemblyStdio.app, with the runtime in Contents/Resources/runtime and the licenses
in Contents/Resources/licenses. The .pkg installer puts the app in /Applications. The installer is not signed:
macOS asks to confirm it once, in Privacy & Security, but the files that it installs are not in quarantine, so
the app then opens without warnings.
"""
import os
import plistlib
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
NAME = "AssemblyStdio"
TITLE = "Assembly Stdio"
BUNDLE_ID = "dev.assemblystdio.AssemblyStdio"
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
        # Inside the bundle, since the installer copies only the app to /Applications.
        copy_licenses(os.path.join(app, "Contents", "Resources", "licenses"))
        sign_macos_app(app)
        return os.path.join(app, "Contents", "MacOS", NAME)

    shutil.copytree(path("dist", NAME), package, symlinks=True, dirs_exist_ok=True)
    shutil.copytree(path("build", "runtime"), os.path.join(package, "runtime"), symlinks=True)
    copy_licenses(os.path.join(package, "licenses"))
    return os.path.join(package, f"{NAME}.exe" if WINDOWS else NAME)


def macos_installer(target: str, output: str) -> None:
    """ Makes an installer that puts AssemblyStdio.app in /Applications. """
    work = path("build", "pkg")
    shutil.rmtree(work, ignore_errors=True)
    resources = os.path.join(work, "resources")
    os.makedirs(resources)
    root = path("package", NAME)
    version = os.environ.get("APP_VERSION", "0.0.0")

    # A relocatable bundle would be installed over any copy of the app found elsewhere on the Mac.
    component_plist = os.path.join(work, "component.plist")
    subprocess.run(["pkgbuild", "--analyze", "--root", root, component_plist], check=True)
    with open(component_plist, "rb") as f:
        components = plistlib.load(f)
    for component in components:
        component["BundleIsRelocatable"] = False
    with open(component_plist, "wb") as f:
        plistlib.dump(components, f)

    component_pkg = os.path.join(work, f"{NAME}.pkg")
    subprocess.run([
        "pkgbuild", "--root", root, "--component-plist", component_plist, "--identifier", BUNDLE_ID,
        "--version", version, "--install-location", "/Applications", component_pkg,
    ], check=True)

    shutil.copy2(path("LICENSE"), os.path.join(resources, "LICENSE.txt"))
    with open(os.path.join(resources, "welcome.txt"), "w", encoding="utf-8") as f:
        f.write(f"{TITLE} {version}\n\n"
                f"This installer puts {TITLE} in the Applications folder. "
                f"It includes its own Java runtime, so nothing else needs to be installed.\n")
    # An Intel build also runs on Apple Silicon, through Rosetta.
    architectures = "arm64" if target.endswith("arm64") else "x86_64,arm64"
    distribution = os.path.join(work, "distribution.xml")
    with open(distribution, "w", encoding="utf-8") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
    <title>{TITLE}</title>
    <welcome file="welcome.txt"/>
    <license file="LICENSE.txt"/>
    <options customize="never" require-scripts="false" hostArchitectures="{architectures}"/>
    <domains enable_localSystem="true"/>
    <choices-outline>
        <line choice="{BUNDLE_ID}"/>
    </choices-outline>
    <choice id="{BUNDLE_ID}" visible="false">
        <pkg-ref id="{BUNDLE_ID}"/>
    </choice>
    <pkg-ref id="{BUNDLE_ID}" version="{version}" onConclusion="none">{NAME}.pkg</pkg-ref>
</installer-gui-script>
""")
    subprocess.run([
        "productbuild", "--distribution", distribution, "--resources", resources, "--package-path", work, output,
    ], check=True)


def archive(target: str) -> str:
    """ Archives package/AssemblyStdio, keeping the folder as the root of the archive, or makes the macOS installer. """
    release = path("release")
    shutil.rmtree(release, ignore_errors=True)
    os.makedirs(release)
    source = path("package", NAME)

    if MACOS:
        output = os.path.join(release, f"{NAME}-{target}.pkg")
        macos_installer(target, output)
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
