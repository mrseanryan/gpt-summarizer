### Using GPU with the local model

If you have an NVIDIA graphics card, then you can run part or all of the model (depending on the card's RAM) on the GPU,
which has much higher level of parallelism than the typical CPU.

Required:

- latest NVIDIA graphic driver
- up to date version of CUDA

#### Tip: if you get errors when running the model, like this:

```
>> Cuda error: no kernel image is available for execution on the device
```

Then recommend to build ctransformers locally.

This is actually quite simple:

```
pip3 uninstall ctransformers
pip3 install ctransformers --no-binary ctransformers # use --no-binary to force a local build. This ensures that the local version of CUDA and NVIDIA graphics driver will be used.
```

You can tweak the settings in `config.py`.

For more details, see the main tool [ctransformers](https://github.com/marella/ctransformers).
