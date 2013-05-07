#-*- coding: ISO-8859-1 -*-
# setup.py: the distutils script
#
# Copyright (C) 2013 Kali Kaneko <kali@futeisha.org> (sqlcipher support)
# Copyright (C) 2005-2010 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlcipher.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import glob
import os
import re
import subprocess
import sys

from distutils.core import setup, Extension, Command
from distutils.command.build_ext import build_ext

import cross_bdist_wininst

# If you need to change anything, it should be enough to change setup.cfg.

PYSQLITE_EXPERIMENTAL = False

class DocBuilder(Command):
    description = "Builds the documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import shutil
        try:
            shutil.rmtree("build/doc")
        except OSError:
            pass
        os.makedirs("build/doc")
        rc = os.system("sphinx-build doc/sphinx build/doc")
        if rc != 0:
            print ("Is sphinx installed? If not, try 'sudo easy_install sphinx'.")

class SQLCipherBuildExtension(build_ext):
    def build_extension(self, ext):
        subprocess.call(["make", "distclean"], cwd=os.path.join(os.path.dirname(__file__), "sqlcipher"))
        subprocess.check_call("./configure --enable-tempstore=yes CFLAGS=\"-DSQLITE_HAS_CODEC\" LDFLAGS=\"-lcrypto\"", shell=True, cwd=os.path.join(os.path.dirname(__file__), "sqlcipher"))
        subprocess.check_call(["make"], cwd=os.path.join(os.path.dirname(__file__), "sqlcipher"))
        build_ext.build_extension(self, ext)

def get_pysqlite_version():
    version = None
    version_minor = None

    version_re = re.compile('#define PYSQLITE_VERSION "(.*)"')
    f = open(os.path.join("src", "module.h"))
    for line in f:
        match = version_re.match(line)
        if match:
            version = match.groups()[0]
            version_minor = ".".join(version.split('.')[:2])
            break
    f.close()

    if not version:
        print "Fatal error: PYSQLITE_VERSION could not be detected!"
        sys.exit(1)

    return version

setup(name="pysqlcipher",
      version="2.1.1-" + get_pysqlite_version(),
      description="DB-API 2.0 interface for SQLCipher",
      long_description="""Python interface to SQLCipher

pysqlcipher is an interface to the SQLite 3.x embedded relational
database engine. It is almost fully compliant with the Python database API
version 2.0. At the same time, it also exposes the unique features of
SQLCipher.""",
      author="Kali Kaneko",
      author_email="kali@futeisha.org",
      license="License :: OSI Approved :: MIT License",
      platforms="ALL",
      url="http://github.com/leapcode/pysqlcipher",
      package_dir={"pysqlcipher": "lib"},
      packages=["pysqlcipher", "pysqlcipher.test"] + ([] if sys.version_info < (2, 5) else ["pysqlcipher.test.py25"]),
      scripts=[],
      data_files=[("pysqlcipher-doc", glob.glob("doc/*.html") + glob.glob("doc/*.txt") + glob.glob("doc/*.css")),
                  ("pysqlcipher-doc/code", glob.glob("doc/code/*.py"))],
      ext_modules=[
          Extension(
              name="pysqlcipher._sqlite",
              sources= ["src/module.c", "src/connection.c", "src/cursor.c", "src/cache.c",
                        "src/microprotocols.c", "src/prepare_protocol.c", "src/statement.c",
                        "src/util.c", "src/row.c", "sqlcipher/sqlite3.c"] + (["src/backup.c"] if PYSQLITE_EXPERIMENTAL else []),
              include_dirs=['sqlcipher'],
              library_dirs=[],
              runtime_library_dirs=[],
              libraries=['crypto'],
              extra_objects=[],
              define_macros=[("SQLITE_ENABLE_FTS3", "1"), ("SQLITE_ENABLE_RTREE", "1"), ("SQLITE_ENABLE_LOAD_EXTENSION", "1"), ("SQLITE_HAS_CODEC", "1"), ("SQLITE_TEMP_STORE", "2")] + 
                            ([('MODULE_NAME', '\\"pysqlcipher.dbapi2\\"')] if sys.platform == "win32" else [('MODULE_NAME', '"pysqlcipher.dbapi2"')])
          )
      ],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX",
          "Programming Language :: C",
          "Programming Language :: Python",
          "Topic :: Database :: Database Engines/Servers",
          "Topic :: Software Development :: Libraries :: Python Modules"],
      cmdclass={"build_docs": DocBuilder,
                "build_ext": SQLCipherBuildExtension,
                "cross_bdist_wininst": cross_bdist_wininst.bdist_wininst}
)

