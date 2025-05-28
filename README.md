# Proyecto3_puzzle-


Steps to create a virtual machine; Irvings para crear un entorno virtual de python
```
    python -m venv venv
```

Activar el entorno 

    - Windows:
```
    ./venv/Scripts/activate
```
    - Linux:
    source venv/bin/activate

Instalar las librerias del archivo de texto
```
    pip install -r requirements.txt
```

Correr el server 
```
    python main.py
```

Conseguir todos los nodos creados en Neo4J
```
    http://127.0.0.1:5000/nodes
```