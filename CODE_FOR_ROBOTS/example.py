import rtde_control
import rtde_receive
import rtde_io
import time
import numpy as np

ROBOT_IP = "192.168.77.2"

# ─── Connect ───────────────────────────────────────────────
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
rtde_io = rtde_io.RTDEIOInterface(ROBOT_IP)

# ─── Read current state ────────────────────────────────────
actual_q = rtde_r.getActualQ()
actual_pose = rtde_r.getActualTCPPose()
actual_speed = rtde_r.getActualTCPSpeed()
print(f"Current joints: {actual_q}")
print(f"Current TCP:    {actual_pose}")

# ─── Move (joint space) ────────────────────────────────────
rtde_c.moveJ(actual_q, speed=0.1, acceleration=0.1)

# ─── Move (Cartesian space) ────────────────────────────────
pose1 = [0.4, 0.0, 0.3, 0.0, 3.14, 0.0]
pose2 = [0.4, 0.2, 0.3, 0.0, 3.14, 0.0]
# rtde_c.moveL(pose1, speed=0.1, acceleration=0.1)
rtde_c.moveL(pose2, speed=0.1, acceleration=0.1)

pose3 = [0.5, 0.2, 0.3, 0.0, 3.14, 0.0]
pose4 = [0.5, 0.0, 0.3, 0.0, 3.14, 0.0]
rtde_c.moveL(pose3, speed=0.1, acceleration=0.1)
rtde_c.moveL(pose4, speed=0.1, acceleration=0.1)

rtde_c.moveL(pose1, speed=0.1, acceleration=0.1)

# ─── Set digital output ON ─────────────────────────────────
rtde_io.setStandardDigitalOut(0, True)
print(f"Digital in 0 (ON):  {rtde_r.getDigitalInState(0)}")

time.sleep(2)

# ─── Set digital output OFF ────────────────────────────────
rtde_io.setStandardDigitalOut(0, False)
print(f"Digital in 0 (OFF): {rtde_r.getDigitalInState(0)}")

# ─── Set payload ───────────────────────────────────────────
rtde_c.setPayload(mass=0.5, center=[0, 0, 0.1])

# ─── Close ─────────────────────────────────────────────────
rtde_c.close()
rtde_r.close()
rtde_io.close()   