import csv
from graphviz import Digraph

# ============================================================
# CLASE NODO DEL ÁRBOL B
# ============================================================

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t                      # Grado mínimo
        self.leaf = leaf                # Indica si es hoja
        self.keys = []                  # Claves
        self.children = []              # Hijos


# ============================================================
# CLASE ÁRBOL B
# ============================================================

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, True)
        self.t = t

    # ========================================================
    # BÚSQUEDA
    # ========================================================

    def search(self, k, x=None):

        if x is None:
            x = self.root

        i = 0

        while i < len(x.keys) and k > x.keys[i]:
            i += 1

        if i < len(x.keys) and k == x.keys[i]:
            return (x, i)

        if x.leaf:
            return None

        return self.search(k, x.children[i])

    # ========================================================
    # INSERCIÓN
    # ========================================================

    def insert(self, k):

        root = self.root

        # Si la raíz está llena
        if len(root.keys) == (2 * self.t) - 1:

            new_root = BTreeNode(self.t, False)
            new_root.children.insert(0, root)

            self.split_child(new_root, 0)

            self.root = new_root

            self.insert_non_full(new_root, k)

        else:
            self.insert_non_full(root, k)

    # --------------------------------------------------------

    def insert_non_full(self, x, k):

        i = len(x.keys) - 1

        if x.leaf:

            x.keys.append(None)

            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1

            x.keys[i + 1] = k

        else:

            while i >= 0 and k < x.keys[i]:
                i -= 1

            i += 1

            if len(x.children[i].keys) == (2 * self.t) - 1:

                self.split_child(x, i)

                if k > x.keys[i]:
                    i += 1

            self.insert_non_full(x.children[i], k)

    # --------------------------------------------------------

    def split_child(self, x, i):

        t = self.t

        y = x.children[i]

        z = BTreeNode(t, y.leaf)

        # Clave del medio
        middle_key = y.keys[t - 1]

        # División de claves
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]

        # División de hijos
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        # Insertar nuevo hijo
        x.children.insert(i + 1, z)

        # Subir clave media
        x.keys.insert(i, middle_key)

    # ========================================================
    # ELIMINACIÓN
    # ========================================================

    def delete(self, k):
        self.delete_internal(self.root, k)

        # Ajustar raíz
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    # --------------------------------------------------------

    def delete_internal(self, node, k):

        t = self.t
        idx = 0

        while idx < len(node.keys) and node.keys[idx] < k:
            idx += 1

        # Caso 1: clave encontrada
        if idx < len(node.keys) and node.keys[idx] == k:

            # Nodo hoja
            if node.leaf:
                node.keys.pop(idx)

            else:
                self.delete_internal_non_leaf(node, k, idx)

        else:

            # No encontrada y es hoja
            if node.leaf:
                print("La clave no existe.")
                return

            flag = idx == len(node.keys)

            if len(node.children[idx].keys) < t:
                self.fill(node, idx)

            if flag and idx > len(node.keys):
                self.delete_internal(node.children[idx - 1], k)
            else:
                self.delete_internal(node.children[idx], k)

    # --------------------------------------------------------

    def delete_internal_non_leaf(self, node, k, idx):

        t = self.t

        # Predecesor
        if len(node.children[idx].keys) >= t:

            pred = self.get_predecessor(node, idx)

            node.keys[idx] = pred

            self.delete_internal(node.children[idx], pred)

        # Sucesor
        elif len(node.children[idx + 1].keys) >= t:

            succ = self.get_successor(node, idx)

            node.keys[idx] = succ

            self.delete_internal(node.children[idx + 1], succ)

        else:

            self.merge(node, idx)

            self.delete_internal(node.children[idx], k)

    # --------------------------------------------------------

    def get_predecessor(self, node, idx):

        current = node.children[idx]

        while not current.leaf:
            current = current.children[-1]

        return current.keys[-1]

    # --------------------------------------------------------

    def get_successor(self, node, idx):

        current = node.children[idx + 1]

        while not current.leaf:
            current = current.children[0]

        return current.keys[0]

    # --------------------------------------------------------

    def fill(self, node, idx):

        t = self.t

        if idx != 0 and len(node.children[idx - 1].keys) >= t:
            self.borrow_from_prev(node, idx)

        elif idx != len(node.children) - 1 and len(node.children[idx + 1].keys) >= t:
            self.borrow_from_next(node, idx)

        else:

            if idx != len(node.children) - 1:
                self.merge(node, idx)
            else:
                self.merge(node, idx - 1)

    # --------------------------------------------------------

    def borrow_from_prev(self, node, idx):

        child = node.children[idx]
        sibling = node.children[idx - 1]

        child.keys.insert(0, node.keys[idx - 1])

        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

        node.keys[idx - 1] = sibling.keys.pop()

    # --------------------------------------------------------

    def borrow_from_next(self, node, idx):

        child = node.children[idx]
        sibling = node.children[idx + 1]

        child.keys.append(node.keys[idx])

        if not child.leaf:
            child.children.append(sibling.children.pop(0))

        node.keys[idx] = sibling.keys.pop(0)

    # --------------------------------------------------------

    def merge(self, node, idx):

        child = node.children[idx]
        sibling = node.children[idx + 1]

        child.keys.append(node.keys[idx])

        child.keys.extend(sibling.keys)

        if not child.leaf:
            child.children.extend(sibling.children)

        node.keys.pop(idx)
        node.children.pop(idx + 1)

    # ========================================================
    # RECORRIDO
    # ========================================================

    def traverse(self, node=None):

        if node is None:
            node = self.root

        i = 0

        while i < len(node.keys):

            if not node.leaf:
                self.traverse(node.children[i])

            print(node.keys[i], end=" ")

            i += 1

        if not node.leaf:
            self.traverse(node.children[i])

    # ========================================================
    # CARGA MASIVA DESDE CSV
    # ========================================================

    def load_csv(self, filename):

        try:

            with open(filename, newline='', encoding='utf-8') as file:

                reader = csv.reader(file)

                count = 0

                for row in reader:

                    for item in row:

                        try:
                            value = int(item)
                            self.insert(value)
                            count += 1

                        except ValueError:
                            pass

                print(f"\n✔ Se cargaron {count} registros correctamente.")

        except FileNotFoundError:
            print("\n✘ Archivo no encontrado.")

    # ========================================================
    # GENERAR GRAFICACIÓN CON GRAPHVIZ
    # ========================================================

    def generate_graph(self, filename="arbol_b"):

        dot = Digraph()

        def add_nodes_edges(node, parent=None, index=0):

            node_id = str(id(node))

            label = " | ".join(map(str, node.keys))

            dot.node(node_id, label, shape="record")

            if parent:
                dot.edge(parent, node_id)

            for child in node.children:
                add_nodes_edges(child, node_id)

        add_nodes_edges(self.root)

        dot.render(filename, format='png', cleanup=True)

        print(f"\n✔ Imagen generada: {filename}.png")


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu():

    print("\n================================================")
    print("IMPLEMENTACIÓN DE ÁRBOL B")
    print("================================================")

    grado = int(input("Ingrese el grado del Árbol B: "))

    btree = BTree(grado)

    while True:

        print("\n================ MENÚ =================")
        print("1. Insertar clave")
        print("2. Buscar clave")
        print("3. Eliminar clave")
        print("4. Mostrar recorrido")
        print("5. Cargar datos desde CSV")
        print("6. Generar gráfica del árbol")
        print("7. Salir")
        print("=======================================")

        option = input("Seleccione una opción: ")

        # ====================================================
        # INSERTAR
        # ====================================================

        if option == "1":

            key = int(input("Ingrese la clave: "))

            btree.insert(key)

            print("✔ Clave insertada correctamente.")

        # ====================================================
        # BUSCAR
        # ====================================================

        elif option == "2":

            key = int(input("Ingrese la clave a buscar: "))

            result = btree.search(key)

            if result:
                print("✔ Clave encontrada.")
            else:
                print("✘ Clave no encontrada.")

        # ====================================================
        # ELIMINAR
        # ====================================================

        elif option == "3":

            key = int(input("Ingrese la clave a eliminar: "))

            btree.delete(key)

            print("✔ Operación completada.")

        # ====================================================
        # MOSTRAR
        # ====================================================

        elif option == "4":

            print("\nRecorrido del Árbol B:")

            btree.traverse()

            print()

        # ====================================================
        # CSV
        # ====================================================

        elif option == "5":

            filename = input("Ingrese el nombre del archivo CSV: ")

            btree.load_csv(filename)

        # ====================================================
        # GRAPHVIZ
        # ====================================================

        elif option == "6":

            filename = input("Ingrese nombre de la imagen: ")

            btree.generate_graph(filename)

        # ====================================================
        # SALIR
        # ====================================================

        elif option == "7":

            print("\nSaliendo del programa...")

            break

        else:
            print("\n✘ Opción inválida.")


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    menu()


# ============================================================
# README (COPIAR EN README.md)
# ============================================================

"""
# IMPLEMENTACIÓN DE ÁRBOL B EN PYTHON

## Descripción

Este proyecto implementa un Árbol B configurable por grado utilizando Python.

El sistema permite:

- Insertar claves
- Buscar claves
- Eliminar claves
- Cargar datos desde archivos CSV
- Generar representación gráfica usando Graphviz

---

## Requisitos

Instalar Graphviz:

https://graphviz.org/download/

Instalar librería de Python:

pip install graphviz

---

## Ejecución

Ejecutar:

python arbol_b.py

---

## Archivos CSV

Colocar los archivos CSV en la raíz del proyecto.

Ejemplo:

datos1.csv
datos2.csv

Cada archivo debe contener mínimo 100 registros.

Ejemplo de contenido:

10,20,30,40,50
60,70,80,90

---

## Generación gráfica

La opción 6 del menú genera una imagen PNG del árbol.

Ejemplo:

arbol.png

---

## Integrantes

Nombre: ___________________
Carnet: ___________________
Participación: ______%

Nombre: ___________________
Carnet: ___________________
Participación: ______%

---

## Tecnologías utilizadas

- Python
- Graphviz

"""