import copy
from datetime import date
from decimal import Decimal

import pytest #type: ignore

import checkout
from checkout import (
    CheckoutError,
    calcular_descuento,
    calcular_envio,
    calcular_subtotal,
    calcular_total,
    validar_item,
)

HOY_VIGENTE = date(2026, 10, 1)


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def codigo_de_error(funcion, *args):
    with pytest.raises(CheckoutError) as error:
        funcion(*args)
    return error.value.code


def test_cantidad_cero_es_invalida():
    assert codigo_de_error(validar_item, item(cantidad=0)) == "CANTIDAD_INVALIDA"


def test_dos_buzos_a_caba_sin_cupon_dan_el_ejemplo_de_la_spec_en_decimal():
    # Arrange
    carrito = [item("buzo", "M", 2)]

    # Act
    resultado = calcular_total(carrito, "CABA", None, HOY_VIGENTE)

    # Assert
    assert resultado == {
        "subtotal": Decimal("49999.80"),
        "descuento": Decimal("0.00"),
        "envio": Decimal("2500.00"),
        "total": Decimal("52499.80"),
    }
    assert all(type(monto) is Decimal for monto in resultado.values())


def test_el_descuento_porcentual_redondea_el_medio_centavo_hacia_arriba():
    # Arrange
    subtotal = Decimal("11999.50")

    # Act
    descuento = calcular_descuento(subtotal, 1, "EGRESADOS2026", HOY_VIGENTE)

    # Assert
    assert descuento == Decimal("1799.93")


def test_el_precio_sale_del_catalogo_aunque_el_item_traiga_uno_propio():
    # Arrange
    carrito = [item("buzo", "M", 1, precio=1)]

    # Act
    subtotal = calcular_subtotal(carrito)

    # Assert
    assert subtotal == Decimal("24999.90")


def test_un_producto_inexistente_en_el_carrito_lanza_producto_inexistente():
    # Arrange
    carrito = [item("buzo", "M", 1), item("gorra", "M", 1)]

    # Act
    codigo = codigo_de_error(calcular_subtotal, carrito)

    # Assert
    assert codigo == "PRODUCTO_INEXISTENTE"


def test_un_talle_con_espacios_alrededor_es_valido():
    # Arrange
    carrito = [item("buzo", "  M ", 1)]

    # Act
    subtotal = calcular_subtotal(carrito)

    # Assert
    assert subtotal == Decimal("24999.90")


def test_validar_item_no_modifica_el_item_que_recibe():
    # Arrange
    un_item = item("buzo", "m", 1)
    copia = copy.deepcopy(un_item)

    # Act
    validar_item(un_item)

    # Assert
    assert un_item == copia


def test_calcular_total_no_modifica_el_carrito_que_recibe():
    # Arrange
    carrito = [item("buzo", "m", 1), item("remera", "s", 2)]
    copia = copy.deepcopy(carrito)

    # Act
    calcular_total(carrito, "CABA", None, HOY_VIGENTE)

    # Assert
    assert carrito == copia


@pytest.mark.parametrize("talle", [None, 42])
def test_un_talle_que_no_es_texto_lanza_talle_invalido(talle):
    # Arrange
    un_item = item("buzo", talle, 1)

    # Act
    codigo = codigo_de_error(validar_item, un_item)

    # Assert
    assert codigo == "TALLE_INVALIDO"


@pytest.mark.parametrize("cantidad, esperado", [(1, "11999.50"), (10, "119995.00")])
def test_las_cantidades_en_los_bordes_del_rango_son_validas(cantidad, esperado):
    # Arrange
    carrito = [item("remera", "M", cantidad)]

    # Act
    subtotal = calcular_subtotal(carrito)

    # Assert
    assert subtotal == Decimal(esperado)


@pytest.mark.parametrize("cantidad", [0, 11, -1, 2.5, 3.0, "3", True, None])
def test_una_cantidad_fuera_de_rango_o_no_entera_lanza_cantidad_invalida(cantidad):
    # Arrange
    un_item = item("buzo", "M", cantidad)

    # Act
    codigo = codigo_de_error(validar_item, un_item)

    # Assert
    assert codigo == "CANTIDAD_INVALIDA"


def test_calcular_total_con_el_carrito_vacio_lanza_carrito_vacio():
    # Arrange
    carrito = []

    # Act
    codigo = codigo_de_error(calcular_total, carrito, "CABA")

    # Assert
    assert codigo == "CARRITO_VACIO"


def test_calcular_subtotal_con_el_carrito_vacio_lanza_carrito_vacio():
    # Arrange
    carrito = []

    # Act
    codigo = codigo_de_error(calcular_subtotal, carrito)

    # Assert
    assert codigo == "CARRITO_VACIO"


@pytest.mark.parametrize("prendas, esperado", [(4, "0.00"), (5, "10000.00"), (6, "10000.00")])
def test_el_descuento_por_cantidad_es_del_10_por_ciento_desde_5_prendas(prendas, esperado):
    # Arrange
    subtotal = Decimal("100000.00")

    # Act
    descuento = calcular_descuento(subtotal, prendas, None, HOY_VIGENTE)

    # Assert
    assert descuento == Decimal(esperado)


def test_el_descuento_por_cantidad_suma_las_prendas_de_todos_los_items():
    # Arrange
    carrito = [item("buzo", "M", 3), item("remera", "M", 2)]

    # Act
    resultado = calcular_total(carrito, "CABA", None, HOY_VIGENTE)

    # Assert
    assert resultado["descuento"] == Decimal("9899.87")
    assert resultado["total"] == Decimal("89098.83")


def hacer_que_hoy_sea(monkeypatch, dia):
    class FechaFalsa(date):
        @classmethod
        def today(cls):
            return dia

    monkeypatch.setattr(checkout, "date", FechaFalsa)


# R1 - Catálogo y precios

@pytest.mark.parametrize("producto, precio", [
    ("buzo", "24999.90"), ("remera", "11999.50"), ("campera", "47999.99"),
])
def test_cada_producto_se_cobra_al_precio_del_catalogo(producto, precio):
    # Arrange
    carrito = [item(producto, "M", 1)]

    # Act
    subtotal = calcular_subtotal(carrito)

    # Assert
    assert subtotal == Decimal(precio)


def test_el_subtotal_suma_todos_los_items_del_carrito():
    # Arrange
    carrito = [item("buzo", "M", 1), item("remera", "S", 2), item("campera", "XL", 1)]

    # Act
    subtotal = calcular_subtotal(carrito)

    # Assert
    assert subtotal == Decimal("96998.89")


@pytest.mark.parametrize("producto", ["gorra", "Buzo", " buzo ", "", None])
def test_un_producto_que_no_esta_escrito_igual_que_en_el_catalogo_lanza_producto_inexistente(producto):
    # Arrange
    un_item = item(producto, "M", 1)

    # Act
    codigo = codigo_de_error(validar_item, un_item)

    # Assert
    assert codigo == "PRODUCTO_INEXISTENTE"


def test_una_clave_extra_en_el_item_se_ignora():
    # Arrange
    carrito = [item("remera", "M", 1, color="azul")]

    # Act
    subtotal = calcular_subtotal(carrito)

    # Assert
    assert subtotal == Decimal("11999.50")


# R2 - Talles

@pytest.mark.parametrize("talle", ["XS", "S", "M", "L", "XL", "XXL", "m", "Xl", " xxl "])
def test_un_talle_valido_sin_importar_mayusculas_ni_espacios_se_cobra(talle):
    # Arrange
    carrito = [item("remera", talle, 1)]

    # Act
    subtotal = calcular_subtotal(carrito)

    # Assert
    assert subtotal == Decimal("11999.50")


@pytest.mark.parametrize("talle", ["XXXL", "ZZ", "", "   ", "X L"])
def test_un_talle_que_no_es_de_la_lista_lanza_talle_invalido(talle):
    # Arrange
    un_item = item("buzo", talle, 1)

    # Act
    codigo = codigo_de_error(validar_item, un_item)

    # Assert
    assert codigo == "TALLE_INVALIDO"


# R4 - Carrito

def test_calcular_total_no_modifica_el_carrito_aunque_lance_un_error():
    # Arrange
    carrito = [item("buzo", "m", 1), item("gorra", "M", 1)]
    copia = copy.deepcopy(carrito)

    # Act
    codigo = codigo_de_error(calcular_total, carrito, "CABA")

    # Assert
    assert codigo == "PRODUCTO_INEXISTENTE"
    assert carrito == copia


# R6 - Cupones

@pytest.mark.parametrize("dia", [date(2026, 10, 1), date(2026, 11, 29), date(2026, 11, 30)])
def test_egresados2026_da_15_por_ciento_hasta_el_30_de_noviembre_inclusive(dia):
    # Arrange
    subtotal = Decimal("100000.00")

    # Act
    descuento = calcular_descuento(subtotal, 1, "EGRESADOS2026", dia)

    # Assert
    assert descuento == Decimal("15000.00")


@pytest.mark.parametrize("dia", [date(2026, 12, 1), date(2027, 3, 1)])
def test_egresados2026_despues_del_30_de_noviembre_lanza_cupon_vencido(dia):
    # Arrange
    subtotal = Decimal("100000.00")

    # Act
    codigo = codigo_de_error(calcular_descuento, subtotal, 1, "EGRESADOS2026", dia)

    # Assert
    assert codigo == "CUPON_VENCIDO"


@pytest.mark.parametrize("subtotal", ["20000.00", "20000.01", "50000.00"])
def test_bienvenida_descuenta_3000_desde_un_subtotal_de_20000(subtotal):
    # Arrange
    monto = Decimal(subtotal)

    # Act
    descuento = calcular_descuento(monto, 1, "BIENVENIDA", HOY_VIGENTE)

    # Assert
    assert descuento == Decimal("3000.00")


def test_bienvenida_con_un_subtotal_menor_a_20000_lanza_cupon_minimo_no_alcanzado():
    # Arrange
    subtotal = Decimal("19999.99")

    # Act
    codigo = codigo_de_error(calcular_descuento, subtotal, 1, "BIENVENIDA", HOY_VIGENTE)

    # Assert
    assert codigo == "CUPON_MINIMO_NO_ALCANZADO"


def test_bienvenida_no_vence():
    # Arrange
    subtotal = Decimal("50000.00")

    # Act
    descuento = calcular_descuento(subtotal, 1, "BIENVENIDA", date(2027, 3, 1))

    # Assert
    assert descuento == Decimal("3000.00")


@pytest.mark.parametrize("cupon, subtotal, esperado", [
    ("egresados2026", "100000.00", "15000.00"),
    ("  Bienvenida ", "50000.00", "3000.00"),
])
def test_el_cupon_no_distingue_mayusculas_ni_espacios(cupon, subtotal, esperado):
    # Arrange
    monto = Decimal(subtotal)

    # Act
    descuento = calcular_descuento(monto, 1, cupon, HOY_VIGENTE)

    # Assert
    assert descuento == Decimal(esperado)


@pytest.mark.parametrize("cupon", [None, "", "   "])
def test_un_cupon_vacio_equivale_a_no_usar_cupon(cupon):
    # Arrange
    subtotal = Decimal("100000.00")

    # Act
    descuento = calcular_descuento(subtotal, 1, cupon, HOY_VIGENTE)

    # Assert
    assert descuento == Decimal("0.00")


@pytest.mark.parametrize("cupon", ["NOEXISTE", "DEBUG100", "EGRESADOS2025", 123])
def test_un_cupon_que_no_existe_lanza_cupon_invalido(cupon):
    # Arrange
    subtotal = Decimal("100000.00")

    # Act
    codigo = codigo_de_error(calcular_descuento, subtotal, 1, cupon, HOY_VIGENTE)

    # Assert
    assert codigo == "CUPON_INVALIDO"


@pytest.mark.parametrize("subtotal, prendas, cupon, esperado", [
    ("100000.00", 6, "EGRESADOS2026", "15000.00"),
    ("100000.00", 5, "BIENVENIDA", "10000.00"),
    ("20000.00", 5, "BIENVENIDA", "3000.00"),
])
def test_el_cupon_no_se_acumula_con_el_descuento_por_cantidad_y_gana_el_mayor(subtotal, prendas, cupon, esperado):
    # Arrange
    monto = Decimal(subtotal)

    # Act
    descuento = calcular_descuento(monto, prendas, cupon, HOY_VIGENTE)

    # Assert
    assert descuento == Decimal(esperado)


def test_sin_fecha_el_cupon_usa_la_fecha_del_dia_de_la_llamada_vigente(monkeypatch):
    # Arrange
    hacer_que_hoy_sea(monkeypatch, date(2026, 11, 30))

    # Act
    descuento = calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026")

    # Assert
    assert descuento == Decimal("15000.00")


def test_sin_fecha_el_cupon_usa_la_fecha_del_dia_de_la_llamada_vencido(monkeypatch):
    # Arrange
    hacer_que_hoy_sea(monkeypatch, date(2026, 12, 1))

    # Act
    codigo = codigo_de_error(calcular_descuento, Decimal("100000.00"), 1, "EGRESADOS2026")

    # Assert
    assert codigo == "CUPON_VENCIDO"


def test_calcular_total_sin_fecha_usa_la_fecha_del_dia_de_la_llamada(monkeypatch):
    # Arrange
    hacer_que_hoy_sea(monkeypatch, date(2026, 12, 1))
    carrito = [item("remera", "M", 1)]

    # Act
    codigo = codigo_de_error(calcular_total, carrito, "CABA", "EGRESADOS2026")

    # Assert
    assert codigo == "CUPON_VENCIDO"


def test_fecha_none_explicita_equivale_a_no_mandar_fecha(monkeypatch):
    # Arrange
    hacer_que_hoy_sea(monkeypatch, date(2026, 10, 1))

    # Act
    descuento = calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", None)

    # Assert
    assert descuento == Decimal("15000.00")


# R7 - Dinero y redondeo

@pytest.mark.parametrize("subtotal, prendas, cupon, esperado", [
    ("24999.90", 1, "EGRESADOS2026", "3749.99"),
    ("20000.01", 1, "EGRESADOS2026", "3000.00"),
    ("239999.95", 5, None, "24000.00"),
    ("124999.50", 5, None, "12499.95"),
])
def test_los_descuentos_porcentuales_se_redondean_al_centavo(subtotal, prendas, cupon, esperado):
    # Arrange
    monto = Decimal(subtotal)

    # Act
    descuento = calcular_descuento(monto, prendas, cupon, HOY_VIGENTE)

    # Assert
    assert descuento == Decimal(esperado)


# R8 - Envío

@pytest.mark.parametrize("zona, costo", [
    ("CABA", "2500.00"), ("GBA", "4000.00"), ("INTERIOR", "6500.00"), ("RETIRO", "0.00"),
    ("caba", "2500.00"), ("  Interior ", "6500.00"),
])
def test_el_envio_cuesta_segun_la_zona_sin_importar_mayusculas_ni_espacios(zona, costo):
    # Arrange
    subtotal = Decimal("1000.00")

    # Act
    envio = calcular_envio(subtotal, zona)

    # Assert
    assert envio == Decimal(costo)
    assert type(envio) is Decimal


@pytest.mark.parametrize("subtotal, costo", [
    ("59999.99", "2500.00"), ("60000.00", "0.00"), ("60000.01", "0.00"),
])
def test_el_envio_es_gratis_desde_60000(subtotal, costo):
    # Arrange
    monto = Decimal(subtotal)

    # Act
    envio = calcular_envio(monto, "CABA")

    # Assert
    assert envio == Decimal(costo)


@pytest.mark.parametrize("zona, subtotal", [
    ("MARTE", "1000.00"), ("", "1000.00"), (None, "1000.00"), ("MARTE", "60000.00"),
])
def test_una_zona_que_no_existe_lanza_zona_invalida(zona, subtotal):
    # Arrange
    monto = Decimal(subtotal)

    # Act
    codigo = codigo_de_error(calcular_envio, monto, zona)

    # Assert
    assert codigo == "ZONA_INVALIDA"


def test_el_envio_gratis_se_decide_con_el_subtotal_ya_descontado():
    # Arrange
    carrito = [item("buzo", "M", 2), item("remera", "M", 1)]

    # Act
    resultado = calcular_total(carrito, "CABA", "EGRESADOS2026", HOY_VIGENTE)

    # Assert
    assert resultado["descuento"] == Decimal("9299.90")
    assert resultado["envio"] == Decimal("2500.00")
    assert resultado["total"] == Decimal("55199.40")


def test_el_envio_es_gratis_si_el_subtotal_descontado_sigue_arriba_de_60000():
    # Arrange
    carrito = [item("buzo", "M", 3)]

    # Act
    resultado = calcular_total(carrito, "GBA", "EGRESADOS2026", HOY_VIGENTE)

    # Assert
    assert resultado["descuento"] == Decimal("11249.96")
    assert resultado["envio"] == Decimal("0.00")
    assert resultado["total"] == Decimal("63749.74")


# R9 - Total

def test_el_total_resta_el_descuento_y_suma_el_envio():
    # Arrange
    carrito = [item("remera", "M", 1)]

    # Act
    resultado = calcular_total(carrito, "CABA", "EGRESADOS2026", HOY_VIGENTE)

    # Assert
    assert resultado == {
        "subtotal": Decimal("11999.50"),
        "descuento": Decimal("1799.93"),
        "envio": Decimal("2500.00"),
        "total": Decimal("12699.57"),
    }


def test_retirar_en_el_colegio_no_suma_envio_al_total():
    # Arrange
    carrito = [item("buzo", "M", 1)]

    # Act
    resultado = calcular_total(carrito, "RETIRO", None, HOY_VIGENTE)

    # Assert
    assert resultado["total"] == Decimal("24999.90")


def test_un_total_con_medio_centavo_en_el_descuento():
    # Arrange
    carrito = [item("campera", "M", 5)]

    # Act
    resultado = calcular_total(carrito, "CABA", None, HOY_VIGENTE)

    # Assert
    assert resultado == {
        "subtotal": Decimal("239999.95"),
        "descuento": Decimal("24000.00"),
        "envio": Decimal("0.00"),
        "total": Decimal("215999.95"),
    }


# Sección 3 - Orden de validación

@pytest.mark.parametrize("carrito, zona, cupon, fecha, esperado", [
    ([], "MARTE", "NOEXISTE", HOY_VIGENTE, "CARRITO_VACIO"),
    ([item("gorra", "ZZ", 0)], "CABA", None, HOY_VIGENTE, "PRODUCTO_INEXISTENTE"),
    ([item("buzo", "ZZ", 0)], "CABA", None, HOY_VIGENTE, "TALLE_INVALIDO"),
    ([item("buzo", "M", 0), item("gorra", "M", 1)], "CABA", None, HOY_VIGENTE, "CANTIDAD_INVALIDA"),
    ([item("buzo", "M", 11)], "MARTE", "NOEXISTE", HOY_VIGENTE, "CANTIDAD_INVALIDA"),
    ([item("buzo", "M", 1)], "MARTE", "NOEXISTE", HOY_VIGENTE, "CUPON_INVALIDO"),
    ([item("buzo", "M", 1)], "MARTE", "EGRESADOS2026", date(2026, 12, 1), "CUPON_VENCIDO"),
    ([item("remera", "M", 1)], "MARTE", "BIENVENIDA", HOY_VIGENTE, "CUPON_MINIMO_NO_ALCANZADO"),
    ([item("buzo", "M", 1)], "MARTE", None, HOY_VIGENTE, "ZONA_INVALIDA"),
])
def test_calcular_total_informa_el_primer_error_segun_el_orden_de_validacion(carrito, zona, cupon, fecha, esperado):
    # Arrange
    # (los datos vienen del parametrize: cada caso combina varios errores a propósito)

    # Act
    codigo = codigo_de_error(calcular_total, carrito, zona, cupon, fecha)

    # Assert
    assert codigo == esperado
