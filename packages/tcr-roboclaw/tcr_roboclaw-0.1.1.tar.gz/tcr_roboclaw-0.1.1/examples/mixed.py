from tcr_roboclaw import Roboclaw

roboclaw = Roboclaw("/dev/ttyACM0", 115200)
roboclaw.open()

retLR = roboclaw.MixedLeftRight(50)  # 13
retForward = roboclaw.MixedForward(50)  # 8
retPos = roboclaw.BuffPositionM1M2(500, 500, 0)  # 121
retSADP = roboclaw.BuffSpeedAccelDeccelPositionM1M2(  # 67
    200, 1500, 200, 500, 200, 1500, 200, 500, 0  # WARNING: These values are not tested
)

print("Different kinds of methods to drive forward")
print(f"13 - MixedLeftRight : {retLR}")
print(f"8 - MixedForward : {retForward}")
print(f"121 - BuffPositionM1M2 : {retPos}")
print(f"67 - BuffSpeedAccelDeccelPositionM1M2 : {retSADP}")
