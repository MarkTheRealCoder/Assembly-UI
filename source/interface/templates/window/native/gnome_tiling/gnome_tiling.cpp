#include <QGuiApplication>
#include <QPlatformSurfaceEvent>
#include <QVariant>
#include <QWindow>
#include <qpa/qplatformnativeinterface.h>

#include <cstddef>
#include <cstring>
#include <wayland-client.h>

#include "gtk-shell-client-protocol.h"

namespace {
constexpr auto monitorName = "AssemblyGnomeTiling";
constexpr auto tiledProperty = "gnomeTiled";

class GnomeTilingMonitor final : public QObject {
public:
    GnomeTilingMonitor(QWindow *window, QPlatformNativeInterface *native, wl_display *display)
        : QObject(window), window_(window), native_(native), registry_(wl_display_get_registry(display))
    {
        setObjectName(QLatin1String(monitorName));
        window_->installEventFilter(this);
        static const wl_registry_listener listener = {globalAdded, globalRemoved};
        wl_registry_add_listener(registry_, &listener, this);
    }

    ~GnomeTilingMonitor() override
    {
        releaseSurface();
        if (shell_)
            gtk_shell1_destroy(shell_);
        wl_registry_destroy(registry_);
    }

private:
    bool eventFilter(QObject *, QEvent *event) override
    {
        if (event->type() == QEvent::Expose && window_->isExposed()) {
            watchSurface();
        } else if (event->type() == QEvent::Hide ||
                   (event->type() == QEvent::PlatformSurface &&
                    static_cast<QPlatformSurfaceEvent *>(event)->surfaceEventType() ==
                        QPlatformSurfaceEvent::SurfaceAboutToBeDestroyed)) {
            releaseSurface();
            setTiled(false);
        }
        return false;
    }

    void watchSurface()
    {
        if (!shell_ || surface_ || !window_->isVisible())
            return;
        auto *surface = static_cast<wl_surface *>(native_->nativeResourceForWindow("surface", window_));
        if (!surface)
            return;

        surface_ = gtk_shell1_get_gtk_surface(shell_, surface);
        if (surface_) {
            static const gtk_surface1_listener listener = {configured, ignoreEdges};
            gtk_surface1_add_listener(surface_, &listener, this);
        }
    }

    void releaseSurface()
    {
        if (surface_) {
            gtk_surface1_release(surface_);
            surface_ = nullptr;
        }
    }

    void setTiled(bool tiled)
    {
        if (window_->property(tiledProperty).toBool() != tiled)
            window_->setProperty(tiledProperty, tiled);
    }

    static void globalAdded(void *data, wl_registry *registry, uint32_t name, const char *interface, uint32_t version)
    {
        auto *monitor = static_cast<GnomeTilingMonitor *>(data);
        constexpr uint32_t protocolVersion = GTK_SURFACE1_RELEASE_SINCE_VERSION;
        if (monitor->shell_ || version < protocolVersion || std::strcmp(interface, gtk_shell1_interface.name) != 0)
            return;

        monitor->shell_ = static_cast<gtk_shell1 *>(wl_registry_bind(registry, name, &gtk_shell1_interface, protocolVersion));
        if (monitor->shell_) {
            monitor->shellName_ = name;
            static const gtk_shell1_listener listener = {ignoreCapabilities};
            gtk_shell1_add_listener(monitor->shell_, &listener, monitor);
            monitor->watchSurface();
        }
    }

    static void globalRemoved(void *data, wl_registry *, uint32_t name)
    {
        auto *monitor = static_cast<GnomeTilingMonitor *>(data);
        if (monitor->shell_ && monitor->shellName_ == name) {
            monitor->releaseSurface();
            gtk_shell1_destroy(monitor->shell_);
            monitor->shell_ = nullptr;
            monitor->setTiled(false);
        }
    }

    static void configured(void *data, gtk_surface1 *, wl_array *states)
    {
        auto *monitor = static_cast<GnomeTilingMonitor *>(data);
        const auto *values = static_cast<const uint32_t *>(states->data);
        for (std::size_t i = 0; i < states->size / sizeof(*values); ++i) {
            if (values[i] >= GTK_SURFACE1_STATE_TILED && values[i] <= GTK_SURFACE1_STATE_TILED_LEFT) {
                monitor->setTiled(true);
                return;
            }
        }
        monitor->setTiled(false);
    }

    static void ignoreCapabilities(void *, gtk_shell1 *, uint32_t) {}
    static void ignoreEdges(void *, gtk_surface1 *, wl_array *) {}

    QWindow *const window_;
    QPlatformNativeInterface *const native_;
    wl_registry *const registry_;
    gtk_shell1 *shell_ = nullptr;
    gtk_surface1 *surface_ = nullptr;
    uint32_t shellName_ = 0;
};
}

extern "C" Q_DECL_EXPORT void assembly_watch_gnome_tiling(QWindow *window)
{
    if (window->findChild<QObject *>(QLatin1String(monitorName), Qt::FindDirectChildrenOnly))
        return;
    auto *native = QGuiApplication::platformNativeInterface();
    if (!native)
        return;
    auto *display = static_cast<wl_display *>(native->nativeResourceForIntegration("wl_display"));
    if (display)
        new GnomeTilingMonitor(window, native, display);
}
