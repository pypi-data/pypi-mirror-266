chmod -R 777 /kcwebplus
./server stop
nohup ./server --h 0.0.0.0 --p 39001 --w 2 start > server.log 2>&1 &
nohup ./server --h 0.0.0.0 --p 39002 --w 2 start > server.log 2>&1 &
nohup ./server --h 0.0.0.0 --p 39003 --w 2 start > server.log 2>&1 &
nohup python3.6kcw_plus server.py intapp/index/pub/clistartplan --cli > server.log 2>&1 &