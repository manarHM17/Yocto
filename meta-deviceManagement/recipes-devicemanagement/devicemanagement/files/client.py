import grpc
import psutil
import device_pb2_grpc
import device_pb2
import socket


def is_ip_in_use(ip_address):
    try:
        # Try to create a socket connection to the IP
        sock = socket.create_connection((ip_address, 80), timeout=2)
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False


def generate_random_ip(base_ip, start=1, end=254):
    import random
    while True:
        last_octet = random.randint(start, end)
        ip_address = f"{base_ip}.{last_octet}"
        if not is_ip_in_use(ip_address):
            return ip_address


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

    # Create request with all necessary fields
    request = device_pb2.SystemStatusRequest(
        device_id=device_id,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        disk_space=disk_space
    )

    # Send request to the server
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


def apply_firmware_update(stub):
    device_id = int(input("Enter device ID: "))

    request = device_pb2.ApplyFirmwareUpdateRequest(device_id=device_id)
    response = stub.ApplyFirmwareUpdate(request)

    print(f"Response message: {response.message}")


def run():
    options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)  # 100MB
    ]
    # channel and stubs
    channel = grpc.insecure_channel('localhost:50051')  # Address of the server:port
    stub1 = device_pb2_grpc.InitialConfigurationStub(channel)
    stub2 = device_pb2_grpc.SystemStatusServiceStub(channel)
    stub3 = device_pb2_grpc.FirmwareUpdateServiceStub(channel)

    while True:
        print("Choose an option:")
        print("1. Register Device")
        print("2. Update Your Device")
        print("3. Get Device ID by Device Name")
        print("4. Set Network Details")
        print("5. Get System Status")
        print("6. Get Last System Status")
        print("7. Apply Firmware Update")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            register_device(stub1)
        elif choice == '2':
            update_own_device(stub1)
        elif choice == '3':
            get_device_id_by_name(stub1)
        elif choice == '4':
            configure_network(stub1)
        elif choice == '5':
            get_system_status(stub2)
        elif choice == '6':
            get_last_system_status(stub2)
        elif choice == '7':
            apply_firmware_update(stub3)
        elif choice == '9':
            break
        else:
            print("Invalid choice. Please choose a valid option.")


if __name__ == '__main__':
    run()
