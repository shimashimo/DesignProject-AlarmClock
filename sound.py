import machine, time


p4 = machine.Pin(4)
speaker = machine.PWM(p4)
speaker.duty_u16(int(65535/2))

speaker.freq(554)
time.sleep(1)
speaker.freq(494)
time.sleep(1)
speaker.freq(440)
time.sleep(1.5)

print("First")

speaker.freq(554)
time.sleep(1)
speaker.freq(494)
time.sleep(1)
speaker.freq(440)
time.sleep(1.5)

speaker.duty_u16(0)
