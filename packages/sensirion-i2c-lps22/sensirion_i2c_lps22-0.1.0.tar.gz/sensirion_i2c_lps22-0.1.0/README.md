# Python I2C Driver for ST LPS22 sensor

This repository contains the Python driver to communicate with a ST LPS22 pressure sensor over I2C. 

<img src="https://raw.githubusercontent.com/Sensirion/python-i2c-lps22/master/images/product-image-st-lps22.jpeg"
width="300px" alt="LPS22 picture">


Click [here](https://www.st.com/en/mems-and-sensors/lps22hb.html) to learn more about the Sensirion LPS22 sensor.


For details about the command please consult the [datasheet](https://www.st.com/resource/en/datasheet/lps22hb.pdf).


The default I²C address of [LPS22](https://www.st.com/en/mems-and-sensors/lps22hb.html) is **0x5C**.


## Documentation & Quickstart

See the [documentation page](https://sensirion.github.io/python-i2c-lps22) for an API description and a 
[quickstart](https://sensirion.github.io/python-i2c-lps22/execute-measurements.html) example.


## Contributing

We develop and test this driver using our company internal tools (version
control, continuous integration, code review etc.) and automatically
synchronize the `master` branch with GitHub. But this doesn't mean that we
don't respond to issues or don't accept pull requests on GitHub. In fact,
you're very welcome to open issues or create pull requests :-)

### Check coding style

The coding style can be checked with [`flake8`](http://flake8.pycqa.org/):

```bash
pip install -e .[test]  # Install requirements
flake8                  # Run style check
```

In addition, we check the formatting of files with
[`editorconfig-checker`](https://editorconfig-checker.github.io/):

```bash
pip install editorconfig-checker==2.0.3   # Install requirements
editorconfig-checker                      # Run check
```

## License

See [LICENSE](LICENSE).
