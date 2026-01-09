import time
import cflib.crtp
import cflib.crtp.udpdriver
from cflib.crazyflie import Crazyflie

# ================= CONFIG =================
DRONE_URI = "udp://192.168.43.42:14550"  # No port needed — CRTP uses default
ROLL_TRIM = 0.0
PITCH_TRIM = 0.0

# Thrust settings
THRUST_MIN = 10000
THRUST_HOVER = 35000
THRUST_MAX = 60000

FW_PITCH = 10.0     # forward/backward tilt
MOVE_DURATION = 1.0 # seconds

# =========================================

# Initialize the drivers
cflib.crtp.init_drivers(enable_debug_driver=False)

print("Connecting to LiteWing at", DRONE_URI)
cf = Crazyflie(rw_cache=".cache")
cf.open_link(DRONE_URI)

# Allow link establishment
time.sleep(2.0)

if not cf.is_connected():
    print("❌ FAILED TO CONNECT — Check WiFi and Firewall")
    exit(1)

print("✅ CONNECTED")

# Function to send setpoints
def send_setpoint(r, p, y, t):
    cf.commander.send_setpoint(r + ROLL_TRIM,
                               p + PITCH_TRIM,
                               y,
                               max(0, min(THRUST_MAX, t)))

print("Arming (zero setpoint)...")
send_setpoint(0.0, 0.0, 0.0, 0)
time.sleep(0.1)

print("Taking off (gentle thrust)...")
send_setpoint(0.0, 0.0, 0.0, THRUST_HOVER)
time.sleep(2.0)

print("Forward movement...")
start = time.time()
while time.time() - start < MOVE_DURATION:
    send_setpoint(0.0, FW_PITCH, 0.0, THRUST_HOVER)
    time.sleep(0.1)

print("Hovering...")
send_setpoint(0.0, 0.0, 0.0, THRUST_HOVER)
time.sleep(1.0)

print("Backward movement...")
start = time.time()
while time.time() - start < MOVE_DURATION:
    send_setpoint(0.0, -FW_PITCH, 0.0, THRUST_HOVER)
    time.sleep(0.1)

print("Landing...")
for t in range(THRUST_HOVER, 0, -3000):
    send_setpoint(0.0, 0.0, 0.0, t)
    time.sleep(0.1)

print("Stopping")
send_setpoint(0.0, 0.0, 0.0, 0)
cf.close_link()
print("Done")
