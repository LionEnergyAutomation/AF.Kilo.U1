import netgear_class
import time

ntg = netgear_class.netgear_switch()

updown, status = ntg.retrieve_data(port=3)

time.sleep(5)

print("updown is: " + str(updown) + " status is: " + status)

ntg.set_port(port=3, status='disable')

time.sleep(5)

updown, status = ntg.retrieve_data(port=3)

print("updown is: " + str(updown) + " status is: " + status)

ntg.set_port(port=3, status="enable")

time.sleep(5)

updown, status = ntg.retrieve_data(port=3)

print("updown is: " + str(updown) + " status is: " + status)