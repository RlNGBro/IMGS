#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "px4")
board = root / "boards/ocore/fly_beta"
driver = root / "src/drivers/imu/invensense/icm42607p"

required = [
    board / "default.px4board",
    board / "bootloader.px4board",
    board / "src/board_config.h",
    board / "src/spi.cpp",
    board / "src/timer_config.cpp",
    board / "nuttx-config/include/board.h",
    driver / "Kconfig",
    driver / "InvenSense_ICM42607P_registers.hpp",
]
missing = [str(p) for p in required if not p.is_file()]
assert not missing, f"missing overlay files: {missing}"

def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

defaults = text(board / "default.px4board")
for item in [
    'CONFIG_DRIVERS_IMU_INVENSENSE_ICM42607P=y',
    'CONFIG_DRIVERS_IMU_BOSCH_BMI088=y',
    'CONFIG_DRIVERS_BAROMETER_DPS310=y',
    'CONFIG_DRIVERS_MAGNETOMETER_ISENTEK_IST8310=y',
    'CONFIG_DRIVERS_OSD_ATXXXX=y',
    'CONFIG_BOARD_SERIAL_GPS1="/dev/ttyS1"',
    'CONFIG_BOARD_SERIAL_TEL2="/dev/ttyS4"',
]:
    assert item in defaults, f"missing px4board option: {item}"

nuttx = text(board / "nuttx-config/include/board.h")
for item in [
    '#define GPIO_SPI1_SCK    ADJ_SLEW_RATE(GPIO_SPI1_SCK_1) /* PA5  */',
    '#define GPIO_SPI1_MISO   GPIO_SPI1_MISO_1               /* PA6  */',
    '#define GPIO_SPI1_MOSI   GPIO_SPI1_MOSI_1               /* PA7  */',
    '#define GPIO_SPI2_MISO   GPIO_SPI2_MISO_1               /* PB14 */',
    '#define GPIO_SPI2_MOSI   GPIO_SPI2_MOSI_1               /* PB15 */',
    '#define GPIO_SPI3_SCK    ADJ_SLEW_RATE(GPIO_SPI3_SCK_1) /* PB3  */',
    '#define GPIO_I2C1_SCL GPIO_I2C1_SCL_1       /* PB6  */',
    '#define GPIO_I2C2_SDA GPIO_I2C2_SDA_1       /* PB11 */',
    '#define GPIO_CAN1_RX     GPIO_CAN1_RX_3     /* PD0  */',
    '#define GPIO_CAN1_TX     GPIO_CAN1_TX_3     /* PD1  */',
]:
    assert item in nuttx, f"missing pin mapping: {item}"
assert 'GPIO_UART7_RTS' not in nuttx, "UART7 RTS still conflicts with motor 5 on PE9"
board_config = text(board / "src/board_config.h")
assert "GPIO_CAN1_RX, \\\n\n" not in board_config, "PX4_GPIO_INIT_LIST macro was terminated by a blank line"
assert 'GPIO_UART7_CTS' not in nuttx, "UART7 CTS still conflicts with BMI088 INT3 on PE10"
nsh = text(board / "nuttx-config/nsh/defconfig")
assert '# CONFIG_STM32H7_SPI4 is not set' in nsh
assert '# CONFIG_UART7_IFLOWCONTROL is not set' in nsh
assert '# CONFIG_UART7_OFLOWCONTROL is not set' in nsh

spi = text(board / "src/spi.cpp")
for item in [
    'DRV_IMU_DEVTYPE_ICM42670P, SPI::CS{GPIO::PortA, GPIO::Pin4}, SPI::DRDY{GPIO::PortC, GPIO::Pin4}',
    'DRV_ACC_DEVTYPE_BMI088, SPI::CS{GPIO::PortB, GPIO::Pin12}, SPI::DRDY{GPIO::PortB, GPIO::Pin2}',
    'DRV_GYR_DEVTYPE_BMI088, SPI::CS{GPIO::PortE, GPIO::Pin12}, SPI::DRDY{GPIO::PortE, GPIO::Pin10}',
    'DRV_OSD_DEVTYPE_ATXXXX, SPI::CS{GPIO::PortD, GPIO::Pin4}',
]:
    assert item in spi, f"missing SPI device mapping: {item}"

timers = text(board / "src/timer_config.cpp")
for pin in [
    '{GPIO::PortA, GPIO::Pin0}', '{GPIO::PortA, GPIO::Pin1}',
    '{GPIO::PortA, GPIO::Pin2}', '{GPIO::PortA, GPIO::Pin3}',
    '{GPIO::PortE, GPIO::Pin9}', '{GPIO::PortE, GPIO::Pin11}',
    '{GPIO::PortE, GPIO::Pin13}', '{GPIO::PortE, GPIO::Pin14}',
]:
    assert pin in timers, f"missing motor timer pin: {pin}"

regs = text(driver / "InvenSense_ICM42607P_registers.hpp")
assert 'WHOAMI = 0x60;' in regs
assert 'SPI_SPEED = 1 * 1000 * 1000;' in regs
assert 'PWR_MGMT0         = 0x1F,' in regs
assert 'GYRO_CONFIG0      = 0x20,' in regs
assert 'ACCEL_CONFIG0     = 0x21,' in regs

prototype = text(board / "firmware.prototype")
hw_config = text(board / "src/hw_config.h")
assert '"board_id": 1207' in prototype
assert '#define BOARD_TYPE                     1207' in hw_config
assert '#define BOARD_USB_VBUS_SENSE_DISABLED' in hw_config
assert '#define APP_RESERVATION_SIZE (128 * 1024)' in hw_config
assert '#define FLASH_BASED_PARAMS' in text(board / "src/board_config.h")
assert '#include <parameters/flashparams/flashfs.h>' in text(board / "src/init.c")
assert 'parameter_flashfs_init(params_sector_map' in text(board / "src/init.c")
assert '{15, 128 * 1024, 0x081E0000}' in text(board / "src/init.c")
assert 'LENGTH = 1792K' in text(board / "nuttx-config/scripts/script.ld")
boot_main = text(root / "platforms/nuttx/src/bootloader/stm/stm32_common/main.c")
assert '#if INTERFACE_USB && !defined(BOARD_USB_VBUS_SENSE_DISABLED)' in boot_main
init_c = text(board / "src/init.c")
assert "int board_read_VBUS_state(void)" in init_c
vbus_body = init_c.split("int board_read_VBUS_state(void)", 1)[1].split("}", 1)[0]
assert "return 0;" in vbus_body, "VBUS placeholder must return 0 (connected convention)"

print("PX4 OCORE-FLY BETA overlay validation passed")










