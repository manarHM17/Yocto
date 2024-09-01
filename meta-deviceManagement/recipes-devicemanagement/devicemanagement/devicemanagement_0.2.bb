DESCRIPTION = "Recipe for IoT Device Management Platform"
LICENSE = "CLOSED"

SRC_URI = "file://client1.py \
           file://client.py \
           file://device.proto \
           file://new_firmware_version.bin \
           file://server.py"

S = "${WORKDIR}"

RDEPENDS_${PN} = "\
                python3-core \
                python3-grpcio \
                python3-protobuf \
                python3-psutil \
"

DEPENDS += " \
    python3-grpcio-tools-native \
"

do_compile() {
    # Generate gRPC Python files
    python3 -m grpc_tools.protoc -I${WORKDIR} --python_out=${WORKDIR} --grpc_python_out=${WORKDIR} ${WORKDIR}/device.proto
}

do_install() {
    # Install the Python scripts
    install -d ${D}/usr/bin/devicemanagement
    install -m 0755 ${S}/client.py ${D}/usr/bin/devicemanagement/
    install -m 0755 ${S}/client1.py ${D}/usr/bin/devicemanagement/
    install -m 0755 ${S}/device_pb2.py ${D}/usr/bin/devicemanagement/
    install -m 0755 ${S}/device_pb2_grpc.py ${D}/usr/bin/devicemanagement/
    install -m 0755 ${S}/server.py ${D}/usr/bin/devicemanagement/

    # Install the protobuf file
    install -d ${D}/usr/share/devicemanagement
    install -m 0644 ${S}/device.proto ${D}/usr/share/devicemanagement/

    # Install the firmware binary
    install -d ${D}/usr/lib/devicemanagement
    install -m 0644 ${S}/new_firmware_version.bin ${D}/usr/lib/devicemanagement/
}

# Specify which files should be included in the package
FILES:${PN} = "/usr/bin/devicemanagement/* \
               /usr/share/devicemanagement/* \
               /usr/lib/devicemanagement/*"
