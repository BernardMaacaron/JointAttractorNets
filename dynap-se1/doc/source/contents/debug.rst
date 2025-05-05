Debugging
======================

1. "Failed to open USB device" error.

  Usually this can be solved if you unplug the USB cable and re-plug the DYNAP-SE1
  board to your machine. If not, it's probably due to the installation. You 
  should update your udev rules by doing the following.

* Make a file in /etc/udev/rules.d/ called 60-inilabs.rules

  .. code-block:: bash

      cd /etc/udev/rules.d
      cat 60-inilabs.rules

* Put the lines below into this file:

  .. code-block:: 

      # All DVS/DAVIS/Dynap-se systems
      SUBSYSTEM=="usb", ATTR{idVendor}=="152a", ATTR{idProduct}=="84[0-1]?", MODE="0666"

* Then, you run this command:

  .. code-block:: bash

      udevadm control --reload-rules

2. The GUI and `matplotlib.pyplot` may not work depending on your system.

- If you get the error below, please `open_dynapse1` without GUI.

  > samna.open_remote_node(visualizer_id, viz_name)
  RuntimeError: Store with ID: 3 timed out on content request

- If you get the error below, please avoid importing `matplotlib.pyplot` together with `Samna`.

  > free(): invalid pointer
  [1]    18258 abort (core dumped)