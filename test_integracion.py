from datetime import date
from decimal import Decimal

import pytest #type: ignore

import pedidos
from checkout import CheckoutError, calcular_total

HOY_VIGENTE = date(2026, 10, 1)


@pytest.fixture
def ruta(tmp_path):
    return str(tmp_path / "tienda.db")


@pytest.fixture
def con(ruta):
    conexion = pedidos.conectar(ruta)
    pedidos.crear_esquema(conexion)
    yield conexion
    conexion.close()


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def contar(ruta, tabla):
    assert tabla in ("pedidos", "items")
    otra = pedidos.conectar(ruta)
    try:
        return otra.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        otra.close()


def test_un_id_inexistente_devuelve_none(con):
    assert pedidos.obtener_pedido(con, 999) is None


def guardar(con, carrito, email="ana@mail.com", zona="CABA", cupon=None, fecha=HOY_VIGENTE):
    return pedidos.guardar_pedido(con, email, carrito, zona, cupon, fecha)


def leer_desde_otra_conexion(ruta, pedido_id):
    otra = pedidos.conectar(ruta)
    try:
        return pedidos.obtener_pedido(otra, pedido_id)
    finally:
        otra.close()


# R10 · guardar_pedido calcula los importes con calcular_total

def test_guardar_pedido_calcula_los_importes_con_checkout(con):
    # Arrange
    carrito = [item("remera", "M", 1)]

    # Act
    pedido_id = guardar(con, carrito)
    pedido = pedidos.obtener_pedido(con, pedido_id)

    # Assert
    assert pedido["subtotal"] == Decimal("11999.50")
    assert pedido["descuento"] == Decimal("0.00")
    assert pedido["envio"] == Decimal("2500.00")
    assert pedido["total"] == Decimal("14499.50")


# R10 · si calcular_total lanza CheckoutError, se propaga y no queda nada guardado

@pytest.mark.parametrize("carrito, zona, cupon, fecha, code", [
    ([item("buzo", "ZZ", 1)], "CABA", None, HOY_VIGENTE, "TALLE_INVALIDO"),
    ([item("buzo", "M", 1)], "MARTE", None, HOY_VIGENTE, "ZONA_INVALIDA"),
    ([item("buzo", "M", 1)], "CABA", "EGRESADOS2026", date(2026, 12, 1), "CUPON_VENCIDO"),
])
def test_si_checkout_lanza_un_error_no_queda_guardado_ni_el_pedido_ni_sus_items(ruta, con, carrito, zona, cupon, fecha, code):
    # Arrange
    # (los datos inválidos vienen del parametrize)

    # Act
    with pytest.raises(CheckoutError) as error:
        guardar(con, carrito, zona=zona, cupon=cupon, fecha=fecha)

    # Assert
    assert error.value.code == code
    assert contar(ruta, "pedidos") == 0
    assert contar(ruta, "items") == 0


def test_un_error_no_borra_ni_deja_a_medias_los_pedidos_anteriores(ruta, con):
    # Arrange
    guardar(con, [item("buzo", "M", 1), item("remera", "S", 2)])

    # Act
    with pytest.raises(CheckoutError):
        guardar(con, [item("buzo", "ZZ", 1)])

    # Assert
    assert contar(ruta, "pedidos") == 1
    assert contar(ruta, "items") == 2


# R10 · cuando guardar_pedido termina, otra conexión ve el pedido completo

def test_otra_conexion_ve_el_pedido_completo_con_sus_importes(ruta, con):
    # Arrange
    carrito = [item("remera", "M", 1)]

    # Act
    pedido_id = guardar(con, carrito)
    pedido = leer_desde_otra_conexion(ruta, pedido_id)

    # Assert
    assert pedido["total"] == Decimal("14499.50")
    assert len(pedido["items"]) == 1


def test_otra_conexion_ve_todos_los_items_del_pedido(ruta, con):
    # Arrange
    carrito = [item("buzo", "M", 1), item("remera", "S", 2)]

    # Act
    pedido_id = guardar(con, carrito)
    pedido = leer_desde_otra_conexion(ruta, pedido_id)

    # Assert
    assert [i["cantidad"] for i in pedido["items"]] == [1, 2]


def test_el_pedido_sigue_completo_despues_de_cerrar_la_conexion_que_lo_guardo(ruta, con):
    # Arrange
    pedido_id = guardar(con, [item("remera", "M", 1)])

    # Act
    con.close()
    pedido = leer_desde_otra_conexion(ruta, pedido_id)

    # Assert
    assert pedido["total"] == Decimal("14499.50")
    assert len(pedido["items"]) == 1


# R10 · los montos que devuelve obtener_pedido son idénticos a los de checkout

def test_los_montos_guardados_son_decimal_sin_perdida_de_precision(con):
    # Arrange
    carrito = [item("remera", "M", 1)]

    # Act
    pedido_id = guardar(con, carrito, cupon="EGRESADOS2026", fecha=date(2026, 11, 1))
    pedido = pedidos.obtener_pedido(con, pedido_id)

    # Assert
    assert pedido["descuento"] == Decimal("1799.93")
    assert pedido["total"] == Decimal("12699.57")
    assert type(pedido["descuento"]) is Decimal


def test_los_montos_guardados_son_identicos_a_los_que_calcula_checkout(con):
    # Arrange
    carrito = [item("buzo", "M", 3), item("remera", "M", 2)]
    esperado = calcular_total(carrito, "GBA", "EGRESADOS2026", HOY_VIGENTE)

    # Act
    pedido_id = guardar(con, carrito, zona="GBA", cupon="EGRESADOS2026")
    pedido = pedidos.obtener_pedido(con, pedido_id)

    # Assert
    assert {clave: pedido[clave] for clave in esperado} == esperado


# R10 · precio_unitario es el del catálogo, nunca uno enviado por el cliente

def test_el_precio_unitario_guardado_es_el_del_catalogo(con):
    # Arrange
    carrito = [item("remera", "M", 1, precio=1)]

    # Act
    pedido_id = guardar(con, carrito)
    pedido = pedidos.obtener_pedido(con, pedido_id)

    # Assert
    assert pedido["items"][0]["precio_unitario"] == Decimal("11999.50")
    assert pedido["total"] == Decimal("14499.50")


# R10 · los datos se guardan normalizados

def test_email_zona_talle_y_cupon_se_guardan_normalizados(con):
    # Arrange
    carrito = [item("remera", " m ", 1)]

    # Act
    pedido_id = guardar(con, carrito, email="  Ana@Mail.COM ", zona=" caba ", cupon=" egresados2026 ")
    pedido = pedidos.obtener_pedido(con, pedido_id)

    # Assert
    assert pedido["email"] == "ana@mail.com"
    assert pedido["zona"] == "CABA"
    assert pedido["cupon"] == "EGRESADOS2026"
    assert pedido["items"][0]["talle"] == "M"


@pytest.mark.parametrize("cupon", ["", "   ", None])
def test_un_cupon_vacio_se_guarda_como_none(con, cupon):
    # Arrange
    carrito = [item("remera", "M", 1)]

    # Act
    pedido_id = guardar(con, carrito, cupon=cupon)
    pedido = pedidos.obtener_pedido(con, pedido_id)

    # Assert
    assert pedido["cupon"] is None


# R10 · pedidos_de: mayúsculas, espacios, orden y consultas seguras

def test_pedidos_de_no_distingue_mayusculas_ni_espacios_en_el_email(con):
    # Arrange
    primero = guardar(con, [item("buzo", "M", 1)], email="ana@mail.com")
    guardar(con, [item("buzo", "M", 1)], email="beto@mail.com")
    segundo = guardar(con, [item("remera", "M", 1)], email="ana@mail.com")

    # Act
    encontrados = pedidos.pedidos_de(con, "  ANA@Mail.com ")

    # Assert
    assert [p["id"] for p in encontrados] == [segundo, primero]


def test_pedidos_de_devuelve_del_mas_reciente_al_mas_antiguo(con):
    # Arrange
    ids = [guardar(con, [item("remera", "M", 1)]) for _ in range(3)]

    # Act
    encontrados = pedidos.pedidos_de(con, "ana@mail.com")

    # Assert
    assert [p["id"] for p in encontrados] == list(reversed(ids))


def test_pedidos_de_un_email_sin_pedidos_devuelve_una_lista_vacia(con):
    # Arrange
    guardar(con, [item("remera", "M", 1)], email="ana@mail.com")

    # Act
    encontrados = pedidos.pedidos_de(con, "nadie@mail.com")

    # Assert
    assert encontrados == []


def test_un_email_con_sql_no_altera_la_consulta(con):
    # Arrange
    guardar(con, [item("remera", "M", 1)], email="ana@mail.com")
    guardar(con, [item("buzo", "M", 1)], email="beto@mail.com")

    # Act
    encontrados = pedidos.pedidos_de(con, "x' OR '1'='1")

    # Assert
    assert encontrados == []


def test_un_email_con_comilla_se_busca_sin_error(con):
    # Arrange
    pedido_id = guardar(con, [item("remera", "M", 1)], email="o'brien@mail.com")

    # Act
    encontrados = pedidos.pedidos_de(con, "o'brien@mail.com")

    # Assert
    assert [p["id"] for p in encontrados] == [pedido_id]
