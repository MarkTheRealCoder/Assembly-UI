# GNOME Wayland tiling

This component reads the tiled state and resizable edges GNOME reports for the IDE's Wayland surface. Build it to enable square corners and resize only on the edges GNOME allows while the window is tiled. Maximized and fullscreen windows use the window states reported by Qt.

On Ubuntu 22.04, install the build dependencies if needed.

```sh
sudo apt install cmake g++ pkg-config qtbase5-private-dev libwayland-dev libwayland-bin
```

Build from the repository root, then launch the IDE as usual.

```sh
cmake -S source/interface/templates/window/native/gnome_tiling -B build/gnome-tiling
cmake --build build/gnome-tiling
```

The IDE loads `build/gnome-tiling/libassembly-gnome-tiling.so` in a Qt 5 Wayland session. The build uses Qt's platform interface from the Qt 5.15 private headers. Compositors without `gtk_shell1` version 4 and checkouts without the built component use the standard Qt window states.
