# metar-data-api
This is a RESTful API built using Flask that will make an external request to fetch METAR data and return the latest weather info given a specific station code (scode). It will also cache the received responses for 5 minutes. Until explicitly specified, data will be fetched and returned from the cache and a request to the server will not be made if a particular scode's data is already present in the cache within the 5 minutes.

# Setup and run instructions:

1. Create a virtual environment
2. Activate the virtual environment
3. Install all dependencies using the following command:
    ```
    pip install -r requirements.txt
    ```
4. Run the server using the following command:
    ```
    flask run
    ```
    This will start a server with the url 
    ```
    http://127.0.0.1:5000
    ```
5. Run the redis server using the following command:
    ```
    sudo service redis-server start
    ```
    This will start a server with the url 
    ```
    127.0.0.1:6379
    ```
    If not, please update line 175 in routes/api.py to reflect the url on which your redis server is running.

This API supports two endpoints:
 ```
GET /api/ping and GET /api?scode=<scode>&nocache=<nocache>
```
GET /api/ping:
```
Return a successful response if a ping to the server is successful.
Status codes: 200
Accepted request headers(These headers are optional. The API will work even if headers are not specified): content-type: application/json
Response header: content-type: application/json
Required Request payload: None
Sample response: 
    200: {
            "data": "pong"
         }
```

GET /api?scode=<scode>&nocache=<nocache>:
```
Returns METAR data as JSON.
Status codes: 200, 400, 500
Accepted request headers(These headers are optional. The API will work even if headers are not specified): content-type: application/json
Response header: content-type: application/json
Required Request payload: None
Query parameters: 
    1. scode - required
    2. nocache - optional
Accepted values for nocache: 1
When thevalue of nocache is 1, live data will be fetched from METAR. The cache will also be refreshed.
Sample response:
    200: {
            "data": {
                        "last_observation": "2011/03/16 at 05:30 GMT",
                        "station": "ABBN",
                        "temperature": "2.0 C (35.60 F)",
                        "wind": "SW at 4.60 mph (04 knots)"
                    }
         },
    400: {
            "error": "Invalid scode"
         },
    500: {
            "error": "Internal server error"
         }
    
```