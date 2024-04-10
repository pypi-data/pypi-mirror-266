from tcr_roboclaw import Roboclaw

roboclaw = Roboclaw("/dev/ttyACM0", 115200)
roboclaw.open()

print(roboclaw.ReadVersion())

print("M1", roboclaw.ReadEncM1())
print("M2", roboclaw.ReadEncM2())

roboclaw.ResetEncoders()

print("M1", roboclaw.ReadEncM1())
print("M2", roboclaw.ReadEncM2())

ret = roboclaw.ForwardM1(127)
print(ret)
