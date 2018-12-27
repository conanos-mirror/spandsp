from conans import ConanFile, tools, MSBuild
from conanos.build import config_scheme
import os, shutil

class SpandspConan(ConanFile):
    name = "spandsp"
    version = "0.0.6"
    description = "SpanDSP is a library of DSP functions for telephony, in the 8000 sample per second world of E1s, T1s, and higher order PCM channels"
    url = "https://github.com/conanos/spandsp"
    homepage = "https://www.soft-switch.org/"
    license = "LGPL-v2.1+"
    exports = ["COPYING","src/*","math_fixed_tables.h","config.h"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)
    
    def requirements(self):
        self.requires.add("libtiff/4.0.10@conanos/stable")

    def source(self):
        url_ = 'http://172.16.64.65:8081/artifactory/gstreamer/spandsp-{version}.tar.gz'
        #url_ = http://www.soft-switch.org/downloads/spandsp/spandsp-{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + '-' + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            shutil.copy(os.path.join(self.source_folder, "math_fixed_tables.h"),os.path.join(self.source_folder,self._source_subfolder,"src"))
            shutil.copy(os.path.join(self.source_folder, "config.h"),os.path.join(self.source_folder,self._source_subfolder,"src","msvc"))
            self._copy_msvc_proj()
    
    def _copy_msvc_proj(self):
        for proj in ["libspandsp.2008.sln", "libspandsp.2008.vcproj"]:
            shutil.copy(os.path.join(self.source_folder,"src",proj),os.path.join(self.source_folder,self._source_subfolder,"src",proj))
        for proj in ["make_at_dictionary.2008.vcproj","make_modem_filter.2008.vcproj"]:
            shutil.copy(os.path.join(self.source_folder,"src","msvc",proj),os.path.join(self.source_folder,self._source_subfolder,"src","msvc",proj))

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    with tools.environment_append({
        #        'PKG_CONFIG_PATH' : "%s/lib/pkgconfig"%(self.deps_cpp_info["libtiff"].rootpath),
        #        'LIBRARY_PATH':"%s/lib"%(self.deps_cpp_info["libtiff"].rootpath),
        #        'C_INCLUDE_PATH':"%s/include"%(self.deps_cpp_info["libtiff"].rootpath)
        #        }):
    
        #        _args = ["--prefix=%s/builddir"%(os.getcwd()),"--disable-silent-rules"]
        #        if self.options.shared:
        #            _args.extend(['--enable-shared=yes','--enable-static=no'])
        #        else:
        #            _args.extend(['--enable-shared=no','--enable-static=yes'])

        #        self.run("sh ./autogen.sh && sh ./configure %s"%(' '.join(_args)))
        #        self.run("make")
        #        self.run("make install")
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"src")):
                msbuild = MSBuild(self)
                msbuild.build("libspandsp.2008.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})

    def package(self):
        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))
        if self.settings.os == 'Windows':
            platforms = {'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join(self.build_folder,self._source_subfolder,"src",platforms.get(str(self.settings.arch)),str(self.settings.build_type))
            self.copy("spandsp.*", dst=os.path.join(self.package_folder,"lib"),src=output_rpath)
            self.copy("libspandsp.dll", dst=os.path.join(self.package_folder,"bin"),src=output_rpath)

            self.copy("spandsp.h", dst=os.path.join(self.package_folder,"include"),src=os.path.join(self.build_folder,self._source_subfolder,"src"))
            tools.replace_in_file(os.path.join(self.package_folder,"include","spandsp.h"),"@INSERT_STDBOOL_HEADER@","#include <stdbool.h>")
            tools.mkdir(os.path.join(self.package_folder,"lib","pkgconfig"))
            shutil.copy(os.path.join(self.build_folder,self._source_subfolder,"spandsp.pc.in"),os.path.join(self.package_folder,"lib","pkgconfig","spandsp.pc"))
            replacements = {
                "@prefix@" : self.package_folder,
                "@exec_prefix@" : "${prefix}/bin",
                "@libdir@" : "${prefix}/lib",
                "@includedir@" : "${prefix}/include",
                "@VERSION@" : self.version,
            }
            for s, r in replacements.items():
                tools.replace_in_file(os.path.join(self.package_folder,"lib","pkgconfig","spandsp.pc"),s,r)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

