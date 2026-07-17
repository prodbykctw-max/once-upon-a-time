import os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\fw_test_wall.png"

sc = reset_scene()
wall = plane((0,0.1,0), 4, stone_mat('W', (0.4,0.3,0.2)), rot=(math.pi/2,0,0))
shelf = cube((0,-0.1,0.3), (1.6,0.15,0.05), wood_mat('S'))
trim = cube((0,-0.12,0.9), (1.6,0.03,0.04), gold_mat('G'))
orb = sphere((0.4,-0.2,0.5), 0.12, marble_mat('M'))
glow = sphere((-0.5,-0.2,0.55), 0.06, emissive_mat('E'))
wall_cam()
warm_rig()
render_to(OUT, 144, 192, samples=96)
print("FW_TEST_OK")
