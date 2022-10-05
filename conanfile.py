import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import get, rm
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"

class LibrethinkdbxxConan(ConanFile):
    name = "librethinkdbxx"
    version = "cci.20171109"

    license = "Apache License Version 2.0"
    url = "https://github.com/AtnNn/librethinkdbxx/"
    description = "This driver is compatible with RethinkDB 2.0. It is based on the official RethinkDB Python driver."
    topics = ("RethinkDB", "C++")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "Makefile", "src/*", "reql/"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    #def layout(self):
    #    basic_layout(self)

    def build_id(self):
        self.info_build.options.shared = "Any"

    def generate(self):
        at_toolchain = AutotoolsToolchain(self)
        at_toolchain.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.make("DEBUG=yes" if self.settings.build_type == "Debug" else "")

    def package(self):
        lib_shared_exts = { "*.a", "*.lib" }, { "*.so", "*.dll", "*.dylib" }
        autotools = Autotools(self)
        autotools.install(args=['prefix={}'.format(self.package_folder), 'DESTDIR='])

        for ext in lib_shared_exts[not self.options.shared]:
            rm(self, pattern=ext, folder=self.package_folder, recursive=True)

        self.copy("COPYRIGHT", dst="licenses")
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["rethinkdb++"]
