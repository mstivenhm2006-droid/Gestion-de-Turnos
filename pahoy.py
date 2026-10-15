import tkinter as tk
from tkinter import messagebox, simpledialog


# ---------------------------------------------------------------------------
# Constantes de la representacion (lienzo de nodos)
# ---------------------------------------------------------------------------
ANCHO_CANVAS = 660
ALTO_CANVAS = 220
MARGEN = 20
Y_CAJA = 84                 # borde superior de los nodos
ALTO_CAJA = 70
ANCHO_CAJA_MAX = 180
ANCHO_CAJA_MIN = 92
SEPARACION_MIN = 26         # espacio libre entre nodos

COLOR_CAJA = "#3495D9"          # nodo en espera
COLOR_CAJA_ACTUAL = "#2ECB70"   # nodo con el turno actual
COLOR_BORDE = "#1F618D"
COLOR_BORDE_ACTUAL = "#F1C40F"
COLOR_FLECHA = "#7F8C8D"

FUENTE = "Arial"


def calcular_diseno(total):
    """Devuelve (ancho_caja, paso, x_inicial) para la fila de nodos."""
    if total <= 1:
        return ANCHO_CAJA_MAX, 0, (ANCHO_CANVAS - ANCHO_CAJA_MAX) / 2

    espacio = ANCHO_CANVAS - 2 * MARGEN
    ancho_caja = min(ANCHO_CAJA_MAX,
                     (espacio - (total - 1) * SEPARACION_MIN) // total)

    if ancho_caja < ANCHO_CAJA_MIN:
        ancho_caja = ANCHO_CAJA_MIN
        paso = ancho_caja + SEPARACION_MIN
        return ancho_caja, paso, MARGEN        # se activa el desplazamiento

    paso = (espacio - ancho_caja) / (total - 1)
    ancho_fila = ancho_caja + (total - 1) * paso
    return ancho_caja, paso, (ANCHO_CANVAS - ancho_fila) / 2


def recortar(texto, limite):
    """Acorta un texto largo para que quepa dentro del nodo."""
    texto = str(texto)
    if len(texto) <= limite:
        return texto
    return texto[:max(1, limite - 3)] + "..."


class Nodo:
    def __init__(self, nombre, identificacion):
        self.nombre = nombre
        self.identificacion = identificacion
        self.turnos = 0
        self.siguiente = None


class ListaCircular:
    def __init__(self):
        self.cabeza = None
        self.actual = None

    def nodos(self):
        """Devuelve los nodos en orden, comenzando por la cabeza."""
        if not self.cabeza:
            return []
        resultado, p = [], self.cabeza
        while True:
            resultado.append(p)
            p = p.siguiente
            if p == self.cabeza:
                break
        return resultado

    def agregar(self, nombre, identificacion):
        nuevo = Nodo(nombre, identificacion)
        if not self.cabeza:
            self.cabeza = self.actual = nuevo
            nuevo.siguiente = nuevo
        else:
            p = self.cabeza
            while p.siguiente != self.cabeza:
                p = p.siguiente
            p.siguiente = nuevo
            nuevo.siguiente = self.cabeza

    def agregar_despues(self, referencia_id, nombre, identificacion):
        if not self.cabeza:
            self.agregar(nombre, identificacion)
            return True
        
        ref = self.buscar(referencia_id)
        if not ref:
            return False
            
        nuevo = Nodo(nombre, identificacion)
        nuevo.siguiente = ref.siguiente
        ref.siguiente = nuevo
        return True

    def agregar_antes(self, referencia_id, nombre, identificacion):
        if not self.cabeza:
            self.agregar(nombre, identificacion)
            return True
            
        ref = self.buscar(referencia_id)
        if not ref:
            return False
            
        p = self.cabeza
        while p.siguiente != ref and p.siguiente != self.cabeza:
            p = p.siguiente
            
        nuevo = Nodo(nombre, identificacion)
        nuevo.siguiente = ref
        p.siguiente = nuevo
        if ref == self.cabeza:
            self.cabeza = nuevo
        return True

    def agregar_prioridad(self, nombre, identificacion):
        nuevo = Nodo(nombre, identificacion)
        if not self.cabeza:
            self.cabeza = self.actual = nuevo
            nuevo.siguiente = nuevo
        else:
            objetivo = self.actual if self.actual else self.cabeza
            nuevo.siguiente = objetivo.siguiente
            objetivo.siguiente = nuevo
        return True

    def buscar(self, identificacion):
        if not self.cabeza:
            return None
        p = self.cabeza
        while True:
            if p.identificacion == identificacion:
                return p
            p = p.siguiente
            if p == self.cabeza:
                break
        return None

    def eliminar(self, identificacion):
        if not self.cabeza:
            return False

        p = self.cabeza
        anterior = None

        while True:
            if p.identificacion == identificacion:
                if p.siguiente == p:
                    self.cabeza = self.actual = None
                else:
                    if anterior:
                        anterior.siguiente = p.siguiente
                    else:
                        ultimo = self.cabeza
                        while ultimo.siguiente != self.cabeza:
                            ultimo = ultimo.siguiente
                        self.cabeza = p.siguiente
                        ultimo.siguiente = self.cabeza

                    if self.actual == p:
                        self.actual = p.siguiente
                return True

            anterior, p = p, p.siguiente
            if p == self.cabeza:
                break

        return False

    def siguiente_turno(self):
        if self.actual:
            self.actual = self.actual.siguiente

    def anterior_turno(self):
        if self.actual:
            p = self.actual
            while p.siguiente != self.actual:
                p = p.siguiente
            self.actual = p

    def contar(self):
        if not self.cabeza:
            return 0

        n, p = 0, self.cabeza
        while True:
            n += 1
            p = p.siguiente
            if p == self.cabeza:
                break
        return n

    def mostrar(self):
        if not self.cabeza:
            return "Lista vacía"

        texto = ""
        p = self.cabeza

        while True:
            marca = " [TURNO ACTUAL]" if p == self.actual else ""
            texto += f"({p.identificacion}) {p.nombre}{marca} -> "
            p = p.siguiente

            if p == self.cabeza:
                break

        return texto + "(regresa al inicio)"


class App:
    def __init__(self, root):
        self.root = root
        self.lista = ListaCircular()
        self.tiempo = 10

        root.title("Sistema de Gestión de Turnos - Simulación Continua")
        root.geometry("740x780")

        # ---------- DATOS ----------
        datos = tk.LabelFrame(root, text="Datos de la Persona",
                              font=("Arial", 10, "bold"))
        datos.pack(fill="x", padx=5, pady=5)

        tk.Label(datos, text="Nombre:").grid(row=0, column=0, padx=15, pady=8)
        self.nombre = tk.Entry(datos, width=25)
        self.nombre.grid(row=0, column=1)

        tk.Label(datos, text="Identificación:").grid(row=1, column=0, padx=15, pady=8)
        self.id = tk.Entry(datos, width=25)
        self.id.grid(row=1, column=1)

        # ---------- OPERACIONES ----------
        op = tk.LabelFrame(root, text="Operaciones Básicas",
                           font=("Arial", 10, "bold"))
        op.pack(fill="x", padx=5, pady=5)

        self.boton(op, "Agregar Persona", self.agregar, "#3495D9", 0, 0)
        self.boton(op, "Buscar Persona", self.buscar, "#3398DC", 0, 1)
        self.boton(op, "Eliminar Persona", self.eliminar, "#E84D3B", 0, 2)

        self.boton(op, "Siguiente Turno", self.siguiente, "#2ECB70", 1, 0)
        self.boton(op, "Anterior Turno", self.anterior, "#E47F23", 1, 1)
        self.boton(op, "Mostrar Lista", self.mostrar, "#3697DB", 1, 2)

        # ---------- FUNCIONALIDADES (RETO) ----------
        extra = tk.LabelFrame(root, text="Funcionalidades Avanzadas (Reto)",
                              font=("Arial", 10, "bold"))
        extra.pack(fill="x", padx=5, pady=5)

        self.boton(extra, "Insertar Después", self.pedir_agregar_despues, "#8E44AD", 0, 0)
        self.boton(extra, "Insertar Antes", self.pedir_agregar_antes, "#8E44AD", 0, 1)
        self.boton(extra, "Turno Prioritario", self.agregar_prioridad, "#D35400", 0, 2)

        self.boton(extra, "Avanzar N Turnos", self.avanzar_n_turnos, "#9B58B5", 1, 0)
        self.boton(extra, "Atender y Eliminar", self.atender, "#C17C6D", 1, 1)

        # ---------- ESTADO ----------
        estado = tk.LabelFrame(root, text="Estado Actual del Sistema",
                               font=("Arial", 10, "bold"))
        estado.pack(fill="both", expand=True, padx=5, pady=5)

        self.actual = tk.Label(estado, text="Turno Actual -> Sin personas",
                               fg="#B4423B", font=("Arial", 10, "bold"))
        self.actual.pack(anchor="w", padx=15, pady=5)

        self.personas = tk.Label(estado, text="Personas Registradas: 0")
        self.personas.pack(anchor="w", padx=15)

        self.timer = tk.Label(estado, text="Tiempo restante: --",
                              font=("Arial", 10, "bold"))
        self.timer.pack(anchor="w", padx=15, pady=5)

        tk.Label(estado, text="Representación Visual de la Lista Circular:",
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=15)

        self.canvas = tk.Canvas(estado, width=ANCHO_CANVAS, height=ALTO_CANVAS,
                                bg="white", highlightthickness=1,
                                highlightbackground="#CCCCCC")
        self.canvas.pack(padx=15, pady=5)

        self.barra = tk.Scrollbar(estado, orient="horizontal",
                                  command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.barra.set)
        self.barra.pack(fill="x", padx=15, pady=(0, 5))

        self.dibujar_nodos()
        self.temporizador()

    def boton(self, padre, texto, comando, color, fila, columna):
        tk.Button(padre, text=texto, command=comando,
                  bg=color, fg="white", width=18,
                  font=("Arial", 9, "bold")).grid(
                      row=fila, column=columna, padx=5, pady=5)

    def dibujar_nodos(self):
        c = self.canvas
        c.delete("all")

        nodos = self.lista.nodos()
        total = len(nodos)

        if total == 0:
            c.create_text(ANCHO_CANVAS / 2, ALTO_CANVAS / 2,
                          text="Lista vacía: todavía no hay nodos",
                          fill="#888888", font=(FUENTE, 12, "bold"))
            c.config(scrollregion=(0, 0, ANCHO_CANVAS, ALTO_CANVAS))
            return

        ancho_caja, paso, x0 = calcular_diseno(total)

        if ancho_caja >= 160:
            fuente = 10
        elif ancho_caja >= 105:
            fuente = 9
        else:
            fuente = 8

        limite_id = max(6, int(ancho_caja / 5.4))
        limite_nombre = max(6, int(ancho_caja / 5.0))

        posiciones = [(x0 + i * paso, Y_CAJA) for i in range(total)]
        centros = [x + ancho_caja / 2 for x, _ in posiciones]
        y_centro = Y_CAJA + ALTO_CAJA / 2

        for i in range(total - 1):
            x_salida = posiciones[i][0] + ancho_caja + 2
            x_llegada = posiciones[i + 1][0] - 6
            c.create_line(x_salida, y_centro, x_llegada, y_centro,
                          arrow=tk.LAST, width=2, fill=COLOR_FLECHA)

        if total == 1:
            x_izq = posiciones[0][0] + 20
            x_der = posiciones[0][0] + ancho_caja - 20
            c.create_arc(x_izq, Y_CAJA - 52, x_der, Y_CAJA + 20,
                         start=0, extent=180, style=tk.ARC,
                         arrow=tk.LAST, width=2, outline=COLOR_FLECHA)
            c.create_text(centros[0], Y_CAJA - 60,
                          text="se apunta a sí mismo",
                          fill="#555555", font=(FUENTE, 8, "italic"))
        else:
            c.create_line(centros[-1], Y_CAJA - 2,
                          (centros[-1] + centros[0]) / 2, Y_CAJA - 60,
                          centros[0], Y_CAJA - 2,
                          smooth=True, arrow=tk.LAST, width=2,
                          fill=COLOR_FLECHA)
            c.create_text((centros[-1] + centros[0]) / 2, Y_CAJA - 68,
                          text="regresa al inicio",
                          fill="#555555", font=(FUENTE, 8, "italic"))

        for i, (nodo, (x, y)) in enumerate(zip(nodos, posiciones)):
            es_actual = nodo is self.lista.actual

            c.create_rectangle(x, y, x + ancho_caja, y + ALTO_CAJA,
                               fill=COLOR_CAJA_ACTUAL if es_actual else COLOR_CAJA,
                               outline=COLOR_BORDE_ACTUAL if es_actual else COLOR_BORDE,
                               width=4 if es_actual else 2)

            c.create_text(centros[i], y + 16,
                          text=recortar(nodo.identificacion, limite_id),
                          fill="white", font=(FUENTE, fuente, "bold"))
            c.create_text(centros[i], y + 38,
                          text=recortar(nodo.nombre, limite_nombre),
                          fill="white", font=(FUENTE, fuente))
            c.create_text(centros[i], y + 57,
                          text=f"Turnos atendidos: {nodo.turnos}",
                          fill="#EAF2F8", font=(FUENTE, max(7, fuente - 1)))

        c.create_text(centros[0], Y_CAJA + ALTO_CAJA + 12,
                      text="inicio de la lista (cabeza)",
                      fill="#1F618D", font=(FUENTE, 8, "bold"))

        c.create_text(10, ALTO_CANVAS - 30, anchor="w",
                      text="Verde con borde amarillo = persona en turno    "
                           "Azul = en espera",
                      fill="#555555", font=(FUENTE, 8))
        c.create_text(10, ALTO_CANVAS - 14, anchor="w",
                      text="Cada flecha une un nodo con el siguiente; "
                           "la última cierra el ciclo.",
                      fill="#555555", font=(FUENTE, 8))

        ancho_fila = ancho_caja + (total - 1) * paso
        ancho_necesario = max(ANCHO_CANVAS, x0 + ancho_fila + MARGEN)
        c.config(scrollregion=(0, 0, ancho_necesario, ALTO_CANVAS))

    def actualizar(self):
        if self.lista.actual:
            p = self.lista.actual
            self.actual.config(
                text=f"Turno Actual -> Nombre: {p.nombre} | "
                     f"ID: {p.identificacion} | "
                     f"Atenciones recibidas: {p.turnos}"
            )
        else:
            self.actual.config(text="Turno Actual -> Sin personas")

        self.personas.config(
            text=f"Personas Registradas: {self.lista.contar()}"
        )
        self.dibujar_nodos()

    def agregar(self):
        nombre = self.nombre.get()
        identificacion = self.id.get()

        if not nombre or not identificacion:
            messagebox.showwarning("Aviso", "Complete los datos")
            return

        self.lista.agregar(nombre, identificacion)
        self.actualizar()

    def pedir_agregar_despues(self):
        nombre = self.nombre.get()
        identificacion = self.id.get()
        if not nombre or not identificacion:
            messagebox.showwarning("Aviso", "Complete Nombre e Identificación")
            return
        ref_id = simpledialog.askstring("Insertar Después", "Ingrese la ID de referencia:")
        if ref_id:
            if self.lista.agregar_despues(ref_id, nombre, identificacion):
                self.actualizar()
            else:
                messagebox.showerror("Error", "No se encontró la ID de referencia")

    def pedir_agregar_antes(self):
        nombre = self.nombre.get()
        identificacion = self.id.get()
        if not nombre or not identificacion:
            messagebox.showwarning("Aviso", "Complete Nombre e Identificación")
            return
        ref_id = simpledialog.askstring("Insertar Antes", "Ingrese la ID de referencia:")
        if ref_id:
            if self.lista.agregar_antes(ref_id, nombre, identificacion):
                self.actualizar()
            else:
                messagebox.showerror("Error", "No se encontró la ID de referencia")

    def agregar_prioridad(self):
        nombre = self.nombre.get()
        identificacion = self.id.get()
        if not nombre or not identificacion:
            messagebox.showwarning("Aviso", "Complete Nombre e Identificación")
            return
        self.lista.agregar_prioridad(nombre, identificacion)
        self.actualizar()

    def avanzar_n_turnos(self):
        n = simpledialog.askinteger("Avanzar Turnos", "Ingrese el número de turnos a avanzar:", initialvalue=1, minvalue=1)
        if n:
            for _ in range(n):
                self.lista.siguiente_turno()
            self.tiempo = 10
            self.actualizar()

    def buscar(self):
        p = self.lista.buscar(self.id.get())
        if p:
            messagebox.showinfo("Resultado", f"Persona encontrada: {p.nombre}")
        else:
            messagebox.showwarning("Resultado", "Persona no encontrada")

    def eliminar(self):
        if self.lista.eliminar(self.id.get()):
            self.actualizar()
        else:
            messagebox.showwarning("Aviso", "Persona no encontrada")

    def siguiente(self):
        self.lista.siguiente_turno()
        self.tiempo = 10
        self.actualizar()

    def anterior(self):
        self.lista.anterior_turno()
        self.tiempo = 10
        self.actualizar()

    def mostrar(self):
        messagebox.showinfo("Lista Circular", self.lista.mostrar())

    def atender(self):
        if self.lista.actual:
            self.lista.actual.turnos += 1
            self.lista.eliminar(self.lista.actual.identificacion)
            self.tiempo = 10
            self.actualizar()
    def temporizador(self):
        """Temporizador recurrente y continuo que rota los turnos y reinicia el contador de inmediato"""
        if self.lista.actual:
            if self.tiempo <= 0:
                self.lista.actual.turnos += 1
                self.lista.siguiente_turno()
                self.tiempo = 10
                self.actualizar()
            
            self.timer.config(text=f"Tiempo restante: {self.tiempo} segundos")
            self.tiempo -= 1
        else:
            self.timer.config(text="Tiempo restante: --")
            self.tiempo = 10

        self.root.after(1000, self.temporizador)
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()