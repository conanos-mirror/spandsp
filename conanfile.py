from conans import ConanFile, CMake, tools
from shutil import copyfile
import os

class SpandspConan(ConanFile):
    name = "spandsp"
    version = "0.0.6"
    description = "SpanDSP is a library of DSP functions for telephony, in the 8000 sample per second world of E1s, T1s, and higher order PCM channels"
    url = "https://github.com/conan-multimedia/spandsp"
    homepage = "https://www.soft-switch.org/"
    license = "LGPLv2_1Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "libtiff/4.0.9@conanos/dev"

    source_subfolder = "source_subfolder"

    def source(self):
        #http://www.soft-switch.org/downloads/spandsp/spandsp-0.0.6.tar.gz'
        tools.get('http://172.16.64.65:8081/artifactory/gstreamer/{name}-{version}.tar.gz'.format(name=self.name,version=self.version))
        extracted_dir = self.name + '-' + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PKG_CONFIG_PATH' : "%s/lib/pkgconfig"%(self.deps_cpp_info["libtiff"].rootpath),
                'LIBRARY_PATH':"%s/lib"%(self.deps_cpp_info["libtiff"].rootpath),
                'C_INCLUDE_PATH':"%s/include"%(self.deps_cpp_info["libtiff"].rootpath)
                }):
    
                _args = ["--prefix=%s/builddir"%(os.getcwd()),"--disable-silent-rules"]
                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])

                self.run("sh ./autogen.sh && sh ./configure %s"%(' '.join(_args)))
                self.run("make")
                self.run("make install")

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

