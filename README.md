# tp1-distribuidos
TP1 para la materia de Sistemas Distribuidos 1

Como probarlo:

```
make up
make logs
```

- POST_CHUNKS: `python3 client.py -c "CHANK A MANDAR"`

- GET_BLOCK: `python3 client.py -b HASH_A_PEDIR`

- GET_STATS: `python3 client.py -s `

- GET_BLOCKS: `python3 client.py -t DD/MM/YYYY, HH:MM:SS `

o por netcat:

nc <localhost> 5000
{"type": "tipo de request", "parameter": "parametro de ser necesario"}


Para pruebas de mas carga hay otro script `multiple_clients.py`:

- `python3 mutiple_clients.py --clients <number> --requests <number> --size <number>`

Para ambos scripts se le puede definir el puerto y la ip a la cual deben pegarle con las 
variables de entorno **PORT** y **HOST**

