import dynapse1utils as ut

"""
Outdated testing code for samna 0.8.32.0
"""

device_name = "dynapse1"
store, gui_process = ut.open_dynapse1(device_name)
model = getattr(store, device_name)

while True:
    pass