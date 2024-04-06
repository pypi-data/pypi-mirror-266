# GP8XXX-IIC

The GP8XXX-IIC module provides an interface for controlling DAC (Digital to Analog Converter) devices over the I2C protocol. This module supports various DAC models with different resolutions and output voltage ranges.

## Features

- **I2C Communication**: Utilizes the smbus2 library for communicating with DAC devices over the I2C bus.
- **Output Ranges**: Supports different output voltage ranges including 0-5V, 0-10V.
- **Support Multiple DAC Models**:
  - GP8503: 12-bit DAC Dual Channel I2C to 0-2.5V/0-VCC
  - GP8211S: 15-bit DAC I2C to 0-5V/0-10V
  - GP8512: 15-bit DAC I2C to 0-2.5V/0-VCC
  - GP8413: 15-bit DAC Dual Channel I2C to 0-10V
  - GP8403: 12-bit DAC Dual Channel I2C to 0-5V/0-10V
  - GP8302: 12-bit DAC Dual Channel I2C to 0-5V/0-10V

## Installation
You can install the GP8XXX module from PyPI using pip:

```bash
pip install GP8XXX-IIC
```

## Example
```python
import time
from GP8XXX_IIC import GP8403

GP8403 = GP8403(i2c_addr=0x5F, auto_range=True)

while GP8403.begin():
    print("init error")
    time.sleep(1)

# Optional
# GP8403.set_dac_outrange(GP8403.OUTPUT_RANGE_10V)

# Chanel 1: 6.721V
GP8403.set_dac_out_voltage(voltage=6.821, channel=0)

time.sleep(3)

# Chanel 2: 2.774V
GP8403.set_dac_out_voltage(voltage=2.774, channel=1)

time.sleep(3)

# Chanel 1 & 2: 0.253V
GP8403.set_dac_out_voltage(voltage=0.253, channel=2)
```

## Tested devices

| DAC Module | Tested |
|------------|--------|
|GP8503      | ❌     |
|GP8211S     | ❌     |
|GP8512      | ❌     |
|GP8512      | ❌     |
|GP8413      | ❌     |
|GP8403      | ✅     |
|GP8302      | ❌     |