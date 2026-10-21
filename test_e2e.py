import json
import threading
import urllib.error
import urllib.request

import pytest #type: ignore

import api

RUTA = "/api/v1/pedidos"


@pytest.fixture
def url(tmp_path):
    servidor = api.crear_servidor(str(tmp_path / "tienda.db"), 0)
    threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}"
    servidor.shutdown()
    servidor.server_close()


def pedir(url, metodo, ruta, cuerpo=None, crudo=None):
    datos = crudo if crudo is not None else (json.dumps(cuerpo).encode() if cuerpo is not None else None)
    req = urllib.request.Request(url + ruta, data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def compra(**cambios):
    cuerpo = {"email": "ana@mail.com", "zona": "CABA",
              "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}]}
    cuerpo.update(cambios)
    return cuerpo


def test_una_ruta_inexistente_devuelve_404(url):
    status, cuerpo = pedir(url, "GET", "/api/v1/otra")
    assert status == 404
    assert cuerpo["error"]["code"] == "RUTA_INEXISTENTE"


def es_error(cuerpo, code):
    return (set(cuerpo) == {"error"}
            and cuerpo["error"]["code"] == code
            and isinstance(cuerpo["error"]["message"], str))


# POST /api/v1/pedidos · 201 con los montos como texto

def test_crear_un_pedido_con_cupon_y_fecha_devuelve_201_con_los_montos_como_texto(url):
    # Arrange
    cuerpo = compra(carrito=[{"producto": "remera", "talle": "M", "cantidad": 1}],
                    cupon="EGRESADOS2026", fecha="2026-11-30")

    # Act
    status, creado = pedir(url, "POST", RUTA, cuerpo)

    # Assert
    assert status == 201
    assert type(creado["id"]) is int
    assert {clave: creado[clave] for clave in ("subtotal", "descuento", "envio", "total")} == {
        "subtotal": "11999.50", "descuento": "1799.93", "envio": "2500.00", "total": "12699.57",
    }


def test_crear_un_pedido_sin_cupon_ni_fecha_devuelve_201_con_los_montos_como_texto(url):
    # Arrange
    cuerpo = compra()

    # Act
    status, creado = pedir(url, "POST", RUTA, cuerpo)

    # Assert
    assert status == 201
    assert creado["total"] == "27499.90"
    assert creado["envio"] == "2500.00"


# GET /api/v1/pedidos/{id} · flujo completo POST -> GET

def test_un_pedido_creado_se_puede_leer_completo_con_get(url):
    # Arrange
    cuerpo = compra(email="  Ana@Mail.COM ",
                    carrito=[{"producto": "remera", "talle": "m", "cantidad": 1}])
    _, creado = pedir(url, "POST", RUTA, cuerpo)

    # Act
    status, pedido = pedir(url, "GET", f"{RUTA}/{creado['id']}")

    # Assert
    assert status == 200
    assert pedido == {
        "id": creado["id"], "email": "ana@mail.com", "zona": "CABA", "cupon": None,
        "subtotal": "11999.50", "descuento": "0.00", "envio": "2500.00", "total": "14499.50",
        "items": [{"producto": "remera", "talle": "M", "cantidad": 1, "precio_unitario": "11999.50"}],
    }


# 422 · cualquier CheckoutError

@pytest.mark.parametrize("cambios, code", [
    ({"carrito": [{"producto": "buzo", "talle": "XXXL", "cantidad": 1}]}, "TALLE_INVALIDO"),
    ({"carrito": []}, "CARRITO_VACIO"),
    ({"cupon": "EGRESADOS2026", "fecha": "2026-12-01"}, "CUPON_VENCIDO"),
])
def test_un_error_de_negocio_devuelve_422_con_su_code(url, cambios, code):
    # Arrange
    cuerpo = compra(**cambios)

    # Act
    status, respuesta = pedir(url, "POST", RUTA, cuerpo)

    # Assert
    assert status == 422
    assert es_error(respuesta, code)


# 400 · JSON_INVALIDO

def test_un_cuerpo_que_no_es_json_devuelve_400_json_invalido(url):
    # Arrange
    crudo = b"{no"

    # Act
    status, respuesta = pedir(url, "POST", RUTA, crudo=crudo)

    # Assert
    assert status == 400
    assert es_error(respuesta, "JSON_INVALIDO")


# 400 · DATOS_INCOMPLETOS

@pytest.mark.parametrize("falta", ["email", "zona", "carrito"])
def test_si_falta_email_zona_o_carrito_devuelve_400_datos_incompletos(url, falta):
    # Arrange
    cuerpo = compra()
    del cuerpo[falta]

    # Act
    status, respuesta = pedir(url, "POST", RUTA, cuerpo)

    # Assert
    assert status == 400
    assert es_error(respuesta, "DATOS_INCOMPLETOS")


@pytest.mark.parametrize("cuerpo", [compra(email=123), compra(zona=5), compra(carrito="buzo"), []])
def test_si_los_datos_tienen_otro_tipo_devuelve_400_datos_incompletos(url, cuerpo):
    # Arrange
    # (el cuerpo con el tipo equivocado viene del parametrize)

    # Act
    status, respuesta = pedir(url, "POST", RUTA, cuerpo)

    # Assert
    assert status == 400
    assert es_error(respuesta, "DATOS_INCOMPLETOS")


# 400 · FECHA_INVALIDA

@pytest.mark.parametrize("fecha", ["30/11/2026", "mañana"])
def test_una_fecha_sin_formato_aaaa_mm_dd_devuelve_400_fecha_invalida(url, fecha):
    # Arrange
    cuerpo = compra(fecha=fecha)

    # Act
    status, respuesta = pedir(url, "POST", RUTA, cuerpo)

    # Assert
    assert status == 400
    assert es_error(respuesta, "FECHA_INVALIDA")


# 404 · PEDIDO_INEXISTENTE y RUTA_INEXISTENTE

def test_un_pedido_que_no_existe_devuelve_404_pedido_inexistente(url):
    # Arrange
    ruta = f"{RUTA}/999"

    # Act
    status, respuesta = pedir(url, "GET", ruta)

    # Assert
    assert status == 404
    assert es_error(respuesta, "PEDIDO_INEXISTENTE")


def test_un_post_a_una_ruta_inexistente_devuelve_404(url):
    # Arrange
    cuerpo = compra()

    # Act
    status, respuesta = pedir(url, "POST", "/api/v1/otra", cuerpo)

    # Assert
    assert status == 404
    assert es_error(respuesta, "RUTA_INEXISTENTE")
