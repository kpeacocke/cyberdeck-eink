# KP cyberdeck hardware

## Current software

The complete dashboard is [kpeacocke/pi-environment-panel](https://github.com/kpeacocke/pi-environment-panel).
It runs from `/opt/pi-environment-panel` via `pi-environment-panel.service`, using
`/etc/pi-environment-panel/config.toml`. The original editable source is in
`/home/kpeacocke/Downloads/pi-environment-panel`. This repository supplies hardware
configuration and UART diagnostics; it does not itself render the dashboard.

## Verified UART routing

SSH inspection on 11–12 September 2026 found Raspberry Pi 5 Model B Rev 1.1,
Debian 13.6 (trixie), kernel `6.18.39+rpt-rpi-2712`.

| Device | Connection | Consumer |
| --- | --- | --- |
| `/dev/ttyAMA10` | Dedicated small 3-pin UART connector | E-paper dashboard |
| `/dev/ttyAMA0` | GPIO14 TX/header pin 8, GPIO15 RX/header pin 10 | SIMCOM SIM7600NA-H modem/GNSS, identified by AT response |
| Internal `ttyS0` controller | BCM2712 Bluetooth UART | Kernel `hci_uart_bcm`; no `/dev/ttyS0` node |
| RP1 UART1–5 | Disabled in live device tree | None |

**The alias changed across boots:** `/dev/serial0` pointed to `ttyAMA0` on the
first inspection and `ttyAMA10` after the subsequent reboot. Use explicit device
paths for both application ports. Do not point the GPS at `/dev/serial0`.

Both ttyAMA devices are `root:dialout` mode 0660; `kpeacocke` belongs to dialout,
gpio and i2c. No serial console is specified in `/proc/cmdline` (`console=tty1`).
The serial-getty instances were inactive. No USB serial or ACM devices were found;
`lsusb` listed root hubs only. A momentary `lsof`/`fuser` check can miss the panel
service because it opens the port briefly for refreshes. Bluetooth is a kernel
consumer, not a userspace file holder.

## Display connections

The photographed controller has a labelled six-pin connector, a lit LED and an
STM32F103ZET6 chip. Its layout and existing driver are consistent with the Waveshare
4.3-inch 800×600 UART module. The following auxiliary wiring was confirmed by the
user; photographs alone do not establish continuity through the HAT stack.

| Display wire | Signal | Pi connection |
| --- | --- | --- |
| Red | VCC | Physical pin 17, 3.3V |
| Yellow | WAKE_UP | Physical pin 15, GPIO22 |
| Blue | RESET | Physical pin 11, GPIO17 |
| White | DOUT | Dedicated UART pin 1, Pi RX |
| Black | GND | Dedicated UART pin 2, GND |
| Green | DIN | Dedicated UART pin 3, Pi TX |

These colours refer to the **display harness**, not an arbitrary Pi adapter cable.
Identify adapter conductors by continuity to connector pin numbers, not colour.
A photo-based suspicion about adapter colours was not electrically verified and
must not be treated as a confirmed fault. Wire joints should be secure and insulated.

Waveshare specifies VCC 3.3–5.5V. Its state LED is off in sleep, so an unlit LED
alone does not prove a power failure. It wakes on a rising WAKE_UP edge.
Sources: [Waveshare module](https://www.waveshare.com/wiki/4.3inch_e-Paper_UART_Module),
[Pi connector specification](https://datasheets.raspberrypi.com/debug/debug-connector-specification.pdf).

## Active boot configuration

Relevant settings in `/boot/firmware/config.txt`:

```ini
dtoverlay=vc4-kms-v3d
[pi5]
dtoverlay=nospi10
[all]
dtparam=i2c_arm=on
enable_uart=1
dtparam=uart0=on
dtparam=pciex1=on
dtparam=pciex1_gen=2
dtoverlay=pciex1-compat-pi5,no-mip
usb_max_current_enable=1
dtoverlay=rpi-dacpro
dtoverlay=rpi-sense-v2
```

`dtparam=spi=on` is commented out; no spidev nodes were present.
`dtoverlay=dwc2,dr_mode=host` is under `[cm5]`, not active for this Pi 5.
`dtoverlay -l` reported no runtime overlays; this does not negate boot-time overlays.
GPIO2/3 are I2C SDA/SCL (pins 3/5). GPIO18/19/20/21 are I2S0
SCLK/WS/SDI0/SDO0 (pins 12/35/38/40). GPIO23 is an input. GPIO16/17 had no UART
flow-control function; UART0 CTS/RTS is not enabled.

## Observations and remaining uncertainty

The existing dashboard README recorded an earlier successful `OK` response at
115200 on `ttyAMA10`. The user also reported a visible dashboard after restarting.
However, the next live inspection showed recurring failed handshakes and zero
UART10 RX bytes since that boot. A static retained e-paper image is not proof of
continuing updates. The root cause of this intermittent/unverified display path
has not been established. No boot/UART configuration changes were made by this work.

The systemd working directory was corrected to `/var/lib/pi-environment-panel`
after lgpio FIFO creation errors in `/`. The running app's explicit port, baud,
WAKE GPIO22 and RESET GPIO17 were verified. Reset/wake tests did not establish a
working serial exchange. The updated dashboard records display command-send status
separately from sensor sampling. It does not mark failed handshakes as success.

The SIM7600NA-H replied to AT commands on `ttyAMA0` at 115200. Its GNSS engine
was off; enabling it returned OK. GPS-based weather is implemented in the dashboard.
A missing satellite fix must remain unavailable, not become a 0,0 weather request.
No coordinates, modem identifiers, private keys or runtime state belong in Git.
