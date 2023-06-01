# Translate P3 dataset using Google Translate API

### Build Docker Image
```
docker build -t my-tor-proxy .
```

### Run Docker Container
```
docker run --name=my-tor-proxy --env=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin 
-p 8118:8118 -p 9095:9050 -p 9051:9051 vu-tor-proxy:latest
```

### Check if the tor proxy is working or not
```
curl -Lx http://localhost:8118 ifconfig.me
```

### Download dataset from 
```
python3 prepare_p3.py
```

### Translate data
  
```
python3 p3_translated.py 
```

### If exceptions occurs 
- Completed subsets are written in the new file 
- Rewritten the original task list file
- Run again with the above commands 
- In this implementation, the train and the validation subsets are separately translated, not parallel yet 

