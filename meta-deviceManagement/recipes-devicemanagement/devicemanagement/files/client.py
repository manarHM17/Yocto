import grpc
import psutil
import device_pb2_grpc
import device_pb2
import socket


def register_device(stub):
    serial_number = input("Enter serial number: ")
    name = input("Enter device name: ")
    device_type = input("Enter device type: ")
    location = input("Enter device location: ")
    owner = input("Enter device owner: ")
    os_type = input("Enter OS type: ")

    device = device_pb2.RegisterDeviceRequest(
        serial_number=serial_number,
        name=name,
        type=device_type,
        location=location,
        owner=owner,
        os_type=os_type
    )

    response = stub.RegisterDevice(device)
    print(f"Response message: {response.message}")
    print(f"Registered device ID: {response.device_id}")

def delete_device(stub):
    device_id = int(input("Enter device ID to delete: "))

    request = device_pb2.DeleteDeviceRequest(device_id=device_id)
    response = stub.DeleteDevice(request)

    if response.success:
        print("Device deleted successfully.")
    else:
        print(f"Failed to delete device: {response.message}")

def update_own_device(stub):
    device_id = int(input("Enter your device ID: "))
    name = input("Enter new device name: ")
    owner = input("Enter new device owner: ")
    os_type = input("Enter new OS type: ")
    location = input("Enter new device location: ")

    request = device_pb2.UpdateOwnDeviceRequest(
        device_id=device_id,
        name=name,
        owner=owner,
        os_type=os_type,
        location=location
    )

    response = stub.UpdateOwnDevice(request)
    print(f"Response message: {response.message}")


def get_device_id_by_name(stub):
    device_name = input("Enter device name to get ID: ")

    request = device_pb2.GetDeviceIdByDeviceNameRequest(device_name=device_name)
    response = stub.GetDeviceIdByDeviceName(request)
    print(f"Device ID: {response.device_id}")


def configure_network(stub):
    device_id = int(input("Enter device ID: "))
    ssid = input("Enter SSID: ")
    wifi_password = input("Enter WiFi password: ")
    ip_address = input("Enter IP address: ")

    request = device_pb2.ConfigureNetworkRequest(
        device_id=device_id,
        ssid=ssid,
        wifi_password=wifi_password,
        ip_address=ip_address
    )
    response = stub.ConfigureNetwork(request)
    print(f"Response message: {response.message}")


def get_system_status(stub):
    device_id = int(input("Enter your Device ID: "))
    cpu_usage = f"{psutil.cpu_percent()}%"
    memory_usage = f"{psutil.virtual_memory().percent}%"
    disk_space = f"{psutil.disk_usage('/').percent}%"

    request = device_pb2.SystemStatusRequest(
        device_id=device_id,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        disk_space=disk_space
    )

    response = stub.GetSystemStatus(request)
    print(f"Response message: {response.message}")


def get_last_system_status(stub):
    device_id = int(input("Enter device ID: "))

    request = device_pb2.GetLastRecordRequest(device_id=device_id)
    response = stub.GetLastRecord(request)

    if response.message == "Last record retrieved successfully":
        print("Last system status:")
        print(f"CPU Usage: {response.cpu_usage}")
        print(f"Memory Usage: {response.memory_usage}")
        print(f"Disk Space: {response.disk_space}")
        print(f"Timestamp: {response.timestamp}")
    else:
        print(f"Error: {response.message}")

def get_current_firmware_version(stub):
    device_id = int(input("Enter device ID to get current firmware version: "))

    request = device_pb2.FirmwareRequest(device_id=device_id)
    response = stub.GetCurrentFirmwareVersion(request)

    if response.current_version:
        print(f"Current firmware version: {response.current_version}")
    else:
        print(f"Error: {response.message}")


def update_firmware(stub):
    device_id = int(input("Enter device ID to update firmware: "))

    request = device_pb2.UpdateFirmwareRequest(device_id=device_id)

    # Stream the responses from the server
    response_stream = stub.UpdateFirmware(request)

    # Open a file to write the firmware binary data
    request = device_pb2.UpdateFirmwareRequest(device_id=device_id)
    response = stub.UpdateFirmware(request)

    if response.success:
        with open('new_firmware_version.bin', 'wb') as f:
            f.write(response.firmware_binary_data)
        print(f"Received firmware version: {response.firmware_version}")
    else:
        print(f"Firmware update failed: {response.message}")

    print("Firmware Binary File succesfully transsmited please complete the firmware update.")


def set_firmware_version(stub):
    device_id = int(input("Enter device ID to set new firmware version: "))
    firmware_version = input("Enter new firmware version: ")  # Use firmware_version as defined in .proto

    request = device_pb2.SetFirmwareVersionRequest(
        device_id=device_id,
        firmware_version=firmware_version
    )

    try:
        response = stub.SetFirmwareVersion(request)
        if response.success:
            print("Firmware version updated successfully.")
        else:
            print(f"Failed to update firmware version: {response.message}")
    except grpc.RpcError as e:
        print(f"RPC error: {e.code()} - {e.details()}")

def run():
    channel = grpc.insecure_channel('192.168.1.23:50051')  # Address of the server:port
    stub1 = device_pb2_grpc.InitialConfigurationStub(channel)
    stub2 = device_pb2_grpc.SystemStatusServiceStub(channel)
    stub3 = device_pb2_grpc.FirmwareConfigurationStub(channel)

    while True:
        print("Choose an option:")
        print("1. Register Device")
        print("2. Set Network Details")
        print("3. Set Firmware Version")
        print("4. Register System Status in the data base")
        print("5. Get Device ID by Device Name")
        print("6. Get Last System Status")
        print("7. Get Current Firmware Version")
        print("8. Update Firmware")
        print("9. Update Your Device informations")
        print("10. Delete Device")
        print("11. Exit")

        choice = input("Enter your choice:")

        if choice == '1':
            register_device(stub1)
        elif choice == '2':
            configure_network(stub1)
        elif choice == '3':
            set_firmware_version(stub3)
        elif choice == '4':
            get_system_status(stub2)
        elif choice == '5':
            get_device_id_by_name(stub1)
        elif choice == '6':
            get_last_system_status(stub2)
        elif choice == '7':
            get_current_firmware_version(stub3)
        elif choice == '8':
            update_firmware(stub3)
        elif choice == '9':
            update_own_device(stub1)
        elif choice == '10':
            delete_device(stub1)
        elif choice == '11':
            break
        else:
            print("Invalid choice. Please choose a valid option.")

if __name__ == '__main__':
    run()
