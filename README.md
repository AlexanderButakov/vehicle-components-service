# README #

## Service description ##

The service listens to a websocket and gets data in the following format:  
```
{
 "component": "Realbridge Air Amplifier",
 "country": "Argentina",
 "description": "ut rerum ut quis nulla quasi quis est autem.",
 "model": "mh 80151"
 }
```
If the data is a valid json, it is stored in MongoDB and returned via API in pages.


## Implementation details ##  

The code is put into several modules:
1. `start.py` gets env variables, initiates connection to Mongo, and spawns a websocket consumer. Starts the application.
2. `handler.py` processes requests going to the `/data` endpoint to get data using pagination.
3. `service.py` incapsulates the logic of reading and writing to the DB.
4. `ws_background.py` listens to a websocket, and writes received data to Mongo in bulks.  

When the application starts, a background task `ws_background.py` is spawned. It uses a client session which is stored in the app to connect to a websocket. Websocket address is passed to the app via env variables and accessible as `app["websocket_addr"]`.  

The background consumer checks that each message is a valid json, sets the default country if it is missing, and prepares a bulk of messages (e.g. 1000) to insert into the DB. A bulk insert will not affect the DB as much as a simple insert.   
The last bulk of messages can be less then 1000 or in case of app shutting down, we need to insert these messages to the DB. If some of them are already in the DB, they will be replaced, to avoid the `duplicate key error`.  


There is an endpoint to request the stored data:  
```
/data?page_num=int&page_size=optional[int]
```   
`page_num` is a required parameter and if it's missing, 400 will be raised.  
`page_size` is an optional parameter. If it's not provided, the default value (50) will be used.  
Data will be returned in pages.  


## How to run ##  

1. Make sure you set addresses for subnet, websocket, and database in the `.env`:
    ```
    VEHICLE_SUBNET=10.0.10.0/24
    WEBSOCKET_ADDR=ws://vehicle-emulator:8080
    DATABASE_ADDR=mongodb://mongo-db:27017

    ```
2. Run docker compose
    ```
    docker-compose up -d
    ```
    This will build images and launch containers for:  
    - `Go`-service which sends data to websocket.  
    - MongoDB  
    - `ws-service` which listens to websocket and return data via API.  

 