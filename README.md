# SSU-Research
A research project about security in usable enviroments

## Android build

This app can be packaged as an Android APK with Buildozer.

1. Use Linux or WSL2, not native Windows.
2. Install Buildozer and its Android build dependencies.
3. From the repository root, build the app with:

```bash
buildozer -v android debug
```

The Android entrypoint is [`App/main.py`](App/main.py), which loads [`App/VaultedPass.py`](App/VaultedPass.py).
