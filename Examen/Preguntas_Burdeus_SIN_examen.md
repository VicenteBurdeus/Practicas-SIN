# Para el metodo A vamos a comprobar si este es admisible

```bash
python .\experiment.py .\data\10_puzzles.txt a_star_manhattan ---->  Solution Cost 20.80
python .\experiment.py .\data\10_puzzles.txt Metodo A ->  Solution Cost 20.80
```

Podemos ver que ambas soluciones son iguales por lo que piezas_descolocadas no parece sobreestimar los pasos.
Tras repasar rapidamente los CSV no e encontrado en ningun caso sobreestime

```bash
python .\experiment.py --save .\data\10_puzzles.txt Metodo A
```


Por lo tanto, podemos asumir que esta heurística es admisible. ya que da valores inferirores a la heuristica de manhattan la cual si es admisible

## ¿Cuál es su nivel de información con respecto a la heurística Manhattan Distance?


Para que esta devuelva mejores soluciones ha de estar más informada (predice mayor número de pasos sin sobreestimarlo, para heurísticas ≤ heurística).
Por lo tanto, comparamos Solution cost. Este es igual, ya lo hemos visto en la pregunta anterior.
Comparamos la cantidad de nodos generados ya que si está más informada necesitará generar menos nodos respecto a una menos informada.
En este caso tenemos:

```
manhattan : Nodes Generated 905.60 (mean)
Metodo_A : Nodes Generated 13387.0 (mean)
```

Aquí podemos ver una clara disonancia en la cantidad de nodos necesarios para encontrar una respuesta.
Por lo cual podemos asumir que A* Manhattan está más informada que el metodo A.

# Para el metodo B vamos a comprobar si este es admisible


```bash
python .\experiment.py .\data\10_puzzles.txt a_star_manhattan ->  Solution Cost 20.80
python .\experiment.py .\data\10_puzzles.txt Metodo_B -------->  Solution Cost 25.40
```

Esta heuristica si es admisible ya que es el Metodo_a/2 = Metodo_B (es la misma pero no multiplica por 2)
dado esto savemos que es una heuristica admisible y esta menos informada que Metodo_A y por lo tanto Manhattan

ademas iagual que la enterior podemos asumir que esta heurística es admisible. ya que da valores inferirores a la heuristica de manhattan la cual si es admisible


# Fuentes
```
============================================================
PERFORMANCE EVALUATION RESULTS
============================================================
Algorithm: Metodo_B
Total puzzles: 10
Solved puzzles: 10
Success rate: 100.0%

PERFORMANCE METRICS      MEAN        MEDIAN      MIN         MAX         STD DEV
-------------------------------------------------------------------------------------
Nodes Generated          912.80      646         390         2574        727.96
Nodes Expanded           309.50      226         122         856         242.91
Max Nodes Stored         565.20      404         236         1559        445.03
Solution Cost            25.40       25          20          30          3.53
Max Depth                27.00       26          22          35          4.55
Execution Time (s)       0.0104      0.0075      0.0040      0.0317      0.0089

Algorithm: Metodo_A
Total puzzles: 10

PERFORMANCE METRICS      MEAN         MEDIAN     MIN         MAX         STD DEV
-----------------------------------------------------------------------------------
Nodes Generated          13387.00    15314       1975        33868       9857.82
Nodes Expanded           4945.90     5646        722         12513       3646.17
Max Nodes Stored         7682.80     8860        1183        18975       5518.33
Solution Cost            20.80       22          16          24          2.35
Max Depth                20.80       22          16          24          2.35
Execution Time (s)       0.0522      0.0583      0.0075      0.1296      0.0382

Algorithm: a_star_manhattan
Total puzzles: 10

PERFORMANCE METRICS      MEAN        MEDIAN      MIN         MAX         STD DEV
-------------------------------------------------------------------------------------
Nodes Generated          905.60      732         149         2209        718.69
Nodes Expanded           332.80      269         56          805         263.08
Max Nodes Stored         538.50      442         94          1289        418.99
Solution Cost            20.80       22          16          24          2.35
Max Depth                20.80       22          16          24          2.35
Execution Time (s)       0.0119      0.0087      0.0010      0.0350      0.0112
```


