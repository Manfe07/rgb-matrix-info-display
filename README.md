# rgb-matrix-info-display

This project sets up an info display using a LED Matrix Display from Sparkfun, AdaFruit or eBay and Aliexpress. By using the awesome [rpi-rgb-led-matrix library](https://github.com/hzeller/rpi-rgb-led-matrix) from _hzeller_ it currently displays the current date and time, outside temperature (needs to be replaced by custom datasource) and currently playing title and artist of my multiroom audio system (needs also be replaced by custom datasource).

## Setup

* Compile and install the `rpi-rgb-led-matrix` library according to the [readme](https://github.com/hzeller/rpi-rgb-led-matrix).
* Install dependencies:

    ```bash
    pip install paho-mqtt 
    pip install requests
    ```

## Run the program

```bash
python3 -u main.py
```


## ArtNet
If you want to use the ArtNet function first activate it in the config.yaml and choose the dmx universe
```yaml
[ArtNet]
enabled = true
universe = 0
```

The `ArtNet.addLight(addr, x, y, w, h)` function will create a 3-Channel RGB Fixture with the desiered dmx-addres, position and pixel size.
