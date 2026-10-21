from datetime import date
from decimal import Decimal

import pytest

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
