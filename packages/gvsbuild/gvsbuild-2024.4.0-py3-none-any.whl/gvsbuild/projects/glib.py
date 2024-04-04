#  Copyright (C) 2016 The Gvsbuild Authors
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.

from gvsbuild.utils.base_builders import Meson
from gvsbuild.utils.base_expanders import NullExpander, Tarball
from gvsbuild.utils.base_project import Project, project_add


@project_add
class GLibBase(Tarball, Meson):
    def __init__(self):
        Meson.__init__(
            self,
            "glib-base",
            version="2.80.0",
            lastversion_even=True,
            repository="https://gitlab.gnome.org/GNOME/glib",
            archive_url="https://download.gnome.org/sources/glib/{major}.{minor}/glib-{version}.tar.xz",
            hash="8228a92f92a412160b139ae68b6345bd28f24434a7b5af150ebe21ff587a561d",
            dependencies=[
                "ninja",
                "meson",
                "pkgconf",
                "gettext",
                "libffi",
                "zlib",
                "pcre2",
            ],
            patches=[
                "001-glib-package-installation-directory.patch",
                # https://gitlab.gnome.org/GNOME/gobject-introspection/-/issues/499
                "002-gir-scanner-dll-not-found.patch",
            ],
        )
        self.add_param("-Dman-pages=disabled")
        self.add_param("-Dtests=false")
        self.add_param("-Ddocumentation=false")
        self.add_param("-Dintrospection=disabled")

    def build(self):
        Meson.build(self)
        self.install(r".\LICENSES\* share\doc\glib")


@project_add
class GLib(Tarball, Meson):
    def __init__(self):
        Meson.__init__(
            self,
            "glib",
            version="2.80.0",
            lastversion_even=True,
            repository="https://gitlab.gnome.org/GNOME/glib",
            archive_url="https://download.gnome.org/sources/glib/{major}.{minor}/glib-{version}.tar.xz",
            hash="8228a92f92a412160b139ae68b6345bd28f24434a7b5af150ebe21ff587a561d",
            dependencies=["glib-base"],
            patches=[
                "001-glib-package-installation-directory.patch",
                # https://gitlab.gnome.org/GNOME/gobject-introspection/-/issues/499
                "002-gir-scanner-dll-not-found.patch",
            ],
        )
        self.add_param("-Dman-pages=disabled")
        self.add_param("-Dtests=false")
        self.add_param("-Ddocumentation=false")
        if self.opts.enable_gi:
            self.add_dependency("gobject-introspection")
            self.add_param("-Dintrospection=enabled")

    def build(self):
        if self.opts.enable_gi:
            Meson.build(self)


@project_add
class GLibNetworking(Tarball, Meson):
    def __init__(self):
        Project.__init__(
            self,
            "glib-networking",
            version="2.80.0",
            lastversion_even=True,
            repository="https://gitlab.gnome.org/GNOME/glib-networking",
            archive_url="https://download.gnome.org/sources/glib-networking/{major}.{minor}/glib-networking-{version}.tar.xz",
            hash="d8f4f1aab213179ae3351617b59dab5de6bcc9e785021eee178998ebd4bb3acf",
            dependencies=[
                "pkgconf",
                "ninja",
                "meson",
                "glib",
                "openssl",
                "gsettings-desktop-schemas",
            ],
        )

    def build(self):
        Meson.build(
            self, meson_params="-Dgnutls=disabled -Dopenssl=enabled -Dlibproxy=disabled"
        )
        self.install(r".\COPYING share\doc\glib-networking")
        self.install(r".\LICENSE_EXCEPTION share\doc\glib-networking")


@project_add
class GLibPyWrapper(NullExpander, Meson):
    def __init__(self):
        Project.__init__(
            self,
            "glib-py-wrapper",
            dependencies=["glib"],
            version="0.1.0",
            internal=True,
            repository="https://gitlab.gnome.org/GNOME/glib-py-wrapper",
        )

    def build(self):
        Meson.build(self)
