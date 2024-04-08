## Common utilities used in BT testing
This package is used to hold common utilities for BT testing.

## Installation
You can install the released package from pip:

```shell
$ pip install bttc
```

or download the source then run command below to use the latest version:

```shell
$ git clone https://github.com/johnklee/bt_test_common.git
$ cd bt_test_common
$ pip install .
```

You may need `sudo` for the above commands if your system has certain permission restrictions.

## Basic Usage

### Retrieve device
You can use function `get_all` to retrieve all local connected adb devices:

```shell
$ adb devices
List of devices attached
07311JECB08252  device
36121FDJG000GR  device

$ python
>>> import bttc
>>> devices = bttc.get_all()
>>> devices['07311JECB08252'].gm.sdk
34
```

Or use function `get` to retrieve a specific device by its serial number:

```shell
>>> import bttc
>>> dut = bttc.get('07311JECB08252', {'wifi'})
>>> dut.wifi.status()
<WifiStatus.ENABLED: 'enabled'>
```

## Release info
* Release v0.0.73: #158, #163
* Release v0.0.72: #153, #155, #51, #157
* Release v0.0.71: #123, #134, #140
* Release v0.0.70: #128, #132, #135
* Release v0.0.69: #58, #59, #63, #109, #111, #113, #116, #119
* Release v0.0.68: #99, #101, #103
* Release v0.0.67: #90, #91, #95
* Release v0.0.66: #67, #84, #85
* Release v0.0.65: #76, #78, #80
