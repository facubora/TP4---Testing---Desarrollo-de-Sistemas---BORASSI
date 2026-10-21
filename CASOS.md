## **CASOS \- TP4 \- TESTING** 

## **\# R1. Catálogo y precios** 

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Producto: buzo | — | calcular\_subtotal(\[item("buzo", "M", 1)\]) | Decimal("24999.90") | unitario |
| Producto: remera | — | calcular\_subtotal(\[item("remera", "M", 1)\]) | Decimal("11999.50") | unitario |
| Producto: campera | — | calcular\_subtotal(\[item("campera", "M", 1)\]) | Decimal("47999.99") | unitario |
| Varios productos distintos | — | calcular\_subtotal(\[item("buzo","M",1), item("remera","S",2), item("campera","XL",1)\]) | Decimal("96998.89") | unitario |
| El precio sale del catálogo: el ítem trae un precio menor | — | calcular\_subtotal(\[{"producto": "buzo", "talle": "M", "cantidad": 1, "precio": 1}\]) | Decimal("24999.90") | unitario |
| El precio sale del catálogo: el ítem trae un precio mayor | — | calcular\_subtotal(\[{"producto": "remera", "talle": "M", "cantidad": 2, "precio": 99999}\]) | Decimal("23999.00") | unitario |
| Otra clave cualquiera se ignora | — | validar\_item({"producto": "buzo", "talle": "M", "cantidad": 1, "color": "azul"}) | no lanza error | unitario |
| Producto que no está en el catálogo | — | validar\_item(item("gorra", "M", 1)) | PRODUCTO\_INEXISTENTE | unitario |
| Producto inexistente dentro de un carrito | — | calcular\_subtotal(\[item("buzo","M",1), item("gorra","M",1)\]) | PRODUCTO\_INEXISTENTE (no se saltea) | unitario |
| Nombre en mayúscula | — | validar\_item(item("Buzo", "M", 1)) | PRODUCTO\_INEXISTENTE | unitario |
| Nombre con espacios  | — | validar\_item(item(" buzo ", "M", 1)) | PRODUCTO\_INEXISTENTE | unitario |
| Nombre vacío | "" | validar\_item(item("", "M", 1)) | PRODUCTO\_INEXISTENTE | unitario |
| Producto que no es texto  | — | validar\_item(item(None, "M", 1)) | PRODUCTO\_INEXISTENTE | unitario |

## 

## **\# R2. Talles**

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Talle válido (Los 6 principales) | XS, S, M, L, XL, XXL | validar\_item(item("buzo", t, 1)) para cada t | no lanza error | unitario |
| Minúscula | — | validar\_item(item("buzo", "m", 1)) | no lanza error | unitario |
| Mezcla de mayúscula y minúscula | — | validar\_item(item("buzo", "Xl", 1)) | no lanza error | unitario |
| Espacios alrededor | — | validar\_item(item("buzo", "  M ", 1)) | no lanza error | unitario |
| Espacios y minúscula a la vez | — | validar\_item(item("buzo", " xxl ", 1)) | no lanza error | unitario |
| Talle que no existe (justo fuera de la lista) | XXXL | validar\_item(item("buzo", "XXXL", 1)) | TALLE\_INVALIDO | unitario |
| Talle que no existe | — | validar\_item(item("buzo", "FB", 1)) | TALLE\_INVALIDO | unitario |
| Vacío | "" | validar\_item(item("buzo", "", 1)) | TALLE\_INVALIDO | unitario |
| Solo espacios | "   " | validar\_item(item("buzo", "   ", 1)) | TALLE\_INVALIDO | unitario |
| Espacio en el medio | — | validar\_item(item("buzo", "X L", 1)) | TALLE\_INVALIDO | unitario |
| Talle que no es texto  | — | validar\_item(item("buzo", None, 1)) | TALLE\_INVALIDO | unitario |
| Talle numérico  | — | validar\_item(item("buzo", 42, 1)) | TALLE\_INVALIDO | unitario |

## 

## **\# R3. Cantidad**

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Entero en rango: borde inferior | 1 | validar\_item(item("buzo", "M", 1)) | no lanza error | unitario |
| Entero en rango: justo arriba del inferior | 2 | validar\_item(item("buzo", "M", 2)) | no lanza error | unitario |
| Entero en rango: justo debajo del superior | 9 | validar\_item(item("buzo", "M", 9)) | no lanza error | unitario |
| Entero en rango: borde superior (inclusive) | 10 | validar\_item(item("buzo", "M", 10)) | no lanza error | unitario |
| Cantidad 10 se cobra | 10 | calcular\_subtotal(\[item("remera", "M", 10)\]) | Decimal("119995.00") | unitario |
| Debajo del rango | 0 | validar\_item(item("buzo", "M", 0)) | CANTIDAD\_INVALIDA | unitario |
| Negativo | \-1 | validar\_item(item("buzo", "M", \-1)) | CANTIDAD\_INVALIDA | unitario |
| Arriba del rango | 11 | validar\_item(item("buzo", "M", 11)) | CANTIDAD\_INVALIDA | unitario |
| No entero (decimal) | 2.5 | validar\_item(item("buzo", "M", 2.5)) | CANTIDAD\_INVALIDA | unitario |
| Float con valor entero  | 3.0 | validar\_item(item("buzo", "M", 3.0)) | CANTIDAD\_INVALIDA | unitario |
| Texto con un número | "3" | validar\_item(item("buzo", "M", "3")) | CANTIDAD\_INVALIDA | unitario |
| Booleano | True | validar\_item(item("buzo", "M", True)) | CANTIDAD\_INVALIDA | unitario |
| Sin valor | None | validar\_item(item("buzo", "M", None)) | CANTIDAD\_INVALIDA | unitario |

## 

## **\# R4. Carrito**

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Carrito vacío | 0 ítems | calcular\_total(\[\], "CABA") | CARRITO\_VACIO | unitario |
| Carrito vacío en el subtotal | 0 ítems | calcular\_subtotal(\[\]) | CARRITO\_VACIO | unitario |
| Carrito con un ítem | 1 ítem | calcular\_total(\[item("buzo", "M", 1)\], "RETIRO")\["total"\] | Decimal("24999.90") | unitario |
| validar\_item no modifica el ítem | — | it \= item("buzo", " m ", 1), validar\_item(it) | it \== copia (sigue "m") | unitario |
| calcular\_subtotal no modifica el carrito | — | carrito con talle "xl" y clave "precio": 1; copia; calcular\_subtotal(carrito) | carrito \== copia | unitario |
| calcular\_total no modifica el carrito | — | carrito con talles " m " y "s"; copia; calcular\_total(carrito, "CABA") | carrito \== copia | unitario |
| Tampoco lo modifica cuando hay un error | — | carrito \[item("buzo", " m ", 1), item("gorra", "M", 1)\]; copia; calcular\_total | lanza PRODUCTO\_INEXISTENTE y carrito \== copia | unitario |

## 

## **\# R5. Descuento por cantidad**

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Menos de 5 prendas: sin descuento | 4 | calcular\_descuento(Decimal("100000.00"), 4, None, HOY) | Decimal("0.00") | unitario |
| 5 prendas: borde, con descuento | 5 | calcular\_descuento(Decimal("100000.00"), 5, None, HOY) | Decimal("10000.00") | unitario |
| Más de 5 prendas | 6 | calcular\_descuento(Decimal("100000.00"), 6, None, HOY) | Decimal("10000.00") | unitario |
| Una sola prenda | 1 | calcular\_descuento(Decimal("100000.00"), 1, None, HOY) | Decimal("0.00") | unitario |
| Se suman las cantidades de todos los ítems (llega a 5\) | 3 \+ 2 \= 5 | calcular\_total(\[item("buzo","M",3), item("remera","M",2)\], "CABA", None, HOY) | descuento Decimal("9899.87"), total Decimal("89098.83") | unitario |
| Se suman las cantidades de todos los ítems (no llega) | 2 \+ 2 \= 4 | calcular\_total(\[item("buzo","M",2), item("remera","M",2)\], "CABA", None, HOY) | descuento Decimal("0.00"), total Decimal("73998.80") | unitario |
| 5 ítems distintos de 1 prenda cada uno | 1 × 5 | calcular\_total(\[item("remera", t, 1\) for t in ("XS","S","M","L","XL")\], "CABA", None, HOY) | descuento Decimal(5999.75") | unitario |

## 

## **\# R6. Cupones**

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| EGRESADOS2026 vigente | 01/10/2026 | calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", date(2026, 10, 1)) | Decimal("15000.00") | unitario |
| EGRESADOS2026 el día anterior al vencimiento | 29/11/2026 | ídem con date(2026, 11, 29\) | Decimal("15000.00") | unitario |
| EGRESADOS2026 el último día (inclusive) | 30/11/2026 | ídem con date(2026, 11, 30\) | Decimal("15000.00") | unitario |
| EGRESADOS2026 vencido: el día siguiente | 01/12/2026 | ídem con date(2026, 12, 1\) | CUPON\_VENCIDO | unitario |
| EGRESADOS2026 vencido: mucho después | 2027 | ídem con date(2027, 3, 1\) | CUPON\_VENCIDO | unitario |
| BIENVENIDA en el mínimo exacto | 20.000,00 | calcular\_descuento(Decimal("20000.00"), 1, "BIENVENIDA", HOY) | Decimal("3000.00") | unitario |
| BIENVENIDA arriba del mínimo | 20.000,01 | calcular\_descuento(Decimal("20000.01"), 1, "BIENVENIDA", HOY) | Decimal(“3000.00") | unitario |
| BIENVENIDA debajo del mínimo | 19.999,99 | calcular\_descuento(Decimal("19999.99"), 1, "BIENVENIDA", HOY) | CUPON\_MINIMO\_NO\_ALCANZADO | unitario |
| BIENVENIDA no vence | 2027 | calcular\_descuento(Decimal("50000.00"), 1, "BIENVENIDA", date(2027, 3, 1)) | Decimal("3000.00") | unitario |
| Minúscula | — | calcular\_descuento(Decimal("100000.00"), 1, "egresados2026", HOY) | Decimal("15000.00") | unitario |
| Mezcla de mayúsculas y espacios | — | calcular\_descuento(Decimal("50000.00"), 1, "  Bienvenida ", HOY) | Decimal("3000.00") | unitario |
| Sin cupón: None | — | calcular\_descuento(Decimal("100000.00"), 1, None, HOY) | Decimal("0.00") | unitario |
| Sin cupón: vacío | "" | calcular\_descuento(Decimal("100000.00"), 1, "", HOY) | Decimal("0.00") (no es error) | unitario |
| Sin cupón: solo espacios | "   " | calcular\_descuento(Decimal("100000.00"), 1, "   ", HOY) | Decimal("0.00") (no es error) | unitario |
| Solo existen dos cupones: otro código | — | calcular\_descuento(Decimal("100000.00"), 1, "NOEXISTE", HOY) | CUPON\_INVALIDO | unitario |
| Solo existen dos cupones: código "de prueba" | — | calcular\_descuento(Decimal("100000.00"), 1, "DEBUG100", HOY) | CUPON\_INVALIDO | unitario |
| Código parecido | — | calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2025", HOY) | CUPON\_INVALIDO | unitario |
| Cupón que no es texto | — | calcular\_descuento(Decimal("100000.00"), 1, 123, HOY) | CUPON\_INVALIDO | unitario |
| No se acumula: gana el cupón (15% \> 10%) | 6 prendas | calcular\_descuento(Decimal("100000.00"), 6, "EGRESADOS2026", HOY) | Decimal("15000.00") (no 25.000) | unitario |
| No se acumula: gana el 10% (10.000 \> 3.000) | 5 prendas | calcular\_descuento(Decimal("100000.00"), 5, "BIENVENIDA", HOY) | Decimal("10000.00") (no 13.000) | unitario |
| No se acumula: gana el cupón fijo (3.000 \> 2.000) | 5 prendas | calcular\_descuento(Decimal("20000.00"), 5, "BIENVENIDA", HOY) | Decimal("3000.00") (no 5.000) | unitario |
| El descuento nunca supera el subtotal | caso más ajustado: BIENVENIDA en el mínimo | calcular\_descuento(Decimal("20000.00"), 1, "BIENVENIDA", HOY) | Decimal("3000.00"), que es ≤ Decimal("20000.00") | unitario |
| Sin fecha: usa la del día de la llamada (hoy vigente) | hoy \= 30/11/2026 | simular que hoy es 30/11/2026; calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026") | ("15000.00") | unitario |
| Sin fecha: usa la del día de la llamada (hoy vencido) | hoy \= 01/12/2026 | simular que hoy es 01/12/2026; misma llamada | CUPON\_VENCIDO | unitario |
| Sin fecha en calcular\_total | hoy \= 01/12/2026 | simular que hoy es 01/12/2026; calcular\_total(\[item("remera","M",1)\], "CABA", "EGRESADOS2026") | CUPON\_VENCIDO | unitario |
| fecha=None explícito equivale a no mandarla | hoy \= 01/10/2026 | simular que hoy es 01/10/2026; calcular\_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", None) | Decimal("15000.00") | unitario |

## 

## **\# R7. Dinero y redondeo**

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| El subtotal es Decimal y exacto | — | calcular\_subtotal(\[item("buzo", "M", 3)\]) | Decimal("74999.70"), de tipo Decimal | unitario |
| Todos los importes de calcular\_total son Decimal | — | calcular\_total(\[item("remera","M",1)\], "CABA", "EGRESADOS2026", HOY) | los 4 valores son Decimal | unitario |
| El envío es Decimal | — | calcular\_envio(Decimal("1000.00"), "GBA") | Decimal("4000.00"), de tipo Decimal | unitario |
| El descuento es Decimal | — | calcular\_descuento(Decimal("100000.00"), 5, None, HOY) | Decimal("10000.00"), de tipo Decimal | unitario |
| Medio centavo redondea hacia arriba (ejemplo de la spec) | ,925 | calcular\_descuento(Decimal("11999.50"), 1, "EGRESADOS2026", HOY) | Decimal("1799.93") | unitario |
| Medio centavo hacia arriba | ,985 | calcular\_descuento(Decimal("24999.90"), 1, "EGRESADOS2026", HOY) | Decimal("3749.99") | unitario |
| Medio centavo en el 10% por cantidad | ,995 | calcular\_descuento(Decimal("239999.95"), 5, None, HOY) | Decimal("24000.00") | unitario |
| Menos de medio centavo redondea hacia abajo | ,0015 | calcular\_descuento(Decimal("20000.01"), 1, "EGRESADOS2026", HOY) | Decimal("3000.00") | unitario |
| Sin redondeo necesario | exacto | calcular\_descuento(Decimal("124999.50"), 5, None, HOY) | Decimal("12499.95") | unitario |
| Total con medio centavo en el descuento | — | calcular\_total(\[item("campera", "M", 5)\], "CABA", None, HOY) | subtotal Decimal("239999.95"), descuento Decimal("24000.00"), envío Decimal("0.00"), total Decimal("215999.95") | unitario |

## 

## **\# R8. Envío**

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| CABA | — | calcular\_envio(Decimal("1000.00"), "CABA") | Decimal("2500.00") | unitario |
| GBA | — | calcular\_envio(Decimal("1000.00"), "GBA") | Decimal("4000.00") | unitario |
| INTERIOR | — | calcular\_envio(Decimal("1000.00"), "INTERIOR") | Decimal("6500.00") | unitario |
| RETIRO | — | calcular\_envio(Decimal("1000.00"), "RETIRO") | Decimal("0.00") | unitario |
| Zona en minúscula | — | calcular\_envio(Decimal("1000.00"), "caba") | Decimal("2500.00") | unitario |
| Zona con espacios y mezcla de mayúsculas | — | calcular\_envio(Decimal("1000.00"), "  Interior ") | Decimal("6500.00") | unitario |
| Envío pago: justo debajo del umbral | 59.999,99 | calcular\_envio(Decimal("59999.99"), "CABA") | Decimal("2500.00") | unitario |
| Envío gratis: en el umbral exacto | 60.000,00 | calcular\_envio(Decimal("60000.00"), "CABA") | Decimal("0.00") | unitario |
| Envío gratis: justo arriba del umbral | 60.000,01 | calcular\_envio(Decimal("60000.01"), "INTERIOR") | Decimal("0.00") | unitario |
| El umbral se mira con el descuento aplicado: el subtotal pasa 60.000 pero el neto no | subtotal 61.999,30 → neto 52.699,40 | calcular\_total(\[item("buzo","M",2), item("remera","M",1)\], "CABA", "EGRESADOS2026", HOY) | descuento Decimal("9299.90"), envío Decimal("2500.00"), total Decimal("55199.40") | unitario |
| Con el descuento aplicado el neto sigue arriba de 60.000 | neto 63.749,74 | calcular\_total(\[item("buzo","M",3)\], "GBA", "EGRESADOS2026", HOY) | descuento Decimal("11249.96"), envío Decimal("0.00"), total Decimal("63749.74") | unitario |
| Zona que no existe | — | calcular\_envio(Decimal("1000.00"), "MARTE") | ZONA\_INVALIDA | unitario |
| Zona vacía | "" | calcular\_envio(Decimal("1000.00"), "") | ZONA\_INVALIDA | unitario |
| Zona inválida aunque el envío sea gratis | 60.000 | calcular\_envio(Decimal("60000.00"), "MARTE") | ZONA\_INVALIDA | unitario |
| Zona que no es texto  | — | calcular\_envio(Decimal("1000.00"), None) | ZONA\_INVALIDA | unitario |

## R9 — Total

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Ejemplo completo de la spec (sección 5\) | — | calcular\_total(\[item("buzo", "M", 2)\], "CABA", None, HOY) | subtotal Decimal("49999.80"), descuento Decimal("0.00"), envío Decimal("2500.00"), total Decimal("52499.80") | unitario |
| Descuento y envío distintos de cero | — | calcular\_total(\[item("remera", "M", 1)\], "CABA", "EGRESADOS2026", HOY) | subtotal Decimal("11999.50"), descuento Decimal("1799.93"), envío Decimal("2500.00"), total Decimal("12699.57") | unitario |
| Sin envío | RETIRO | calcular\_total(\[item("buzo", "M", 1)\], "RETIRO", None, HOY) | total Decimal("24999.90") | unitario |
| Con descuento y sin envío | — | calcular\_total(\[item("buzo","M",3), item("remera","M",2)\], "INTERIOR", None, HOY) | total Decimal("89098.83") | unitario |
| El resultado tiene exactamente esas 4 claves | — | calcular\_total(\[item("buzo", "M", 1)\], "CABA", None, HOY) | claves {"subtotal", "descuento", "envio", "total"} | unitario |

## Orden de validación en calcular\_total (sección 3\)

Acá cada caso combina varios errores **a propósito**: lo que se prueba es cuál sale primero.

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| 1° carrito vacío, antes que cupón y zona | — | calcular\_total(\[\], "MARTE", "NOEXISTE", HOY) | CARRITO\_VACIO | unitario |
| 2° producto, antes que talle y cantidad | — | calcular\_total(\[item("gorra", "ZZ", 0)\], "CABA") | PRODUCTO\_INEXISTENTE | unitario |
| Talle antes que cantidad | — | calcular\_total(\[item("buzo", "ZZ", 0)\], "CABA") | TALLE\_INVALIDO | unitario |
| Los ítems en el orden en que aparecen | — | calcular\_total(\[item("buzo", "M", 0), item("gorra", "M", 1)\], "CABA") | CANTIDAD\_INVALIDA | unitario |
| Ítem antes que cupón y zona | — | calcular\_total(\[item("buzo", "M", 11)\], "MARTE", "NOEXISTE", HOY) | CANTIDAD\_INVALIDA | unitario |
| 3° cupón antes que zona | — | calcular\_total(\[item("buzo", "M", 1)\], "MARTE", "NOEXISTE", HOY) | CUPON\_INVALIDO | unitario |
| Cupón vencido antes que zona | — | calcular\_total(\[item("buzo", "M", 1)\], "MARTE", "EGRESADOS2026", date(2026, 12, 1)) | CUPON\_VENCIDO | unitario |
| Mínimo no alcanzado antes que zona | — | calcular\_total(\[item("remera", "M", 1)\], "MARTE", "BIENVENIDA", HOY) | CUPON\_MINIMO\_NO\_ALCANZADO | unitario |
| 4° zona, cuando todo lo demás está bien | — | calcular\_total(\[item("buzo", "M", 1)\], "MARTE", None, HOY) | ZONA\_INVALIDA | unitario |

---

## R10 — Persistencia (pedidos.py)

Cada caso usa una base nueva en un archivo temporal. "Otra conexión" \= abrir un segundo conectar(ruta) sobre el mismo archivo.

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| Los importes salen de calcular\_total | — | guardar\_pedido(con, "ana@mail.com", \[item("buzo", "M", 2)\], "CABA", None, HOY) y obtener\_pedido | subtotal Decimal("49999.80"), descuento Decimal("0.00"), envío Decimal("2500.00"), total Decimal("52499.80") | integración |
| CheckoutError en un ítem: se propaga y no queda nada | — | guardar\_pedido(con, "ana@mail.com", \[item("buzo", "ZZ", 1)\], "CABA") | lanza TALLE\_INVALIDO; otra conexión cuenta 0 pedidos y 0 ítems | integración |
| CheckoutError en la zona (después de validar los ítems) | — | guardar\_pedido(con, "ana@mail.com", \[item("buzo", "M", 1)\], "MARTE") | lanza ZONA\_INVALIDA; 0 pedidos y 0 ítems | integración |
| CheckoutError por cupón vencido | — | guardar\_pedido(con, "ana@mail.com", \[item("buzo", "M", 1)\], "CABA", "EGRESADOS2026", date(2026, 12, 1)) | lanza CUPON\_VENCIDO; 0 pedidos y 0 ítems | integración |
| Error con un pedido anterior ya guardado | 1 pedido previo | guardar uno válido y después uno con talle "ZZ" | se lanza el error y sigue habiendo 1 pedido y sus ítems | integración |
| Pedido definitivo: otra conexión lo ve completo | 1 ítem | guardar\_pedido(con, "ana@mail.com", \[item("remera", "M", 1)\], "CABA", None, HOY); obtener\_pedido(otra, id) | total Decimal("14499.50") y 1 ítem | integración |
| Pedido definitivo con varios ítems | 2 ítems | carrito \[item("buzo","M",1), item("remera","S",2)\]; leer desde otra conexión | 2 ítems, con cantidades 1 y 2 | integración |
| Pedido definitivo aunque se cierre la conexión que guardó | — | guardar, con.close(), leer desde otra conexión | el pedido está completo | integración |
| Montos idénticos, Decimal, sin pérdida | medio centavo | guardar\_pedido(con, "ana@mail.com", \[item("remera", "M", 1)\], "CABA", "EGRESADOS2026", date(2026, 11, 1)); obtener\_pedido | descuento \== Decimal("1799.93"), total \== Decimal("12699.57"), ambos de tipo Decimal | integración |
| Montos idénticos a lo que da checkout | — | comparar obtener\_pedido(...) con calcular\_total(...) para el mismo carrito | subtotal, descuento, envío y total iguales | integración |
| precio\_unitario del catálogo aunque el cliente mande otro | — | ítem {"producto": "remera", "talle": "M", "cantidad": 1, "precio": 1} | precio\_unitario \== Decimal("11999.50") y total Decimal("14499.50") | integración |
| Email normalizado | — | email "  Ana@Mail.COM " | se guarda "ana@mail.com" | integración |
| Zona normalizada | — | zona " caba " | se guarda "CABA" | integración |
| Talle normalizado | — | ítem con talle " m " | se guarda "M" | integración |
| Cupón normalizado | — | cupón " egresados2026 ", fecha HOY | se guarda "EGRESADOS2026" | integración |
| Cupón vacío se guarda como None | "" | cupón "" | cupon is None | integración |
| Cupón de solo espacios se guarda como None | "   " | cupón "   " | cupon is None | integración |
| Sin cupón | None | cupón None | cupon is None | integración |
| Id que no existe | — | obtener\_pedido(con, 999\) | None | integración |
| pedidos\_de no distingue mayúsculas ni espacios | — | 2 pedidos de "ana@mail.com"; pedidos\_de(con, "  ANA@Mail.com ") | devuelve esos 2 | integración |
| pedidos\_de del más reciente al más antiguo | 3 pedidos | guardar 3 pedidos de Ana (ids a, b, c, en ese orden) | ids en orden \[c, b, a\] | integración |
| pedidos\_de no trae pedidos de otro email | — | 1 de Ana y 1 de Beto; pedidos\_de(con, "ana@mail.com") | solo el de Ana | integración |
| pedidos\_de de un email sin pedidos | — | pedidos\_de(con, "nadie@mail.com") | \[\] | integración |
| El email no altera la consulta (inyección) | — | pedidos de Ana y de Beto; pedidos\_de(con, "x' OR '1'='1") | \[\] | integración |
| Email con comilla legítima | — | guardar con "o'brien@mail.com"; pedidos\_de(con, "o'brien@mail.com") | devuelve ese pedido, sin error | integración |

## R11 — API HTTP (api.py)

Servidor real con crear\_servidor(ruta\_temporal, 0\) y requests con urllib.

| Partición | Límites | Caso | Esperado | Nivel |
| :---- | :---- | :---- | :---- | :---- |
| POST válido con cupón y fecha | fecha 2026-11-30 (último día) | POST /api/v1/pedidos con remera M ×1, CABA, "cupon": "EGRESADOS2026", "fecha": "2026-11-30" | 201, {"id": \<entero\>, "subtotal": "11999.50", "descuento": "1799.93", "envio": "2500.00", "total": "12699.57"} | E2E |
| POST válido sin cupón ni fecha (opcionales) | — | POST con buzo M ×1, CABA | 201, subtotal "24999.90", descuento "0.00", envío "2500.00", total "27499.90" | E2E |
| Los montos viajan como texto | — | el mismo POST | los 4 montos son str en el JSON, no números | E2E |
| GET de un pedido creado: formato completo | — | POST y después GET /api/v1/pedidos/{id} | 200; email, zona, cupón, montos como texto e ítems con precio\_unitario "11999.50" | E2E |
| CheckoutError → 422 con su code | — | POST con talle "XXXL" | 422, {"error": {"code": "TALLE\_INVALIDO", "message": ...}} | E2E |
| CheckoutError por carrito vacío | — | POST con "carrito": \[\] | 422, CARRITO\_VACIO | E2E |
| CheckoutError por cupón vencido según la fecha enviada | 2026-12-01 | POST con "cupon": "EGRESADOS2026", "fecha": "2026-12-01" | 422, CUPON\_VENCIDO | E2E |
| El cuerpo no es JSON | — | POST con cuerpo crudo b"{no" | 400, JSON\_INVALIDO | E2E |
| Falta email | — | POST sin la clave email | 400, DATOS\_INCOMPLETOS | E2E |
| Falta zona | — | POST sin la clave zona | 400, DATOS\_INCOMPLETOS | E2E |
| Falta carrito | — | POST sin la clave carrito | 400, DATOS\_INCOMPLETOS | E2E |
| Carrito de otro tipo | — | POST con "carrito": "buzo" | 400, DATOS\_INCOMPLETOS | E2E |
| Email o zona de otro tipo | — | POST con "email": 123 / "zona": 5 | 400, DATOS\_INCOMPLETOS | E2E |
| El cuerpo es JSON pero no un objeto | — | POST con \[\] | 400, DATOS\_INCOMPLETOS | E2E |
| Fecha con otro formato | — | POST con "fecha": "30/11/2026" | 400, FECHA\_INVALIDA | E2E |
| Fecha que no es fecha | — | POST con "fecha": "mañana" | 400, FECHA\_INVALIDA | E2E |
| Pedido inexistente | — | GET /api/v1/pedidos/999 | 404, PEDIDO\_INEXISTENTE | E2E |
| Ruta inexistente (GET) | — | GET /api/v1/otra | 404, RUTA\_INEXISTENTE | E2E |
| Ruta inexistente (POST) | — | POST /api/v1/otra | 404, RUTA\_INEXISTENTE | E2E |
| Un error nunca devuelve 500 y siempre usa el mismo formato | — | todos los casos de error de arriba | status ≠ 500 y cuerpo {"error": {"code": str, "message": str}} | E2E |

