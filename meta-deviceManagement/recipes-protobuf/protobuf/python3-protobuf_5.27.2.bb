DESCRIPTION = "Protocol Buffers"
HOMEPAGE = "https://developers.google.com/protocol-buffers/"
SECTION = "devel/python"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://PKG-INFO;beginline=8;endline=8;md5=be628fb2c2ba7982037799701e5913bf"

inherit pypi setuptools3

SRC_URI = "https://files.pythonhosted.org/packages/71/a5/d61e4263e62e6db1990c120d682870e5c50a30fb6b26119a214c7a014847/protobuf-5.27.2.tar.gz"
SRC_URI[sha256sum] = "f3ecdef226b9af856075f28227ff2c90ce3a594d092c39bee5513573f25e2714"

UPSTREAM_CHECK_REGEX = "protobuf/(?P<pver>\d+(\.\d+)+)/"

DEPENDS += "protobuf"

RDEPENDS:${PN} += " \
    ${PYTHON_PN}-datetime \
    ${PYTHON_PN}-json \
    ${PYTHON_PN}-logging \
    ${PYTHON_PN}-netclient \
    ${PYTHON_PN}-numbers \
    ${PYTHON_PN}-pkgutil \
    ${PYTHON_PN}-six \
    ${PYTHON_PN}-unittest \
"

# For usage in other recipes when compiling protobuf files (e.g. by grpcio-tools)
BBCLASSEXTEND = "native nativesdk"

DISTUTILS_BUILD_ARGS += "--cpp_implementation"
DISTUTILS_INSTALL_ARGS += "--cpp_implementation"

do_compile:prepend:class-native () {
    export KOKORO_BUILD_NUMBER="1"
}

