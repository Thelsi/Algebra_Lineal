# ============ 1) CONFIGURACIÓN Y VERSIONES (útil para la tabla 5.2 del informe) ============
import sys
import numpy as np

print("Python :", sys.version.split()[0])
print("NumPy  :", np.__version__)
print("Entorno: Google Colab")

# ============ 2) NÚCLEO MATEMÁTICO (Cifrado de Hill 2x2, módulo 26) ============
import numpy as np
import unicodedata
from math import gcd

MOD = 26        # tamaño del alfabeto A-Z (A=0, B=1, ..., Z=25)
RELLENO = 23    # letra 'X': se agrega si el mensaje tiene una cantidad impar de letras


def limpiar_texto(texto):
    """Quita tildes, espacios y símbolos. Deja solo letras A-Z en mayúscula."""
    t = unicodedata.normalize("NFD", texto)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return "".join(c for c in t.upper() if "A" <= c <= "Z")


def a_numeros(texto):
    """Convierte letras a números: A=0, B=1, ..., Z=25."""
    return [ord(c) - 65 for c in texto]


def a_texto(nums):
    """Convierte números a letras (siempre en módulo 26)."""
    return "".join(chr(int(n) % MOD + 65) for n in nums)


def determinante(K):
    """det(K) = ad - bc (con enteros exactos, sin errores de punto flotante)."""
    return int(K[0, 0]) * int(K[1, 1]) - int(K[0, 1]) * int(K[1, 0])


def clave_valida(K):
    """K tiene inversa módulo 26 solo si mcd(det(K) mod 26, 26) = 1."""
    return gcd(determinante(K) % MOD, MOD) == 1


def inverso_modular(a, m=MOD):
    """Devuelve x tal que a*x ≡ 1 (mod m)."""
    return pow(int(a), -1, m)


def adjunta(K):
    """Adjunta de una matriz 2x2: se intercambia la diagonal y se cambia el signo de la otra."""
    return np.array([[K[1, 1], -K[0, 1]],
                     [-K[1, 0], K[0, 0]]], dtype=int)


def inversa_mod26(K):
    """K^-1 = (det^-1 mod 26) * adj(K)  (mod 26)."""
    det_mod = determinante(K) % MOD
    if gcd(det_mod, MOD) != 1:
        raise ValueError("La clave no es invertible módulo 26.")
    return (inverso_modular(det_mod) * adjunta(K)) % MOD


def transformar(texto, M):
    """
    Aplica la matriz M a cada par de letras: C = M · P (mod 26).
    Sirve para cifrar (M = K) y para descifrar (M = K^-1).
    Devuelve también cada paso para mostrarlo en pantalla.
    """
    limpio = limpiar_texto(texto)
    nums = a_numeros(limpio)
    relleno = len(nums) % 2 == 1
    if relleno:
        nums.append(RELLENO)

    pasos, salida = [], []
    for i in range(0, len(nums), 2):
        p1, p2 = nums[i], nums[i + 1]
        a, b, c, d = int(M[0, 0]), int(M[0, 1]), int(M[1, 0]), int(M[1, 1])
        f1 = a * p1 + b * p2
        f2 = c * p1 + d * p2
        r1, r2 = f1 % MOD, f2 % MOD
        pasos.append({
            "letras": a_texto([p1, p2]),
            "par": (p1, p2),
            "expr1": f"{a}({p1}) + {b}({p2}) = {f1} → {r1}",
            "expr2": f"{c}({p1}) + {d}({p2}) = {f2} → {r2}",
            "res": a_texto([r1, r2]),
        })
        salida += [r1, r2]

    return {"limpio": limpio, "nums": nums, "relleno": relleno,
            "resultado": a_texto(salida), "pasos": pasos}

# ============ 3) PRUEBAS AUTOMÁTICAS (deben coincidir con el cálculo a mano del informe) ============
K = np.array([[3, 3], [2, 5]])

assert determinante(K) == 9
assert clave_valida(K)
assert inverso_modular(9) == 3
K_inv = inversa_mod26(K)
assert (K_inv == np.array([[15, 17], [20, 9]])).all()
assert ((K @ K_inv) % MOD == np.eye(2, dtype=int)).all()
assert transformar("HOLA", K)["resultado"] == "LGHW"
assert transformar("LGHW", K_inv)["resultado"] == "HOLA"
assert transformar("Código secreto", K)["resultado"] != ""   # tildes y espacios no rompen el programa

print("✅ det(K) = 9")
print("✅ K⁻¹ =", K_inv.tolist())
print("✅ K · K⁻¹ = Identidad (mod 26)")
print("✅ HOLA  →  LGHW  →  HOLA   (igual que a mano)")
print("\nTodas las pruebas pasaron. El programa coincide con el procedimiento manual.")

# ============ 4) APLICACIÓN INTERACTIVA ============
import random
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

TD = "padding:4px 10px;border:1px solid #9ca3af;text-align:center;color:#1f2937"
TH = TD + ";background:#e5e7eb;font-weight:700"


def caja(titulo, cuerpo, borde="#4f46e5", fondo="#f4f6ff"):
    return ("<div style='background:" + fondo + ";color:#1f2937;border-left:6px solid " + borde +
            ";border-radius:8px;padding:10px 16px;margin:10px 0;font-family:sans-serif'>"
            "<div style='font-weight:700;margin-bottom:6px'>" + titulo + "</div>" + cuerpo + "</div>")


def matriz_html(M, nombre):
    filas = ""
    for fila in M:
        filas += "<tr>" + "".join("<td style='" + TD + "'>" + str(int(x)) + "</td>" for x in fila) + "</tr>"
    return ("<div style='display:inline-block;margin:6px 18px 6px 0;vertical-align:top;color:#1f2937'>"
            "<b>" + nombre + "</b><table style='border-collapse:collapse;margin-top:4px;background:#fff'>" +
            filas + "</table></div>")


def resultado_grande(texto):
    pares = " ".join(texto[i:i + 2] for i in range(0, len(texto), 2))
    return ("<div style='font-size:30px;letter-spacing:6px;font-family:monospace;font-weight:700;color:#111827'>" +
            pares + "</div>")


def tabla_pasos(res):
    cab = "".join("<th style='" + TH + "'>" + h + "</th>"
                  for h in ["#", "Par", "Números", "Fila 1: a·p1 + b·p2", "Fila 2: c·p1 + d·p2", "Resultado"])
    filas = ""
    for i, p in enumerate(res["pasos"], 1):
        celdas = [i, p["letras"], str(p["par"]), p["expr1"], p["expr2"], "<b>" + p["res"] + "</b>"]
        filas += "<tr>" + "".join("<td style='" + TD + "'>" + str(x) + "</td>" for x in celdas) + "</tr>"
    return ("<div style='max-height:320px;overflow:auto;background:#fff'>"
            "<table style='border-collapse:collapse;width:100%;font-size:14px'><tr>" + cab + "</tr>" +
            filas + "</table></div>")


ALFABETO = ("<details style='color:#1f2937;margin:8px 0'><summary style='cursor:pointer'>"
            "<b>Ver tabla del alfabeto (letra ↔ número)</b></summary><div style='font-family:monospace;"
            "margin-top:6px;line-height:1.9'>" +
            " &nbsp; ".join(chr(65 + i) + "=" + str(i) for i in range(26)) + "</div></details>")

# ---------- Widgets ----------
estilo = {"description_width": "80px"}
w_texto = widgets.Text(value="HOLA", description="Mensaje:", style=estilo,
                       layout=widgets.Layout(width="560px"))
w_modo = widgets.ToggleButtons(options=["Cifrar", "Descifrar"], description="Modo:", style=estilo)


def entero(valor, nombre):
    return widgets.IntText(value=valor, description=nombre, style={"description_width": "22px"},
                           layout=widgets.Layout(width="110px"))


w_a, w_b, w_c, w_d = entero(3, "a"), entero(3, "b"), entero(2, "c"), entero(5, "d")
btn_run = widgets.Button(description="▶ Ejecutar", button_style="success")
btn_rand = widgets.Button(description="🎲 Clave aleatoria válida", button_style="info",
                          layout=widgets.Layout(width="210px"))
btn_ej = widgets.Button(description="📘 Ejemplo del informe", button_style="warning",
                        layout=widgets.Layout(width="190px"))
salida = widgets.Output()


def ejecutar(_=None):
    with salida:
        clear_output(wait=True)
        K = np.array([[w_a.value, w_b.value], [w_c.value, w_d.value]], dtype=int)
        det = determinante(K)
        det_mod = det % MOD
        g = gcd(det_mod, MOD)

        # ---- Paso 1: validar la clave ----
        cuerpo = matriz_html(K, "Matriz clave K")
        cuerpo += ("<div style='margin-top:8px'>det(K) = (" + str(int(K[0, 0])) + ")(" + str(int(K[1, 1])) +
                   ") − (" + str(int(K[0, 1])) + ")(" + str(int(K[1, 0])) + ") = <b>" + str(det) + "</b>"
                   " → " + str(det) + " mod 26 = <b>" + str(det_mod) + "</b><br>"
                   "mcd(" + str(det_mod) + ", 26) = <b>" + str(g) + "</b></div>")
        if g != 1:
            cuerpo += ("<div style='margin-top:8px'>❌ <b>Clave NO válida:</b> el determinante no es coprimo con 26, "
                       "por lo que K no tiene inversa módulo 26 y el mensaje no se podría descifrar.<br>"
                       "Prueba con otra clave, con la del informe (3, 3, 2, 5) o usa <i>Clave aleatoria válida</i>.</div>")
            display(HTML(caja("1️⃣ Validación de la clave", cuerpo, "#dc2626", "#fef2f2")))
            return
        cuerpo += "<div style='margin-top:8px'>✅ <b>Clave válida:</b> mcd = 1, K tiene inversa módulo 26.</div>"
        display(HTML(caja("1️⃣ Validación de la clave (determinante)", cuerpo, "#16a34a", "#f0fdf4")))

        # ---- Paso 2: matriz inversa ----
        det_inv = inverso_modular(det_mod)
        adj = adjunta(K)
        K_inv = inversa_mod26(K)
        ident = (K @ K_inv) % MOD
        cuerpo = ("<div>Inverso de " + str(det_mod) + " módulo 26: " + str(det_mod) + " · " + str(det_inv) + " = " +
                  str(det_mod * det_inv) + " ≡ <b>1</b> (mod 26) → det⁻¹ = <b>" + str(det_inv) + "</b></div>"
                  "<div style='margin-top:6px'>K⁻¹ = det⁻¹ · adj(K)  (mod 26)</div>" +
                  matriz_html(adj, "adj(K)") + matriz_html(K_inv, "K⁻¹ (mod 26)") +
                  matriz_html(ident, "K · K⁻¹ (mod 26)") +
                  "<div>✅ K · K⁻¹ = matriz identidad, la inversa es correcta.</div>")
        display(HTML(caja("2️⃣ Matriz inversa módulo 26", cuerpo, "#0ea5e9", "#f0f9ff")))

        # ---- Paso 3: procesar el mensaje ----
        texto = w_texto.value
        limpio = limpiar_texto(texto)
        if not limpio:
            display(HTML(caja("⚠️ Mensaje vacío", "Escribe un mensaje con al menos una letra.", "#f59e0b", "#fffbeb")))
            return

        cifrando = (w_modo.value == "Cifrar")
        M = K if cifrando else K_inv
        M_op = K_inv if cifrando else K
        res = transformar(texto, M)

        et_in = "Mensaje original" if cifrando else "Mensaje cifrado (entrada)"
        et_out = "Mensaje cifrado" if cifrando else "Mensaje descifrado"

        cuerpo = ("<div><b>" + et_in + ":</b> " + texto.replace("<", "&lt;") + "</div>"
                  "<div><b>Normalizado (A-Z, sin tildes ni espacios):</b> " + res["limpio"] + "</div>")
        if res["relleno"]:
            cuerpo += "<div>ℹ️ Cantidad impar de letras: se agregó la letra <b>X</b> (=23) al final.</div>"
        cuerpo += ("<div><b>Números:</b> " + str(res["nums"]) + "</div>"
                   "<div><b>Pares (vectores):</b> " + "  ".join(str(p["par"]) for p in res["pasos"]) + "</div>" + ALFABETO)
        display(HTML(caja("3️⃣ Preparación del mensaje", cuerpo, "#7c3aed", "#f5f3ff")))

        mat_usada = "K" if cifrando else "K⁻¹"
        cuerpo = ("<div>Cada par se multiplica: <b>" + ("C" if cifrando else "P") + " = " + mat_usada +
                  " · " + ("P" if cifrando else "C") + "  (mod 26)</b></div>" + tabla_pasos(res))
        display(HTML(caja("4️⃣ Multiplicación de matrices paso a paso", cuerpo, "#ea580c", "#fff7ed")))

        # ---- Resultado ----
        display(HTML(caja("🎯 " + et_out, resultado_grande(res["resultado"]), "#16a34a", "#ecfdf5")))

        # ---- Verificación ida y vuelta ----
        vuelta = transformar(res["resultado"], M_op)["resultado"]
        esperado = res["limpio"] + ("X" if res["relleno"] else "")
        ok = (vuelta == esperado)
        cuerpo = ("<div>Se aplica la matriz contraria (" + ("K⁻¹" if cifrando else "K") + ") al resultado:</div>"
                  "<div style='margin:6px 0'><b>" + res["limpio"] + "</b> → <b>" + res["resultado"] +
                  "</b> → <b>" + vuelta + "</b></div>")
        if ok:
            cuerpo += "<div>✅ <b>Verificación correcta:</b> se recupera exactamente el mensaje de entrada.</div>"
            display(HTML(caja("✔️ Verificación de resultados", cuerpo, "#16a34a", "#f0fdf4")))
        else:
            cuerpo += "<div>❌ La verificación falló.</div>"
            display(HTML(caja("✔️ Verificación de resultados", cuerpo, "#dc2626", "#fef2f2")))


def aleatoria(_=None):
    while True:
        v = [random.randint(0, 25) for __ in range(4)]
        if gcd((v[0] * v[3] - v[1] * v[2]) % MOD, MOD) == 1:
            break
    w_a.value, w_b.value, w_c.value, w_d.value = v
    ejecutar()


def ejemplo(_=None):
    w_texto.value = "HOLA"
    w_modo.value = "Cifrar"
    w_a.value, w_b.value, w_c.value, w_d.value = 3, 3, 2, 5
    ejecutar()


btn_run.on_click(ejecutar)
btn_rand.on_click(aleatoria)
btn_ej.on_click(ejemplo)

display(HTML("<h2 style='font-family:sans-serif;margin-bottom:0'>🔐 Cifrado de Hill con matrices</h2>"
             "<div style='font-family:sans-serif;opacity:.8'>Álgebra Lineal · UNL · Matriz clave 2×2 en módulo 26</div>"))
display(widgets.VBox([
    w_texto,
    w_modo,
    widgets.HTML("<b>Matriz clave</b> &nbsp; K = [[a, b], [c, d]]"),
    widgets.HBox([w_a, w_b, w_c, w_d]),
    widgets.HBox([btn_run, btn_rand, btn_ej]),
    salida,
]))
ejecutar()