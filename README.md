# PyOvpn

Utility to orchestrate OpenVPN servers
Is simple Python AsyncIO application, which listen on websocket and JsonRPC interfaces.
When OpenVPN deamon is lunched, all log are accesible throught interface
All conected clients are showed in web interface

All prerequisites for alpinelinux is in alpine.packages

```bash
pyovpn -g # generate config example
pyovpn -c config.yml # run the app
```

It's not done yet, please be patient
