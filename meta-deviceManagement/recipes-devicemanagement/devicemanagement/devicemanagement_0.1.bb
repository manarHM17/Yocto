DESCRIPTION = "Recipe for IoT Device Management Platform"
LICENSE = "CLOSED"

SRC_URI = "file://client.py \
           file://device.proto \
           file://latest_firmware.bin \
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
    python3 -m grpc.tools.protoc -I${WORKDIR} --python_out=${WORKDIR} --grpc_python_out=${WORKDIR} ${WORKDIR}/device.proto
}

do_install() {
    # Install the Python scripts
    install -d ${D}/usr/bin/deviceManagement
    install -m 0755 ${S}/client.py ${D}/usr/bin/deviceManagement/
    install -m 0755 ${S}/device_pb2.py ${D}/usr/bin/deviceManagement/
    install -m 0755 ${S}/device_pb2_grpc.py ${D}/usr/bin/deviceManagement/
    install -m 0755 ${S}/server.py ${D}/usr/bin/deviceManagement/

    # Install the protobuf file
    install -d ${D}/usr/share/deviceManagement
    install -m 0644 ${S}/device.proto ${D}/usr/share/deviceManagement/

    # Install the firmware binary
    install -d ${D}/usr/lib/deviceManagement
    install -m 0644 ${S}/latest_firmware.bin ${D}/usr/lib/deviceManagement/
}

# Specify which files should be included in the package
FILES:${PN} = "/usr/bin/deviceManagement/* \
               /usr/share/deviceManagement/* \
               /usr/lib/deviceManagement/*"
