"""
cpymake's build_ext command for building a python C/C++ extension using CMake
"""

import os
import pathlib
import subprocess
import sysconfig

from typing import List

from setuptools import errors
from setuptools.command.build import SubCommand
from setuptools.command.build_ext import build_ext
from cpymake.cpymake_extension import CPyMakeExtension


# NOTE:
#   Whilst we do not use a lot of the variables set in setuptools' build_ext
# and distutils' build_ext (although a few more of those are used) it could be safer to
# just call their version in initalize and finalize options but at the same time ...
# then again what hppens if they move more stuff from distutils to setuptools and change
# the way some options are used (such as build-temp).
#   Ideally we would just inherit distutils' version but that is deprecated so....
#   Ah Forget it we're gonna rewrte all the *_options functions!


# Sub Command is a Protocol but we want to explicitly inherit
class CPyMakeBuildExt(build_ext, SubCommand):  # pylint: disable=too-many-ancestors
    """CPyMake's build_ext class that can be used as a plugin for setuptools
    to build extension modules that use CMake as their build (generator) system
    """

    description = "build C/C++ extensions using CMake (compile/link to build directory)"

    user_options = [
        ("build-lib=", "b", "directory for compiled extension modules"),
        ("build-temp=", "t", "directory for temporary files (build by-products)"),
        # VV not supported yet but we will leave it for now (-A in CMAKE)
        (
            "plat-name=",
            "p",
            (
                "platform name to cross-compile for, if supported "
                f"(default: {sysconfig.get_platform()})"
            ),
        ),
        (
            "inplace",
            "i",
            "ignore build-lib and put compiled extensions into the source "
            + "directory alongside your pure Python modules",
        ),
        ("define=", "D", "C preprocessor macros to define"),
        ("undef=", "U", "C preprocessor macros to undefine"),
        ("debug", "g", "compile/link with debugging information"),
        ("force", "f", "forcibly build everything (ignore file timestamps)"),
        ("parallel=", "j", "number of parallel build jobs"),
    ]

    boolean_options = ["inplace", "debug", "force"]

    # TODO: VV Show generators and possibly platforms?
    # help_options = [
    #     ("help-compiler", None, "list available compilers", show_compilers),
    # ]

    # override
    def initialize_options(self):
        # pylint: disable=attribute-defined-outside-init

        print("***** Initialize_options Called!")

        self.package = None
        self.extensions = None

        self.build_lib = None
        self.build_temp = None
        self.plat_name = None
        self.inplace = 0
        self.editable_mode = False
        # self.ext_map = {} #<- I don't think we need this!
        # self.ext_map = {}
        # ^^ Irritatingly if we just add this we can use setuptools functions
        # that expect this variable

        self.define = None
        self.undef = None
        self.debug = None
        self.force = None
        self.parallel = None

    # override
    def finalize_options(self):
        # pylint: disable=attribute-defined-outside-init

        print("***** Finalize_options Called")

        self.set_undefined_options(
            "build",
            ("build_lib", "build_lib"),
            ("build_temp", "build_temp"),
            ("debug", "debug"),
            ("force", "force"),
            ("parallel", "parallel"),
            ("plat_name", "plat_name"),
        )

        if self.package is None:
            self.package = self.distribution.ext_package

        self.extensions = self.distribution.ext_modules or []

        if os.name == "nt":
            if self.debug:
                self.build_temp = os.path.join(self.build_temp, "Debug")
            else:
                self.build_temp = os.path.join(self.build_temp, "Release")

        # TODO:
        # defines and undefs

        # NOTE: May want to do it more like how numpy does
        # (i.e convert to int regardless)
        if isinstance(self.parallel, str):
            try:
                self.parallel = int(self.parallel)
            except ValueError as e:
                raise errors.OptionError("--parallel/-j should be an integer") from e

        # TODO: custom check extension list

        # TODO: Do we need??
        # for ext in self.extensions:
        #     ext._full_name = self.get_ext_fullname(ext.name)
        #     # this is split into two loops in setuptools but why?
        #     self.ext_map[

        if self.editable_mode:
            self.inplace = True

    # Don't call super as we need all custom behaviour
    # override
    def run(self):
        print("***** Run Called")

        print(
            "***** cpymake's build_ext's variables =",
            f"package = {self.package}",
            "extensions = printed_later",
            f"build_lib = {self.build_lib}",
            f"build_temp = {self.build_temp}",
            f"plat_name = {self.plat_name}",
            f"inplace = {self.inplace}",
            f"editable_mode = {self.editable_mode}",
            f"define = {self.define}",
            f"undef = {self.undef}",
            f"debug = {self.debug}",
            f"force = {self.force}",
            f"parallel = {self.parallel}",
            sep="\n\t",
        )

        # 'self.extensions', as supplied by setup.py, is a list of
        # Extension instances.
        if not self.extensions:
            return

        # Ensure that CMake is present and working. Was going to extract
        # but I think that that is unneccisary
        try:
            subprocess.run(["cmake", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError as cpe:
            raise RuntimeError("Cannot find CMake executable") from cpe

        self.build_extensions()
        # VV Happens automatically as inplace automatically modifys build dir
        # to be inplace :D -> wasted time sad tho.
        # if self.inplace:
        #  self.copy_extensions_to_source()
        # ^^ self.inplace is set in super().finalize_options() to be true
        # when self.editable_mode is True

    # override
    def build_extensions(self):
        print("****** Build_extensions Called")

        # origional_package = self.package

        # Really useful to see what additional options we can use
        # print('***', *(self.user_options), sep="\n")
        # Same as python setup.py build_ext --help

        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)

        print("***** print each ext:")

        for extension in self.extensions:
            print("******", extension)
            # Looks dodgy but it's been years since I made this so...
            # Actually maybe not...
            # self.package = (  # pylint: disable=attribute-defined-outside-init
            #     extension.package_name
            # )
            # extension_dir = self.get_extension_build_directory(extension.name)
            extension_dir = os.getcwd() + os.sep + self.build_lib
            extension_suffix = (
                # self.extension_suffix  # sysconfig.get_config_var("EXT_SUFFIX")
                sysconfig.get_config_var("EXT_SUFFIX")
            )

            # Should I also allow this to be overridable in extension?
            config = "Debug" if self.debug else "Release"
            cmake_args = [
                f"-DCMAKE_BUILD_TYPE={config}",
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{config}={extension_dir}",
                # Needed for windows (more specifically .dll platforms).
                # It is safe to leave for all systems although will erroneously
                # add any .exe's created, which shouldn't exist anyway
                #
                # May remove for .so systems but without further testing it is
                # an unnecessary risk to remove
                f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{config}={extension_dir}",
                f"-DPYTHON_EXTENSION_SUFFIX={extension_suffix}",
            ]
            if extension.generator:
                cmake_args.append(f"-G {extension.generator}")

            # Config -> outputs in our temp dir
            subprocess.run(
                ["cmake", extension.cmake_lists_root_dir, *cmake_args],
                # cwd=self.build_temp,
                check=True,
                capture_output=True,
            )

            print("~~~~~~~ CWD=", os.getcwd())

            # Build -> builds the config (AKA generated solution/makefiles) in
            # our temp dir but outputs have already been setup in cmake_args
            # TODO: Update
            build_cmd = ["cmake", "--build", ".", "--config", config]
            if extension.targets is not None:
                build_cmd.append("--target")
                # TODO: Check if it requires args as a separate strings or
                # if Joint is okay
                build_cmd.append(" ".join(extension.targets))

            if self.parallel:
                build_cmd.append(f"-j {self.parallel}")
            else:
                build_cmd.append("-j")

            print("##### pre-run")
            subprocess.run(build_cmd, #cwd=self.build_temp,
                           check=True)
            print("##### post-run")

    # TODO: These three functions need a rewrite! I think we can use special cmake
    # runs, unfortunatly I'm not 100% sure plus it may well
    # be considered "a side affect" although not really? but i guess configure is
    # required

    # NOTE: Possibly too different from original but.... I mean this whole thing
    # could be a separate command caled build_cmake_ext for example

    # override
    def get_output_mapping(self) -> dict[str, str]:
        print("***** Get_output_mapping Called")

        # They sort an interator and convert to dict but lets just make it here

        # might be neater to just use if rather than if not
        if not self.inplace:
            return {}

        build_py = self.get_finalized_command("build_py")
        output_mapping = {}

        for ext in self.extensions:
            inplace_file, regular_file = self._get_inplace_equivalent(build_py, ext)
            output_mapping[regular_file] = inplace_file

        return output_mapping

    # override
    def get_outputs(self) -> List[str]:
        print("****** Get_outputs Called")

        # NOTE: Ideally we would also get clibs that the CMake extension requires/builds
        # unfortunatly I dont yet see how so for now.....
        # Can cmake tell us ??? I think so, so... what happens then can we use
        # vars set in run? will run have been "run" first?

        if self.inplace:
            return list(self.get_output_mapping().keys())

        self.check_extensions_list(self.extensions)
        outputs = []
        for ext in self.extensions:
            outputs.append(self.get_ext_fullpath(ext.name))
        print("***** Outputs =", outputs)

        return outputs

    # override
    def get_source_files(self):
        print("***** Get_source_files Called")

        self.check_extensions_list(self.extensions)
        # TODO: For now this is all we can do
        filenames = []
        for ext in self.extensions:
            filenames.append(ext.cmake_lists_root_dir)
        return filenames  # contains path for now so change probably

    # override
    def check_extensions_list(self, extensions):
        """Ensures that the list of extensions provided by setuptools.setup's
        ext_modules parameter is valid. i.e. it is a list of
        CeMakeExtension objects. Old style list of 2-tuples is no longer supported.

        Raise Setuptools' SetupError if invalid extension found
        """

        print("***** Check_extensions_list Called")

        if not isinstance(extensions, list):
            raise errors.SetupError(
                "'ext_modules' argument must be a list of CeMakeExtension instances "
                f"however ext_modules had type {type(extensions)}"
            )

        if not all(isinstance(ext, CPyMakeExtension) for ext in extensions):
            raise errors.SetupError(
                "Each element of 'ext_modules' must be an instance of "
                "the CeMakeExtension class"
            )
