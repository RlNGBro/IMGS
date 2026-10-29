# PX4 OCORE-FLY BETA H743

Custom PX4 v1.17.0 board overlay for the `H743VIT6飞控板_new` / `OCORE-FLY BETA` flight controller.

Targets:

- `ocore_fly_beta_default`
- `ocore_fly_beta_bootloader`

Confirmed hardware mapping:

- MCU: STM32H743VIT6, 2 MB flash, 1 MB RAM, 8 MHz HSE
- ICM42607-P: SPI1, CS PA4, SCK PA5, MISO PA6, MOSI PA7, DRDY PC4
- BMI088: SPI2, accel CS PB12 / INT PB2, gyro CS PE12 / INT PE10
- DPS310: I2C2 PB10/PB11, address 0x76
- IST8310: I2C1 PB6/PB7
- AT7456E OSD: SPI3, CS PD4
- microSD: SDMMC1 4-bit, PC8-PC12 and PD2
- Motors 1-4: PA0-PA3 (TIM5 CH1-CH4)
- Motors 5-8: PE9/PE11/PE13/PE14 (TIM1 CH1-CH4)
- USB FS: PA11/PA12
- UART1-4, UART6-8 at the pins used by the project
- CAN1 logic: PD0/PD1, external transceiver required

The board-specific `icm42607p` driver is derived from PX4's register-compatible ICM-42670P driver, with the correct WHO_AM_I (`0x60`) and a conservative 1 MHz SPI clock validated on this PCB.

Build locally from a PX4 v1.17.0 checkout:

```sh
cp -a overlay/. /path/to/PX4-Autopilot/
cd /path/to/PX4-Autopilot
make ocore_fly_beta_default
make ocore_fly_beta_bootloader
```

This repository contains board support and build automation only. Flight control tuning, airframe selection, sensor calibration, actuator mapping, and bench validation still have to be completed after flashing.
