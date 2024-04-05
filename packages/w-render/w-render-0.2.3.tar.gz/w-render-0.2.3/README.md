### Description

Web-render is a method of rendering dynamic web pages using Selenium.

### Commands

To start the rendering service, use the following command:

```shell
render-server "web-render -f selenium --headless --proxy=185.105.91.140:1021" "flask-backend"
```

To run a test, use the following command:

```shell
python -W ignore:ResourceWarning -m unittest web_render/base/test_webrender.py
```

```shell
render-server \
  "web-render -f selenium --chrome-driver-version=116.0.5845.110 --proxy 95.213.10.169:1022 --port 21000" \
  "flask-backend --port 5000 --render-address localhost:21000"
```