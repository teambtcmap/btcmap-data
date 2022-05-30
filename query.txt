[out:json][timeout:300];
(
    node["currency:XBT"="yes"];
    way["currency:XBT"="yes"];
    relation["currency:XBT"="yes"];
    node["currency:BTC"="yes"];
    way["currency:BTC"="yes"];
    relation["currency:BTC"="yes"];
    node["payment:bitcoin"="yes"];
    way["payment:bitcoin"="yes"];
    relation["payment:bitcoin"="yes"];
);
out meta geom;
