## Sección 1 — Los tests de la IA

### 1. Clasificación de los 8 tests del código

| \# | Test | Clasificación | Por qué |
| :---- | :---- | :---- | :---- |
| 1 | test\_subtotal | Tautológico | El esperado es CATALOGO\["buzo"\] \* 2: usa la misma tabla del código, así que nunca lo compara con el precio de la spec. |
| 2 | test\_total\_funciona | Débil | assert resultado is not None: calcular\_total siempre devuelve un dict, así que solo falla si el código explota. |
| 3 | test\_total\_positivo | Débil | assert resultado\["total"\] \> 0: una campera vale \~\$48.000, así que casi cualquier cuenta da positiva. |
| 4 | test\_cupon\_egresados | Tautológico | El esperado 100000 \* 0.15 es la misma fórmula en float que usa el código, con un subtotal sin centavos y una fecha lejos del vencimiento. |
| 5 | test\_envio\_caba | Útil | Compara contra 2500, un valor fijo de la tabla de R8. Pero usa un solo caso, lejos del umbral de \$60.000. |
| 6 | test\_descuento\_por\_cantidad | Útil | Compara contra 10000, que sale de la spec. Pero prueba 6 prendas y el borde de R5 es 5\. |
| 7 | test\_talle\_valido | Inútil | No tiene assert: solo llama a validar\_item con un ítem perfecto. Un validar\_item vacío también pasaría. |
| 8 | test\_no\_explota\_con\_varios\_productos | Inútil | try: ... except Exception: pass se traga cualquier error, incluso un AssertionError. |

### 2. Mutation testing

python mutar.py \--tests test\_checkout\_ia.py

Mutantes generados : 29

Muertos            : 17

Sobrevivientes     : 12

Puntaje de mutación: 58.6%

Sobrevivientes (líneas de checkout.py):

línea  40  '\<' → '\<='              if not (1 \<= item\["cantidad"\] \< 10):

línea  40  10 → 11                 if not (1 \<= item\["cantidad"\] \< 10):

línea  60  '\>' → '\>='              if cantidad\_prendas \> 5:

línea  72  '\<' → '\<='              if not fecha \< datos\["vence"\]:

línea  76  '==' → '\!='             elif datos\["tipo"\] \== "fijo":

línea  77  '\<' → '\<='              if subtotal \< datos\["minimo"\]:

línea  82  '+' → '-'               descuento \+= datos\["valor"\]

línea  96  '\>=' → '\>'              if subtotal \>= 60000:

línea  96  60000 → 60001           if subtotal \>= 60000:

línea 107  '+' → '-'               prendas \= prendas \+ item\["cantidad"\]

línea 111  '+' → '-'               total \= subtotal \- descuento \+ envio

línea 111  '-' → '+'               total \= subtotal \- descuento \+ envio

La mitad de los sobrevivientes (6 de 12\) son **bordes** (\</\<=, \>/\>=, una constante \+ 1): la suite nunca prueba un valor límite. Y 3 están en el bloque del cupón BIENVENIDA (líneas 76-82), que ningún test ejecuta.

### 3\. ¿Por qué casi el 80% de cobertura no detectó ninguna falla?

La cobertura mide qué líneas **se ejecutaron**, no qué resultado **se verificó**. Una línea cuenta como cubierta aunque el test que pasa por ella tenga un is not None, un \> 0, ningún assert o un except: pass (así son 4 de los 8 tests), o un esperado calculado con la misma fórmula del código (otros 2). Además, casi todas las fallas de checkout.py están en líneas que sí se ejecutan (el \> 5, el \< vence, el round sobre float, el item\["talle"\] \= ...upper(), el item.get("precio", ...)), pero con valores que no las disparan: lejos de los bordes, en mayúscula, sin centavos y sin precio propio en el ítem. El 23% que falta es donde más fallas hay: ningún test recorre un camino de error (líneas 7-9, 38, 41, 50-51, 67, 73, 91), y ahí están el producto inexistente que se saltea en silencio, el except desnudo y el .join inventado. La mutación lo confirma: cuando se rompe a propósito una comparación o una cuenta, 12 de 29 veces ningún test se entera.