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

## Sección 2 — Hallazgos

### 1. Linter

```bash
ruff check checkout.py
```

```
checkout.py:1:8:   F401 `json` imported but unused
checkout.py:50:9:  E722 Do not use bare `except`
checkout.py:57:70: B008 Do not perform function call `date.today` in argument defaults
checkout.py:63:17: E711 Comparison to `None` should be `cond is not None`
checkout.py:102:53: B008 Do not perform function call `date.today` in argument defaults
Found 5 errors.
```

`ruff check pedidos.py api.py` da `All checks passed!`, aunque ahí están la
inyección SQL y los pedidos que se pierden. El linter solo ve la **forma** del
código, no si cumple la spec.

### 2. Fallas

Cada falla se confirmó ejecutando el código original. Los números de línea son
los de los archivos originales.

#### `checkout.py`

**C-01 · Los importes son `float`, no `Decimal`**
- **Archivo y línea:** `checkout.py`, líneas 13-15, 22, 27-30, 45, 58, 61, 74, 97-99
- **Categoría:** numéricos
- **Regla:** R7 ("Todos los importes se manejan como `Decimal`. Nunca `float`")
- **Cómo la encontré:** lectura del código y prueba en la terminal
- **Severidad:** alta: todos los montos de todas las compras arrastran error de `float`.

**C-02 · El redondeo no es comercial**
- **Archivo y línea:** `checkout.py`, líneas 54, 84, 117
- **Categoría:** numéricos
- **Regla:** R7 (redondeo comercial, ejemplo de la spec)
- **Cómo la encontré:** caso de `CASOS.md` (R7, ejemplo de la spec) y prueba en la terminal
- **Severidad:** alta: el ejemplo oficial de la spec da mal.

**C-03 · Se usa el precio que manda el cliente**
- **Archivo y línea:** `checkout.py`, línea 49
- **Categoría:** seguridad
- **Regla:** R1 ("El precio sale siempre del catálogo")
- **Cómo la encontré:** lectura del código (`item.get("precio", ...)`) y prueba en la terminal
- **Severidad:** alta: cualquiera puede ponerle el precio que quiera a su compra.

**C-04 · Un producto inexistente se saltea en silencio**
- **Archivo y línea:** `checkout.py`, líneas 48-51
- **Categoría:** manejo de errores
- **Regla:** R1 ("Un producto que no está en el catálogo → `PRODUCTO_INEXISTENTE`")
- **Cómo la encontré:** linter (E722) y prueba en la terminal
- **Severidad:** alta: un pedido con un producto mal escrito se cobra incompleto.

**C-05 · `validar_item` no valida el producto ni respeta el orden de validación**
- **Archivo y línea:** `checkout.py`, líneas 34-41
- **Categoría:** lógica y límites
- **Regla:** R1 y sección 3 (orden: producto, talle, cantidad)
- **Cómo la encontré:** caso de `CASOS.md` (orden de validación) y prueba en la terminal
- **Severidad:** media: se informa un error equivocado.

**C-06 · `validar_item` modifica el ítem que recibe**
- **Archivo y línea:** `checkout.py`, línea 35
- **Categoría:** efectos laterales
- **Regla:** R4 ("Ninguna función modifica el carrito que recibe")
- **Cómo la encontré:** lectura del código (`item["talle"] = ...`) y prueba en la terminal
- **Severidad:** media: el frontend encuentra el carrito cambiado.

**C-07 · No se sacan los espacios del talle**
- **Archivo y línea:** `checkout.py`, línea 35
- **Categoría:** strings
- **Regla:** R2 ("Se ignoran los espacios al principio y al final")
- **Cómo la encontré:** caso de `CASOS.md` (R2) y prueba en la terminal
- **Severidad:** media: se rechaza una compra válida.

**C-08 · Un talle que no es texto rompe con `AttributeError`**
- **Archivo y línea:** `checkout.py`, línea 35
- **Categoría:** tipos
- **Regla:** R2 y sección 1 ("Nunca otro tipo de excepción")
- **Cómo la encontré:** caso de `CASOS.md` (R2, tipo raro) y prueba en la terminal
- **Severidad:** media: un dato malo termina en un error no controlado.

**C-09 · La cantidad 10 se rechaza**
- **Archivo y línea:** `checkout.py`, línea 40
- **Categoría:** lógica y límites
- **Regla:** R3 ("entre 1 y 10, ambos inclusive")
- **Cómo la encontré:** caso de `CASOS.md` (R3, límite 10) y mutación (sobrevive `<` → `<=`)
- **Severidad:** alta: no se pueden comprar 10 prendas, que la spec permite.

**C-10 · No controla que la cantidad sea un entero**
- **Archivo y línea:** `checkout.py`, línea 40
- **Categoría:** tipos
- **Regla:** R3 ("Cualquier otro valor, incluidos los no enteros → `CANTIDAD_INVALIDA`")
- **Cómo la encontré:** caso de `CASOS.md` (R3) y prueba en la terminal
- **Severidad:** alta: se cobran fracciones de prenda.

**C-11 · El carrito vacío no da error**
- **Archivo y línea:** `checkout.py`, líneas 44-54 y 102-103
- **Categoría:** lógica y límites
- **Regla:** R4 ("Debe tener al menos un ítem → si no, `CARRITO_VACIO`")
- **Cómo la encontré:** caso de `CASOS.md` (R4) y prueba en la terminal
- **Severidad:** media: se puede generar un pedido vacío que cobra envío.

**C-12 · La fecha "de hoy" se calcula una sola vez, al importar**
- **Archivo y línea:** `checkout.py`, líneas 57 y 102
- **Categoría:** fechas
- **Regla:** R6 ("se usa la fecha del día en que se hace la llamada")
- **Cómo la encontré:** linter (B008) y lectura del código
- **Severidad:** alta: el cupón no vence nunca mientras el servidor no se reinicie.

**C-13 · `fecha=None` explícito rompe con `TypeError`**
- **Archivo y línea:** `checkout.py`, línea 72
- **Categoría:** fechas
- **Regla:** R6 y sección 1 (la firma acepta `fecha: date | None = None`)
- **Cómo la encontré:** lectura de la firma de la spec y prueba en la terminal
- **Severidad:** alta: `pedidos.py` siempre manda `None` (ver P-06).

**C-14 · Con 5 prendas no hay descuento**
- **Archivo y línea:** `checkout.py`, línea 60
- **Categoría:** lógica y límites
- **Regla:** R5 ("5 o más")
- **Cómo la encontré:** caso de `CASOS.md` (R5, límite 5) y mutación (sobrevive `>` → `>=`)
- **Severidad:** alta: se cobra de más en un caso común.

**C-15 · El cupón vacío o con espacios da error**
- **Archivo y línea:** `checkout.py`, líneas 63-67
- **Categoría:** strings
- **Regla:** R6 ("`None`, `""` o un texto de solo espacios equivalen a no usar cupón. No es un error")
- **Cómo la encontré:** caso de `CASOS.md` (R6) y prueba en la terminal
- **Severidad:** media: el frontend manda `""` cuando el campo queda vacío y la compra se rechaza.

**C-16 · El cupón distingue mayúsculas**
- **Archivo y línea:** `checkout.py`, línea 64
- **Categoría:** strings
- **Regla:** R6 ("No se distingue mayúscula de minúscula")
- **Cómo la encontré:** caso de `CASOS.md` (R6) y prueba en la terminal
- **Severidad:** media: se rechaza un cupón válido.

**C-17 · Hay un cupón oculto del 100%**
- **Archivo y línea:** `checkout.py`, línea 23
- **Categoría:** seguridad
- **Regla:** R6 ("Estos son los únicos dos cupones que existen")
- **Cómo la encontré:** lectura del código
- **Severidad:** alta: cualquiera que lo conozca se lleva todo gratis.

**C-18 · `EGRESADOS2026` ya está vencido el 30/11**
- **Archivo y línea:** `checkout.py`, línea 72
- **Categoría:** lógica y límites
- **Regla:** R6 ("Válido hasta el 30/11/2026 inclusive")
- **Cómo la encontré:** caso de `CASOS.md` (R6, último día) y mutación (sobrevive `<` → `<=`)
- **Severidad:** alta: el último día del cupón, el de más compras, se rechaza.

**C-19 · El cupón se suma al descuento por cantidad**
- **Archivo y línea:** `checkout.py`, líneas 60-82
- **Categoría:** lógica y límites
- **Regla:** R6 ("no se acumula con el descuento por cantidad. Se calculan los dos y se aplica el mayor")
- **Cómo la encontré:** caso de `CASOS.md` (R6) y prueba en la terminal
- **Severidad:** alta: se descuenta de más en todas las compras grandes con cupón.

**C-20 · El descuento puede superar el subtotal**
- **Archivo y línea:** `checkout.py`, línea 84
- **Categoría:** lógica y límites
- **Regla:** R6 ("El descuento nunca puede superar el subtotal")
- **Cómo la encontré:** lectura del código y prueba en la terminal
- **Severidad:** baja: solo pasa combinado con C-17; con los dos cupones reales no se alcanza.

**C-21 · Un cupón que no es texto rompe con `AttributeError`**
- **Archivo y línea:** `checkout.py`, línea 64
- **Categoría:** tipos
- **Regla:** R6 y sección 1 ("Nunca otro tipo de excepción")
- **Cómo la encontré:** caso de `CASOS.md` (R6, tipo raro) y prueba en la terminal
- **Severidad:** baja: el frontend manda texto.

**C-22 · Una zona inválida rompe con un método que no existe**
- **Archivo y línea:** `checkout.py`, línea 93
- **Categoría:** alucinación
- **Regla:** R8 ("Zona que no existe → `ZONA_INVALIDA`")
- **Cómo la encontré:** caso de `CASOS.md` (R8) y prueba en la terminal
- **Severidad:** alta: ningún error de zona se informa bien.

**C-23 · El envío gratis se calcula sobre el subtotal sin descuento**
- **Archivo y línea:** `checkout.py`, línea 110
- **Categoría:** lógica y límites
- **Regla:** R8 ("si el subtotal ya con el descuento aplicado es de $60.000 o más")
- **Cómo la encontré:** caso de `CASOS.md` (R8, umbral con descuento) y prueba en la terminal
- **Severidad:** alta: se regala el envío cuando no corresponde.

**C-24 · Una zona que no es texto rompe con `AttributeError`**
- **Archivo y línea:** `checkout.py`, línea 88
- **Categoría:** tipos
- **Regla:** R8 y sección 1 ("Nunca otro tipo de excepción")
- **Cómo la encontré:** caso de `CASOS.md` (R8, tipo raro) y prueba en la terminal
- **Severidad:** baja: el frontend manda texto.

**C-25 · Import sin usar y comparación con `!= None`**
- **Archivo y línea:** `checkout.py`, líneas 1 y 63
- **Categoría:** code smell
- **Regla:** —
- **Cómo la encontré:** linter (F401, E711)
- **Severidad:** baja: no rompe nada hoy.

#### `pedidos.py`

**P-01 · Si `checkout` lanza error, queda un pedido fantasma**
- **Archivo y línea:** `pedidos.py`, líneas 39-50
- **Categoría:** efectos laterales
- **Regla:** R10 ("Si eso lanza `CheckoutError` [...] no queda nada guardado")
- **Cómo la encontré:** caso de `CASOS.md` (R10) y prueba con una segunda conexión
- **Severidad:** alta: cada compra rechazada deja basura en la base.

**P-02 · Los importes y los ítems nunca se commitean**
- **Archivo y línea:** `pedidos.py`, líneas 52-71
- **Categoría:** efectos laterales
- **Regla:** R10 ("Cuando `guardar_pedido` termina, el pedido es definitivo: cualquier otra conexión [...] lo ve completo")
- **Cómo la encontré:** caso de `CASOS.md` (R10, otra conexión) y prueba en la terminal y por HTTP
- **Severidad:** alta: se pierden todos los pedidos.

**P-03 · Los montos pierden precisión al guardarse**
- **Archivo y línea:** `pedidos.py`, líneas 12-15, 23, 55-58, 68, 88-91, 97
- **Categoría:** numéricos
- **Regla:** R10 ("Los montos que devuelve `obtener_pedido` son idénticos [...] sin ninguna pérdida") y R7
- **Cómo la encontré:** lectura del código y prueba en la terminal
- **Severidad:** alta: los montos guardados no son los cobrados.

**P-04 · `precio_unitario` sale del precio que manda el cliente**
- **Archivo y línea:** `pedidos.py`, línea 64
- **Categoría:** seguridad
- **Regla:** R10 ("`precio_unitario` es el precio del catálogo, nunca uno enviado por el cliente")
- **Cómo la encontré:** caso de `CASOS.md` (R10) y prueba en la terminal
- **Severidad:** alta: el registro del pedido queda con un precio falso.

**P-05 · Inyección SQL en `pedidos_de`**
- **Archivo y línea:** `pedidos.py`, líneas 106-108
- **Categoría:** seguridad
- **Regla:** R10 ("ningún valor puede alterar la consulta a la base")
- **Cómo la encontré:** lectura del código (la única consulta sin `?`) y prueba en la terminal
- **Severidad:** alta: expone los datos de todos los compradores.

**P-06 · Le pasa `fecha=None` a `calcular_total`**
- **Archivo y línea:** `pedidos.py`, línea 50
- **Categoría:** fechas
- **Regla:** R10 y R6 (sin fecha se usa la del día)
- **Cómo la encontré:** prueba en la terminal
- **Severidad:** alta: el cupón principal no funciona en el sistema.

#### `api.py`

**A-01 · Todo error devuelve 500 con otro formato**
- **Archivo y línea:** `api.py`, líneas 53-54 y 67-68
- **Categoría:** manejo de errores
- **Regla:** R11 (tabla de errores; "Un error nunca puede devolver 500")
- **Cómo la encontré:** caso de `CASOS.md` (R11) y prueba por HTTP
- **Severidad:** alta: el frontend no puede saber qué falló.

**A-02 · Los montos viajan como número JSON**
- **Archivo y línea:** `api.py`, línea 18
- **Categoría:** numéricos
- **Regla:** R11 ("Los montos viajan siempre como texto")
- **Cómo la encontré:** caso de `CASOS.md` (R11) y prueba por HTTP
- **Severidad:** alta: el frontend lee los montos como `float`.

**A-03 · La fecha no se convierte ni se valida**
- **Archivo y línea:** `api.py`, línea 41
- **Categoría:** tipos
- **Regla:** R11 ("La fecha viaja como texto en formato `AAAA-MM-DD`"; fecha mal formada → `400 FECHA_INVALIDA`)
- **Cómo la encontré:** caso de `CASOS.md` (R11) y prueba por HTTP
- **Severidad:** alta: no se puede comprar con cupón mandando la fecha.

**A-04 · JSON inválido devuelve 500**
- **Archivo y línea:** `api.py`, líneas 31-32
- **Categoría:** manejo de errores
- **Regla:** R11 ("El cuerpo no es JSON válido → 400 `JSON_INVALIDO`")
- **Cómo la encontré:** caso de `CASOS.md` (R11) y prueba por HTTP
- **Severidad:** media: se informa mal un error del cliente.

**A-05 · No valida que estén email, zona y carrito ni sus tipos**
- **Archivo y línea:** `api.py`, líneas 36-40
- **Categoría:** tipos
- **Regla:** R11 ("Falta email, zona o carrito, o tienen otro tipo → 400 `DATOS_INCOMPLETOS`")
- **Cómo la encontré:** caso de `CASOS.md` (R11) y prueba por HTTP
- **Severidad:** media: se informa mal un error del cliente.

**A-06 · Un pedido inexistente devuelve 200**
- **Archivo y línea:** `api.py`, líneas 64-66
- **Categoría:** manejo de errores
- **Regla:** R11 ("El pedido no existe → 404 `PEDIDO_INEXISTENTE`")
- **Cómo la encontré:** caso de `CASOS.md` (R11) y prueba por HTTP
- **Severidad:** media: el frontend recibe "éxito" sin datos.

**A-07 · Un id gigante devuelve 500**
- **Archivo y línea:** `api.py`, línea 64
- **Categoría:** tipos
- **Regla:** R11 ("Un error nunca puede devolver 500")
- **Cómo la encontré:** prueba por HTTP
- **Severidad:** baja: hay que escribir la URL a mano.

**A-08 · La conexión a la base no se cierra si hay error**
- **Archivo y línea:** `api.py`, líneas 34-44 y 63-65
- **Categoría:** code smell
- **Regla:** —
- **Cómo la encontré:** lectura del código
- **Severidad:** baja: no rompe una compra, pero acumula conexiones abiertas.

### 3. Tabla de fallas, de la más grave a la menos grave

| # | Falla | Archivo y línea | Categoría | Regla | Severidad |
|---|---|---|---|---|---|
| P-02 | Importes e ítems nunca se commitean: los pedidos se pierden | `pedidos.py` 52-71 | efectos laterales | R10 | alta |
| P-05 | Inyección SQL en `pedidos_de` | `pedidos.py` 106-108 | seguridad | R10 | alta |
| C-03 | Se usa el precio que manda el cliente | `checkout.py` 49 | seguridad | R1 | alta |
| C-17 | Cupón oculto `DEBUG100` del 100% | `checkout.py` 23 | seguridad | R6 | alta |
| P-04 | `precio_unitario` sale del cliente | `pedidos.py` 64 | seguridad | R10 | alta |
| P-01 | Pedido fantasma cuando `checkout` lanza error | `pedidos.py` 39-50 | efectos laterales | R10 | alta |
| C-01 | Importes en `float`, no `Decimal` | `checkout.py` 13-15, 22, 27-30, ... | numéricos | R7 | alta |
| C-02 | Redondeo no comercial (1799.92 en vez de 1799.93) | `checkout.py` 54, 84, 117 | numéricos | R7 | alta |
| P-03 | Los montos pierden precisión al guardarse | `pedidos.py` 12-15, 55-58, 88-91, ... | numéricos | R10, R7 | alta |
| A-02 | Montos como número JSON | `api.py` 18 | numéricos | R11 | alta |
| A-01 | Todo error devuelve 500 con otro formato | `api.py` 53-54, 67-68 | manejo de errores | R11 | alta |
| C-04 | Producto inexistente se saltea en silencio | `checkout.py` 48-51 | manejo de errores | R1 | alta |
| C-19 | Cupón y descuento por cantidad se suman | `checkout.py` 60-82 | lógica y límites | R6 | alta |
| C-23 | Envío gratis sobre el subtotal sin descuento | `checkout.py` 110 | lógica y límites | R8 | alta |
| C-12 | Fecha "de hoy" fijada al importar | `checkout.py` 57, 102 | fechas | R6 | alta |
| C-13 | `fecha=None` rompe con `TypeError` | `checkout.py` 72 | fechas | R6 | alta |
| P-06 | `pedidos.py` le pasa `fecha=None` a `checkout` | `pedidos.py` 50 | fechas | R10, R6 | alta |
| A-03 | La fecha no se convierte ni se valida | `api.py` 41 | tipos | R11 | alta |
| C-22 | `ENVIOS.keys().join` no existe | `checkout.py` 93 | alucinación | R8 | alta |
| C-09 | La cantidad 10 se rechaza | `checkout.py` 40 | lógica y límites | R3 | alta |
| C-10 | No controla que la cantidad sea entero | `checkout.py` 40 | tipos | R3 | alta |
| C-14 | Con 5 prendas no hay descuento | `checkout.py` 60 | lógica y límites | R5 | alta |
| C-18 | `EGRESADOS2026` vencido el 30/11 | `checkout.py` 72 | lógica y límites | R6 | alta |
| C-05 | No valida el producto ni el orden de validación | `checkout.py` 34-41 | lógica y límites | R1, §3 | media |
| C-06 | `validar_item` modifica el ítem | `checkout.py` 35 | efectos laterales | R4 | media |
| C-07 | No saca los espacios del talle | `checkout.py` 35 | strings | R2 | media |
| C-08 | Talle no texto → `AttributeError` | `checkout.py` 35 | tipos | R2 | media |
| C-11 | Carrito vacío no da error | `checkout.py` 44-54, 102-103 | lógica y límites | R4 | media |
| C-15 | Cupón vacío o con espacios da error | `checkout.py` 63-67 | strings | R6 | media |
| C-16 | El cupón distingue mayúsculas | `checkout.py` 64 | strings | R6 | media |
| A-04 | JSON inválido devuelve 500 | `api.py` 31-32 | manejo de errores | R11 | media |
| A-05 | No valida email, zona y carrito | `api.py` 36-40 | tipos | R11 | media |
| A-06 | Pedido inexistente devuelve 200 | `api.py` 64-66 | manejo de errores | R11 | media |
| C-20 | El descuento puede superar el subtotal | `checkout.py` 84 | lógica y límites | R6 | baja |
| C-21 | Cupón no texto → `AttributeError` | `checkout.py` 64 | tipos | R6 | baja |
| C-24 | Zona no texto → `AttributeError` | `checkout.py` 88 | tipos | R8 | baja |
| A-07 | Id gigante devuelve 500 | `api.py` 64 | tipos | R11 | baja |
| C-25 | Import sin usar y `!= None` | `checkout.py` 1, 63 | code smell | — | baja |
| A-08 | La conexión no se cierra si hay error | `api.py` 34-44, 63-65 | code smell | — | baja |

**Total: 39 fallas** (25 en `checkout.py`, 6 en `pedidos.py`, 8 en `api.py`): 23 altas, 10 medias y 6 bajas.

**Qué detectó el linter por sí solo:** C-04 (E722), C-12 (B008) y C-25 (F401, E711). Es decir, 3 de 39; en `pedidos.py` y `api.py`, ninguna.
