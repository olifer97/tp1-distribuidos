# tp1-distribuidos
TP1 para la materia de Sistemas Distribuidos 1

Como probarlo:

```
make docker-compose-up
make docker-compose-logs
```

- GET_CHUNKS: `client.py -c "CHANK A MANDAR"`

- GET_BLOCK: `client.py -b HASH_A_PEDIR`

- GET_STATS: `client.py -s `

- GET_BLOCKS: `client.py -t DD/MM/YYYY, HH:MM:SS `

o por netcat:

nc <localhost> 5000
{"type": "tipo de request", "parameter": "parametro de ser necesario"}
