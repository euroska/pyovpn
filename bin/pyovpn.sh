#!/bin/bash
SERVER="https://pyovpn.miksanik.net/api/jsonrpc"
TOKEN="4dd836a1cfdb34579d4790cec98f0d79ee06db751989f4259db17698109bc7e4"
USER="euro"
VPN="common"
CONFIG_PATH="/home/euro/out.ovpn"


# command to get new config
COMMAND="
curl -X POST
  -s
  -H 'Cache-Control: no-cache'
  -H 'Content-Type: application/json'
  -H 'X-Token: $TOKEN'
  -d '{\"message\": \"pyovpn.vpn.user.config\",\"body\": {\"name\": \"$VPN\",\"username\": \"$USER\"}}'
  $SERVER
"

# extract configuration
NEW_CONFIG=`eval $COMMAND | python -c "import sys,json; obj=json.load(sys.stdin); print(obj['body']['config']);"`

# if configuration has been sucessfuly downloaded
if [ $? -eq 0 ]
then
	OLD_CONFIG=`cat "$CONFIG_PATH"`

	# if configuration is different from current
	if [ "$NEW_CONFIG" != "$OLD_CONFIG" ]
	then
		echo "RELOAD ovpn"
		echo "$NEW_CONFIG" >  "$CONFIG_PATH"
		pkill -1 openvpn
		exit 0
    # configuration is same
	else
        exit 0
		# echo "CONFIG IS SAME"
	fi
# there was problem with download
else
	echo "Get config FAILED!!!"
	exit 1
fi
