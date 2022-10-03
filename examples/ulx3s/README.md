# About

``hello.v`` does the following:
 - displays a binary counter onto 4 LEDs
 - forms a UART loopback with the host computer
 - displays the value sent from the host computer
   to the LEDs briefly before switching back to the counter display
 - sends an ASCII value composed of some upper bits of the
   counter periodically to the host computer

# Running
Here is an example of how you might program and test the
``hello.v`` example into your ulx3s 85k FPGA. The device in
the screen command is probably MacOS specific.

You may have to install 
[openFPGALoader](https://github.com/trabucayre/openFPGALoader).

```bash
make -f 85k.mk hello.bit
openFPGALoader -f -b ulx3s hello.bit
screen /dev/tty.usbserial-K00027 9600
```