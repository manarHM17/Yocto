from concurrent import futures
import grpc
import mysql.connector
import psutil
import requests
from mysql.connector import Error
import device_pb2
import device_pb2_grpc

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="grpc",
            password="grpc",
            database="iot_device_management"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

class InitialConfiguration(device_pb2_grpc.InitialConfigurationServicer):
    def __init__(self):
        self.db_connection = get_db_connection()
        self.cursor = self.db_connection.cursor()

    def RegisterDevice(self, request, context):
        sql = """
           INSERT INTO devices (serial_number, name, type, location, owner, os_type)
           VALUES (%s, %s, %s, %s, %s, %s)
           """
        values = (
            request.serial_number,
            request.name,
            request.type,
            request.location,
            request.owner,
            request.os_type
        )
        try:
            self.cursor.execute(sql, values)
            self.db_connection.commit()
            print("Device registered successfully in the database")
            device_id = self.cursor.lastrowid
            return device_pb2.RegisterDeviceResponse(message="Device registered successfully", device_id=device_id)
        except mysql.connector.Error as err:
            context.set_details(f"Error registering device: {err}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return device_pb2.RegisterDeviceResponse(message=f"Failed to register device: {err}", device_id=0)

    def UpdateOwnDevice(self, request, context):
        sql = """
           UPDATE devices
           SET name = %s, owner = %s, os_type = %s, location = %s
           WHERE id = %s
           """
        values = (
            request.name,
            request.owner,
            request.os_type,
            request.location,
            request.device_id
        )
        try:
            self.cursor.execute(sql, values)
            self.db_connection.commit()
            print("Device updated successfully")
            return device_pb2.UpdateOwnDeviceResponse(message="Device updated successfully")
        except mysql.connector.Error as err:
            context.set_details(f"Error updating device: {err}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return device_pb2.UpdateOwnDeviceResponse(message=f"Failed to update device: {err}")

    def GetDeviceIdByDeviceName(self, request, context):
        sql = "SELECT id FROM devices WHERE name = %s"
        try:
            self.cursor.execute(sql, (request.device_name,))
            device_id = self.cursor.fetchone()
            if device_id:
                return device_pb2.GetDeviceIdByDeviceNameResponse(device_id=device_id[0])
            else:
                context.set_details("Device not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return device_pb2.GetDeviceIdByDeviceNameResponse(device_id=0)
        except mysql.connector.Error as err:
            context.set_details(f"Error fetching device ID: {err}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return device_pb2.GetDeviceIdByDeviceNameResponse(device_id=0)

    def ConfigureNetwork(self, request, context):
        sql = """
               UPDATE devices
               SET ssid = %s, wifi_password = %s, ip_address = %s
               WHERE id = %s
           """
        values = (request.ssid, request.wifi_password, request.ip_address, request.device_id)
        try:
            self.cursor.execute(sql, values)
            self.db_connection.commit()
            return device_pb2.ConfigureNetworkResponse(message="Network configuration updated successfully")
        except mysql.connector.Error as err:
            context.set_details(f"Error updating network configuration: {err}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return device_pb2.ConfigureNetworkResponse(message=f"Failed to update network configuration: {err}")

class SystemStatusService(device_pb2_grpc.SystemStatusServiceServicer):
    def __init__(self):
        self.db_connection = get_db_connection()
        self.cursor = self.db_connection.cursor()

    def GetSystemStatus(self, request, context):
        sql = """
             INSERT INTO device_monitoring (device_id, cpu_usage, memory_usage, disk_space)
             VALUES (%s, %s, %s, %s)
             """
        values = (request.device_id, request.cpu_usage, request.memory_usage, request.disk_space)
        try:
            self.cursor.execute(sql, values)
            self.db_connection.commit()
            print("System status recorded successfully in the database")
            return device_pb2.SystemStatusResponse(message="System status recorded successfully")
        except mysql.connector.Error as err:
            context.set_details(f"Error recording system status: {err}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return device_pb2.SystemStatusResponse(message=f"Failed to record system status: {err}")

    def GetLastRecord(self, request, context):
        sql = "SELECT cpu_usage, memory_usage, disk_space, timestamp FROM device_monitoring WHERE device_id = %s ORDER BY timestamp DESC LIMIT 1"
        try:
            self.cursor.execute(sql, (request.device_id,))
            record = self.cursor.fetchone()
            if record:
                return device_pb2.GetLastRecordResponse(
                    cpu_usage=record[0],
                    memory_usage=record[1],
                    disk_space=record[2],
                    timestamp=str(record[3]),
                    message="Last record retrieved successfully"
                )
            else:
                context.set_details("No record found for the device")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return device_pb2.GetLastRecordResponse(message="No record found for the device")
        except mysql.connector.Error as err:
            context.set_details(f"Error retrieving last record: {err}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return device_pb2.GetLastRecordResponse(message=f"Failed to retrieve last record: {err}")

class FirmwareUpdateService(device_pb2_grpc.FirmwareUpdateServiceServicer):
    def __init__(self, firmware_path):
        self.firmware_path = firmware_path

    def ApplyFirmwareUpdate(self, request, context):
        try:
            with open(self.firmware_path, 'rb') as file:
                firmware_data = file.read()
            return device_pb2.ApplyFirmwareUpdateResponse(
                firmware_data=firmware_data,
                message="Firmware update applied successfully"
            )
        except Exception as e:
            context.set_details(f"Failed to apply firmware update: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return device_pb2.ApplyFirmwareUpdateResponse(
                firmware_data=b'',
                message=f"Failed to apply firmware update: {e}"
            )

def download_latest_firmware(github_url, download_path):
    response = requests.get(github_url)
    if response.status_code == 200: #200 is the status code for a successful request.
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"Firmware downloaded successfully to {download_path}")
    else:
        print(f"Failed to download firmware from {github_url}")

def serve():
    options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)  # 100MB
    ]
    firmware_url = 'https://github.com/raspberrypi/firmware/raw/master/boot/kernel.img'
    firmware_path = 'latest_firmware.bin'

    # Download the latest firmware before starting the server
    download_latest_firmware(firmware_url, firmware_path)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    device_pb2_grpc.add_InitialConfigurationServicer_to_server(InitialConfiguration(), server)
    device_pb2_grpc.add_SystemStatusServiceServicer_to_server(SystemStatusService(), server)
    device_pb2_grpc.add_FirmwareUpdateServiceServicer_to_server(FirmwareUpdateService(firmware_path), server)
    server.add_insecure_port('[::]:50051')
    print("Server listening on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
