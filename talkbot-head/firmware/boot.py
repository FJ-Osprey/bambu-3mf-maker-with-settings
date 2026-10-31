# Turn on the second USB serial port (usb_cdc.data) that code.py reads angles from. The first (console) stays
# for the REPL. Copy to the CIRCUITPY drive root; takes effect after a power cycle.
import usb_cdc

usb_cdc.enable(console=True, data=True)
