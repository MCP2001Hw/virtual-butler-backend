import database_execute
import decimal
import datetime
import random

def update_device_stats(deviceID, deviceType, deviceUsage, devicestatus):
    """Fetches device energy data and updates the database with usage stats."""

    # Fetch device type-specific energy consumption and generation per hour
    device_data = database_execute.execute_SQL("""
        SELECT energyConsumptionPerHour, energyGenerationPerHour FROM DeviceData WHERE deviceType = %s
    """, (deviceType,))

    # Safety check: Ensure device_data is not empty or None
    if not device_data or not device_data[0]:
        print(f"⚠️ Warning: No data found for deviceType '{deviceType}'. Skipping update.")
        return False  # Prevents further execution if data is missing

    # Generate efficiency factor (random value between 0.75 and 1.25)
    efficiency = decimal.Decimal(random.uniform(0.75, 1.25))

    # Extract energy values safely
    energyConsumptionPerHour = decimal.Decimal(device_data[0][0]) if device_data[0][0] is not None else decimal.Decimal("0.00")
    energyGenerationPerHour = decimal.Decimal(device_data[0][1]) if device_data[0][1] is not None else decimal.Decimal("0.00")

    # Compute actual energy consumption & generation based on usage
    energyConsumption = energyConsumptionPerHour * (decimal.Decimal(deviceUsage) / (60 * 60)) * efficiency
    energyGeneration = energyGenerationPerHour * (decimal.Decimal(deviceUsage) / (60 * 60)) * efficiency
    costsOfEnergy = energyConsumption * decimal.Decimal('0.27')

    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare data tuple for insertion
    data = (
        deviceID,
        energyConsumption,
        energyGeneration,
        costsOfEnergy,
        deviceUsage,
        devicestatus,
        timestamp,
        efficiency
    )

    # Execute SQL insertion with proper safety
    try:
        database_execute.execute_SQL("""
            INSERT INTO DeviceStats (
                deviceId, 
                energyConsumption, 
                energyGeneration, 
                costsOfEnergy, 
                deviceUsage, 
                deviceStatus, 
                timestamp, 
                efficiency
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        print(f"✅ Device {deviceID} stats updated successfully.")
        return True  # Indicate success

    except Exception as e:
        print(f"❌ Error updating device {deviceID} stats: {e}")
        return False  # Indicate failure