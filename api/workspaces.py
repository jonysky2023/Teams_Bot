import os
import requests

WORKSPACES = {
    "default": {
        "api_baseurl": os.getenv("API_BASEURL"),
        "api_user": os.getenv("API_USER"),
        "api_pass": os.getenv("API_PASS"),
        "enabled_tools": [
            "get_device_status",
            "get_service_info",
            "restart_service"
        ]
    },
    "client_a": {
        "api_baseurl": "https://client-a.api.com",
        "api_user": "user_a",
        "api_pass": "pass_a",
        "enabled_tools": [
            "get_device_status",
            "get_user_info"
        ]
    }
}


def get_workspace(name: str) -> dict:
    return WORKSPACES.get(name, WORKSPACES["default"])


def find_workspace(device_name: str) -> dict | None:
    if not device_name:
        return None

    config = get_workspace("default")
    base_url = config.get("api_baseurl")
    user = config.get("api_user")
    password = config.get("api_pass")

    if not base_url:
        print("ERROR: API_BASEURL no configurada")
        return None

    try:
        response = requests.get(
            f"{base_url}/workspaces",
            params={"apiversion": "1"},
            auth=(user, password),
            timeout=10
        )

        if not response.ok:
            print(f"Flexxible API error: {response.status_code} {response.text}")
            return None

        data = response.json()
        items = data if isinstance(data, list) else data.get("Items", data.get("value", []))

        device_name_lower = device_name.lower()

        for item in items:
            if item.get("FullName", "").lower() == device_name_lower:
                return item

        for item in items:
            if device_name_lower in item.get("FullName", "").lower():
                return item

        return None

    except Exception as e:
        print(f"Error conectando con Flexxible: {e}")
        return None


def fetch_device_status(device_name: str, workspace_name: str = "default") -> dict | None:
    device = find_workspace(device_name)
    if not device:
        return None

    return {
        # Identidad
        "full_name":            device.get("FullName", "N/A"),
        "user":                 device.get("UserName", "N/A"),
        "flexxible_mid":        device.get("FlexxibleMID", "N/A"),

        # Estado y conectividad
        "power_state":          device.get("PowerState", "N/A"),
        "agent_status":         device.get("FlexxAgentStatus", "N/A"),
        "agent_version":        device.get("FlexxAgentVersion", "N/A"),
        "last_report":          device.get("FlexxAgentLastReport", "N/A"),
        "last_seen":            device.get("LastTime", "N/A"),
        "last_restart_days":    device.get("LastRestartInDays", "N/A"),
        "reboot_pending":       device.get("RebootPending", "N/A"),
        "sessions":             device.get("SessionsCount", "N/A"),
        "idle_time":            device.get("IdleTime", "N/A"),

        # Red
        "ip":                   device.get("IP", "N/A"),
        "public_ip":            device.get("PublicIP", "N/A"),
        "mac":                  device.get("MACAddress", "N/A"),
        "subnet":               device.get("Subnet", "N/A"),
        "gateway":              device.get("DefaultGateway", "N/A"),
        "network_name":         device.get("NetworkName", "N/A"),
        "wifi_signal":          device.get("ConnectionSignal", "N/A"),
        "wifi_reliable":        device.get("WifiNetworkReliable", "N/A"),
        "network_type":         device.get("NetworkInterfaceType", "N/A"),

        # Hardware
        "cpu":                  device.get("CPU", "N/A"),
        "memory":               device.get("PercentRAM", "N/A"),
        "max_ram_gb":           device.get("MaxRAM", "N/A"),
        "cores":                device.get("cores", "N/A"),
        "disk_pct":             device.get("BootHardDiskUsedPercentage", "N/A"),
        "disk_detail":          device.get("HardDiskCSize", "N/A"),
        "is_physical":          device.get("IsPhysical", "N/A"),
        "hypervisor":           device.get("Hypervisor", "N/A"),
        "last_boot_duration":   device.get("LastBootDuration", "N/A"),

        # Sistema operativo
        "os":                   device.get("OperatingSystem", "N/A"),
        "os_build":             device.get("OSBuildNumber", "N/A"),
        "windows_type":         device.get("WindowsType", "N/A"),
        "last_windows_update":  device.get("LastWindowsUpdate", "N/A"),
        "days_since_update":    device.get("LastWindowsUpdateInDays", "N/A"),
        "fast_startup":         device.get("FastStartup", "N/A"),

        # Seguridad
        "antivirus":            device.get("Antivirus", "N/A"),
        "antivirus_status":     device.get("AntivirusStatus", "N/A"),
        "antivirus_version":    device.get("AntivirusVersion", "N/A"),
        "crowdstrike":          device.get("CrowdStrikeStatus", "N/A"),
        "crowdstrike_version":  device.get("CrowdStrikeVersion", "N/A"),
        "crowdstrike_alerts":   device.get("CrowdStrikeActiveDetections", "N/A"),
        "edr":                  device.get("EDR", "N/A"),
        "compliance":           device.get("ComplianceResult", "N/A"),
        "maintenance_mode":     device.get("IsInMaintenanceMode", "N/A"),

        # BIOS
        "bios_version":         device.get("BIOSVersion", "N/A"),
        "bios_manufacturer":    device.get("BIOSManufacturer", "N/A"),
        "bios_serial":          device.get("BIOSSerialNumber", "N/A"),
        "bios_smb":             device.get("BIOSSMBVersion", "N/A"),

        # Ubicación y organización
        "city":                 device.get("City", "N/A"),
        "country":              device.get("Country", "N/A"),
        "area":                 device.get("Area", "N/A"),
        "office":               device.get("Office", "N/A"),
        "department":           device.get("Department", "N/A"),
        "reporting_group":      device.get("ReportingGroup", "N/A"),
        "tenant":               device.get("RGTenant", "N/A"),
        "ou":                   device.get("OU", "N/A"),
        "broker":               device.get("Broker", "N/A"),

        # Ciclo de vida
        "creation_date":        device.get("CreationDate", "N/A"),
        "deletion_date":        device.get("DeletionDate", "N/A"),
        "days_for_deletion":    device.get("DaysForDeletion", "N/A"),

        # IoT / Agente
        "iot_config":           device.get("IoTHubConfig", "N/A"),
        "iot_status":           device.get("IoTHubDeviceStatus", "N/A"),
        "session_analyzer":     device.get("SessionAnalyzer", "N/A"),
        "session_analyzer_ver": device.get("SessionAnalyzerVersion", "N/A"),
        "unattended_remote":    device.get("UnattendedRemoteAssistance", "N/A"),
    }


def run_microservice(microservice_id: str, flx_unique_id: str, display_name: str = "Task from FlexxiBot") -> dict | None:
    """
    Ejecuta un microservicio en un dispositivo via Flexxible API.
    Devuelve la respuesta de la API o None si falla.
    """
    config = get_workspace("default")
    base_url = config.get("api_baseurl")
    user = config.get("api_user")
    password = config.get("api_pass")

    if not base_url:
        print("ERROR: API_BASEURL no configurada")
        return None

    try:
        response = requests.post(
            f"{base_url}/runMicroserviceAsTask",
            params={"apiversion": "1"},
            auth=(user, password),
            json={
                "displayname": display_name,
                "MicroserviceId": microservice_id,
                "FLXUniqueIDList": flx_unique_id,
                "SNOWEnvironmentList": "",
                "WorkspaceGroupIDList": ""
            },
            timeout=15
        )

        print(f"DEBUG runMicroservice status: {response.status_code}")
        print(f"DEBUG runMicroservice response: {response.text[:300]}")

        if response.ok:
            return response.json() if response.text else {"ok": True}
        else:
            print(f"Flexxible runMicroservice error: {response.status_code} {response.text}")
            return None

    except Exception as e:
        print(f"Error ejecutando microservicio: {e}")
        return None
