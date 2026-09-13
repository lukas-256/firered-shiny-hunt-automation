# ShinyHunting

Screen-aware shiny-hunting automation for Pokémon FireRed. The Python program
reads frames from an HDMI capture card and sends controller input through a
USB-to-UART adapter and an ATmega32U4 Pro Micro.

This project has been tested with a Nintendo Switch 2, a UGREEN 25854/CM716
capture card, a 5 V/16 MHz USB-C Pro Micro, a DSD TECH SH-U09C2 USB-to-TTL
adapter, and macOS. Similar hardware may work but is untested.

See [USAGE.md](USAGE.md) for the hardware diagram, wiring, firmware build and
flash procedure, configuration, CLI examples, reference-image workflow, and
troubleshooting guide.
