# HoMM3 vcmi server
## REQUIREMENTS
1. At least 4gb memory for building server
2. Game data from HoMM3 game

## INSTRUCTIONS
1. Build Dockerfile
```bash
docker build -t vcmi .
```
2. Put data to __gamedata__ dir
3. Up service via:
```bash
docker-compose up -d
```
4. Now you can connect to vcmi server via multiplayer join
* run client
```bash
vcmiclient
```
* new game
* multiplayer
* join 
* Player 1 @ 127.0.0.1:3030
* ok, begin, ok, ok

<img src='connect.gif'/>
