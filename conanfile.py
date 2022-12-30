import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import chdir, copy, get, rm
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"

class LibrethinkdbxxConan(ConanFile):
    name = "librethinkdbxx"
    version = "cci.20171109"

    license = "Apache License Version 2.0"
    url = "https://github.com/AtnNn/librethinkdbxx/"
    description = "This driver is compatible with RethinkDB 2.0. It is based on the official RethinkDB Python driver."
    topics = ("rethinkdb", "c++")
    package_type = "library"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        with chdir(self, self.source_folder):
            autotools.make("DEBUG=yes" if self.settings.build_type == "Debug" else "")

    def package(self):
        lib_shared_exts = { "*.a", "*.lib" }, { "*.so", "*.dll", "*.dylib" }
        autotools = Autotools(self)
        with chdir(self, self.source_folder):
            autotools.install(args=['prefix='])

        for ext in lib_shared_exts[not self.options.shared]:
            rm(self, pattern=ext, folder=self.package_folder, recursive=True)

        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["rethinkdb++"]
