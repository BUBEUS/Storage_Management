#project: Mini Allegro - System Magazynowy
#opis test
import tkinter as tk
from tkinter import ttk
import os
import sqlite3
from tkinter import messagebox
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import calendar

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mini_allegro.db")

class MagazynApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System Magazynowy - Mini Allegro")
        self.geometry("1250x700")
        self.minsize(900, 600)
        self.configure(bg="#f5f7fa")  # Jasne tło

        # Styl ttk
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#e3eaf2", borderwidth=0)
        style.configure("TFrame", background="#f5f7fa")
        style.configure("TLabel", background="#f5f7fa", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#1976d2", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background="#ffffff", fieldbackground="#f5f7fa")
        style.map("TButton", background=[("active", "#1976d2")], foreground=[("active", "white")])

        # Nagłówek aplikacji
        header = ttk.Label(self, text="Mini Allegro - System Magazynowy", font=("Segoe UI", 18, "bold"), background="#1976d2", foreground="white", anchor="center")
        header.pack(fill="x", pady=(0, 5))

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_produkty_tab()
        self.create_operacje_tab()
        self.create_zamow_tab()
        self.create_cart_tab()
        self.create_orders_tab()
        self.cart_items = []
        self.create_PozycjeZam_tab()
        self.create_analiza_tab() 
        
        

#Frame produkty
    def create_produkty_tab(self):
        self.produkty_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.produkty_frame, text="Produkty")
        self.produkty_frame.grid_rowconfigure(0, weight=1)
        self.produkty_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self.produkty_frame,
            columns=("ID", "Nazwa", "Kategoria", "Cena", "Ilość", "LokalizacjaID"),
            show="headings"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.load_products()
        self.entry_frame = ttk.Frame(self.produkty_frame)
        self.entry_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.entry_frame.grid_columnconfigure(0, weight=1)
        self.entry_frame.grid_columnconfigure(1, weight=1)
        self.entry_frame.grid_columnconfigure(2, weight=1)
        self.entry_frame.grid_columnconfigure(3, weight=1)
        self.entry_frame.grid_columnconfigure(4, weight=1)
        self.entry_frame.grid_columnconfigure(5, weight=1)

        # Etykiety nad polami
        labels = ["Nazwa produktu", "Kategoria", "Cena", "Ilość", "LokalizacjaID"]
        for i, text in enumerate(labels):
            label = ttk.Label(self.entry_frame, text=text)
            label.grid(row=0, column=i, padx=5, pady=(5, 0), sticky="w")

        # Pola Entry pod etykietami
        self.name_entry = ttk.Entry(self.entry_frame, width=25, font=("Segoe UI", 11))
        self.name_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.kategoria_entry = ttk.Entry(self.entry_frame, width=15, font=("Segoe UI", 11))
        self.kategoria_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.prod_price_entry = ttk.Entry(self.entry_frame, width=10, font=("Segoe UI", 11))
        self.prod_price_entry.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        self.prod_price_entry.insert(0, 0)

        self.qty_entry = ttk.Entry(self.entry_frame, width=10, font=("Segoe UI", 11))
        self.qty_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self.qty_entry.insert(0, 0)

        self.lokalizacja_entry = ttk.Combobox(self.entry_frame, width=10, font=("Segoe UI", 11), state="readonly")
        self.lokalizacja_entry.grid(row=1, column=4, padx=5, pady=5, sticky="ew")
        self.Load_lokalizacja_combo()

        add_button = ttk.Button(self.entry_frame, text="Dodaj produkt", command=self.add_product)
        add_button.grid(row=1, column=5, padx=10, pady=5, sticky="ew")


    def Load_lokalizacja_combo(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MagazynID FROM Magazyn")
        Magazyn = cursor.fetchall()
        conn.close()

        self.lok_map = [zid[0] for zid in Magazyn]
        self.lokalizacja_entry["values"] = self.lok_map

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ProduktID, Nazwa, Kategoria, Cena, Ilosc, LokalizacjaID FROM Produkty")
        for produkt in cursor.fetchall():
            self.tree.insert("", "end", values=produkt)
        conn.close()

    def add_product(self):
        nazwa = self.name_entry.get().strip()
        if not nazwa:
            messagebox.showerror("Błąd", "Nazwa produktu nie może być pusta!")
            return
        kategoria = self.kategoria_entry.get()
        if not kategoria:
            messagebox.showerror("Błąd", "Kategoria nie może być pusta!")
            return
        cena_str = self.prod_price_entry.get().strip()
        if not cena_str:
            messagebox.showerror("Błąd", "Cena nie może być pusta!")
            return
        try:
            cena = float(cena_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Błąd", "Cena musi być liczbą (np. 1200.50)!")
            return
        try:
            ilosc = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Ilość musi być liczbą całkowitą!")
            return
        lokalizacja_id = self.lokalizacja_entry.get()
        if lokalizacja_id:
            try:
                lokalizacja_id = int(lokalizacja_id)
            except ValueError:
                messagebox.showerror("Błąd", "Lokalizacja musi być liczbą!")
                return
        else:
            lokalizacja_id = None

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Sprawdź, czy produkt już istnieje (po nazwie)
        cursor.execute("SELECT ProduktID, Ilosc FROM Produkty WHERE Nazwa = ?", (nazwa,))
        result = cursor.fetchone()

        data_operacji = datetime.now().strftime("%Y-%m-%d")

        if result:
            # Produkt istnieje – dodaj operację i zaktualizuj ilość
            produkt_id, aktualna_ilosc = result

            # Dodaj operację "Dostawa"
            cursor.execute("""
                INSERT INTO OperacjeMagazynowe (ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi)
                VALUES (?, 'Dostawa', ?, ?, ?)
            """, (produkt_id, data_operacji, ilosc, f'Dostawa istniejącego produktu: {nazwa}'))

            # Zwiększ stan ilości w tabeli Produkty
            cursor.execute("""
                UPDATE Produkty SET Ilosc = Ilosc + ? WHERE ProduktID = ?
            """, (ilosc, produkt_id))

        else:
            # Produkt nie istnieje – dodaj go i utwórz operację
            cursor.execute("""
                INSERT INTO Produkty (Nazwa, Kategoria, Cena, Ilosc, LokalizacjaID) 
                VALUES (?, ?, ?, ?, ?)
            """, (nazwa, kategoria, cena, ilosc, lokalizacja_id))
            produkt_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO OperacjeMagazynowe (ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi)
                VALUES (?, 'Dostawa', ?, ?, ?)
            """, (produkt_id, data_operacji, ilosc, f'Dodano nowy produkt: {nazwa}'))

        conn.commit()
        conn.close()

        # Wyczyść pola wejściowe
        self.prod_price_entry.delete(0, "end")
        self.qty_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.kategoria_entry.delete(0, "end")
        self.lokalizacja_entry.delete(0, "end")

        self.load_products()
        messagebox.showinfo("Sukces", "Produkt dodany lub zaktualizowany jako dostawa!")
        self.load_products_for_order()
        self.load_operations()


#Frame operacje
    def create_operacje_tab(self):
        self.operacje_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.operacje_frame, text="Operacje Magazynowe")

        # LabelFrame z danymi (Treeview)
        self.oper_data_frame = ttk.LabelFrame(self.operacje_frame, text="Lista operacji magazynowych")
        self.oper_data_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        self.operacje_tree = ttk.Treeview(
            self.oper_data_frame,
            columns=("ID", "ProduktID", "Typ", "Data", "Ilość", "Uwagi"),
            show="headings"
        )
        for col in self.operacje_tree["columns"]:
            self.operacje_tree.heading(col, text=col)
            self.operacje_tree.column(col, anchor="center", width=120)
        self.operacje_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.oper_data_frame.grid_rowconfigure(0, weight=1)
        self.oper_data_frame.grid_columnconfigure(0, weight=1)

        # LabelFrame z filtrami
        self.oper_label_frame = ttk.LabelFrame(self.operacje_frame, text="Filtruj operacje")
        self.oper_label_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Przykładowe pola filtrujące (do rozbudowania)
        ttk.Label(self.oper_label_frame, text="Typ operacji:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.typ_operacji_combo = ttk.Combobox(self.oper_label_frame, state="readonly", values=["", "Zamówienie", "Dostawa", "Zwrot", "Wysyłka"])
        self.typ_operacji_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self.oper_label_frame, text="Data od:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.data_od_entry = ttk.Entry(self.oper_label_frame)
        self.data_od_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(self.oper_label_frame, text="Data do:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.data_do_entry = ttk.Entry(self.oper_label_frame)
        self.data_do_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        self.filter_button = ttk.Button(self.oper_label_frame, text="Filtruj", command=self.filter_operations)
        self.filter_button.grid(row=0, column=6, padx=10, pady=5)

        reset_button = ttk.Button(self.oper_label_frame, text="Resetuj", command=self.load_operations)
        reset_button.grid(row=0, column=7, padx=5, pady=5)

        # Rozciąganie
        self.operacje_frame.grid_rowconfigure(0, weight=1)
        self.operacje_frame.grid_columnconfigure(0, weight=1)

        self.load_operations()


    def filter_operations(self):
        typ_operacji = self.typ_operacji_combo.get().strip()
        data_od = self.data_od_entry.get().strip()
        data_do = self.data_do_entry.get().strip()

        query = "SELECT * FROM OperacjeMagazynowe WHERE 1=1"
        params = []

        # Filtr: typ operacji
        if typ_operacji:
            query += " AND TypOperacji = ?"
            params.append(typ_operacji)

        # Filtr: data od
        if data_od:
            try:
                datetime.strptime(data_od, "%Y-%m-%d")  # walidacja daty
                query += " AND DataOperacji >= ?"
                params.append(data_od)
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowy format daty (Data od). Użyj YYYY-MM-DD.")
                return

        # Filtr: data do
        if data_do:
            try:
                datetime.strptime(data_do, "%Y-%m-%d")  # walidacja daty
                query += " AND DataOperacji <= ?"
                params.append(data_do)
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowy format daty (Data do). Użyj YYYY-MM-DD.")
                return

        # Połączenie z bazą i wykonanie zapytania
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)
            results = cursor.fetchall()

            # Wyczyść drzewo i załaduj nowe dane
            for row in self.operacje_tree.get_children():
                self.operacje_tree.delete(row)

            for row in results:
                self.operacje_tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas filtrowania danych: {e}")
        finally:
            conn.close()


    def load_operations(self):
        for row in self.operacje_tree.get_children():
            self.operacje_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT OperacjaID, ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi
            FROM OperacjeMagazynowe
            ORDER BY OperacjaID DESC
        """)
        for op in cursor.fetchall():
            self.operacje_tree.insert("", "end", values=op)
        conn.close()


    #Frame zamów
    def create_zamow_tab(self): 
        self.zamowienia_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.zamowienia_frame, text="Zamów")

        # Ustaw skalowanie
        self.zamowienia_frame.grid_rowconfigure(0, weight=8)
        self.zamowienia_frame.grid_rowconfigure(1, weight=1)
        self.zamowienia_frame.grid_rowconfigure(2, weight=0)
        self.zamowienia_frame.grid_columnconfigure(0, weight=1)

        # Produkty
        self.products_frame = ttk.LabelFrame(self.zamowienia_frame, text="Produkty", padding=1)
        self.products_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.products_frame.grid_rowconfigure(0, weight=1)
        self.products_frame.grid_columnconfigure(0, weight=1)

        self.products_tree = ttk.Treeview(
            self.products_frame,
            columns=("ProduktID", "Nazwa", "Dostępna ilość", "Cena produktu"),
            show="headings"
        )
        for col in self.products_tree["columns"]:
            self.products_tree.heading(col, text=col)
        self.products_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.load_products_for_order()

        # Dane
        self.dane_frame = ttk.LabelFrame(self.zamowienia_frame, text="Dane", padding=5)
        self.dane_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Konfiguracja kolumn - 6 kolumn: label + entry dla każdego pola

        # ID produktu
        self.label_id = ttk.Label(self.dane_frame, text="ID produktu:")
        self.label_id.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.product_SelectedId = ttk.Entry(self.dane_frame, width=10)
        self.product_SelectedId.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Ilość
        self.label_ilosc = ttk.Label(self.dane_frame, text="Ilość:")
        self.label_ilosc.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.countInput = ttk.Entry(self.dane_frame, width=10)
        self.countInput.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Cena
        self.label_cena = ttk.Label(self.dane_frame, text="Cena:")
        self.label_cena.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(self.dane_frame, textvariable=self.price_var, width=12, state="readonly")
        self.price_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        

        # Przycisk
        order_button = ttk.Button(self.zamowienia_frame, text="Dodaj do koszyka", command=self.add_To_cart)
        order_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # Powiązania zdarzeń
        self.product_SelectedId.bind("<KeyRelease>", self.on_id_entry)
        self.countInput.bind("<KeyRelease>", lambda e: self.update_price())
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)


    def load_clients(self, combo):
        """Wypełnia combobox listą klientów"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT KlientID, Imie || ' ' || Nazwisko FROM Klienci")
        clients = cursor.fetchall()
        conn.close()

        # mapa nazwa -> id
        self.client_map = {nazwa: klient_id for klient_id, nazwa in clients}
        combo["values"] = list(self.client_map.keys())

    def load_products_for_order(self):
        """Ładuje produkty do tabeli w zakładce Zamówienia"""
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ProduktID, Nazwa, Ilosc, Cena FROM Produkty")
        for produkt_id, nazwa, ilosc, cena in cursor.fetchall():
            # Kolumna "Zamawiana ilość" zaczyna od zera
            self.products_tree.insert("", "end", values=(produkt_id, nazwa, ilosc, cena))
        conn.close()

#Metody koszyka
    def add_To_cart(self):
        produkt_id_str = self.product_SelectedId.get().strip()
        ilosc_str = self.countInput.get().strip()

        # 1. Priorytet: wpisane ID i ilość
        if produkt_id_str and ilosc_str:
            if not produkt_id_str.isdigit():
                messagebox.showerror("Błąd", "ID produktu musi być liczbą całkowitą.")
                return
            produkt_id = int(produkt_id_str)
            try:
                ilosc = float(ilosc_str)
            except ValueError:
                messagebox.showerror("Błąd", "Ilość musi być liczbą.")
                return

            # Pobierz dane produktu z bazy
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT Nazwa, Ilosc, Cena FROM Produkty WHERE ProduktID = ?", (produkt_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                messagebox.showerror("Błąd", f"Nie znaleziono produktu o ID {produkt_id}.")
                return

            produkt_nazwa, dostepna_ilosc, produkt_cena = row

            # Sprawdź, ile już jest w koszyku danego produktu
            ilosc_w_koszyku = 0
            for item in self.cart_items:
                if item["ProduktID"] == produkt_id:
                    ilosc_w_koszyku = item["Ilosc"]
                    break

            if ilosc <= 0:
                messagebox.showerror("Błąd", "Ilość musi być większa niż zero.")
                return

            if ilosc + ilosc_w_koszyku > dostepna_ilosc:
                messagebox.showerror("Błąd", "Brak wystarczającej ilości produktu po dodaniu do koszyka.")
                return

            # Jeśli produkt już jest w koszyku, aktualizuj ilość i cenę brutto
            for item in self.cart_items:
                if item["ProduktID"] == produkt_id:
                    item["Ilosc"] += ilosc
                    item["CenaBrutto"] = item["Ilosc"] * produkt_cena
                    messagebox.showinfo("Dodano do koszyka", f"Zaktualizowano koszyk: {produkt_nazwa} ({ilosc} szt.)")
                    self.refresh_cart_tree()
                    self.load_products_for_order()
                    return

            # Jeśli produktu nie ma, dodaj nowy wpis
            cena_brutto = ilosc * produkt_cena
            self.cart_items.append({
                "ProduktID": produkt_id,
                "Nazwa": produkt_nazwa,
                "Ilosc": ilosc,
                "Cena": produkt_cena,
                "CenaBrutto": cena_brutto
            })
            messagebox.showinfo("Dodano do koszyka", f"Dodano: {produkt_nazwa} ({ilosc} szt.)")
            self.refresh_cart_tree()
            self.load_products_for_order()
            self.load_operations()
            return

        # 2. Jeśli nie wpisano ID, ale jest zaznaczenie w tabeli
        selected = self.products_tree.selection()
        if selected:
            produkt_values = self.products_tree.item(selected[0], "values")
            produkt_id = int(produkt_values[0])
            produkt_nazwa = produkt_values[1]
            try:
                dostepna_ilosc = float(produkt_values[2])
                produkt_cena = float(produkt_values[3])
                ilosc = float(self.countInput.get())
            except ValueError:
                messagebox.showerror("Błąd", "Nieprawidłowe dane liczbowe.")
                return

            if ilosc <= 0:
                messagebox.showerror("Błąd", "Ilość musi być większa niż zero.")
                return

            # Sprawdź, ile już jest w koszyku danego produktu
            ilosc_w_koszyku = 0
            for item in self.cart_items:
                if item["ProduktID"] == produkt_id:
                    ilosc_w_koszyku = item["Ilosc"]
                    break

            if ilosc + ilosc_w_koszyku > dostepna_ilosc:
                messagebox.showerror("Błąd", "Brak wystarczającej ilości produktu po dodaniu do koszyka.")
                return

            # Jeśli produkt już jest w koszyku, aktualizuj ilość i cenę brutto
            for item in self.cart_items:
                if item["ProduktID"] == produkt_id:
                    item["Ilosc"] += ilosc
                    item["CenaBrutto"] = item["Ilosc"] * produkt_cena
                    self.refresh_cart_tree()
                    self.load_products_for_order()
                    return

            # Jeśli produktu nie ma, dodaj nowy wpis
            cena_brutto = ilosc * produkt_cena
            self.cart_items.append({
                "ProduktID": produkt_id,
                "Nazwa": produkt_nazwa,
                "Ilosc": ilosc,
                "Cena": produkt_cena,
                "CenaBrutto": cena_brutto
            })

            self.refresh_cart_tree()
            self.load_products_for_order()
            self.load_operations()
            return

        # 3. Jeśli nie wpisano ID i nie zaznaczono produktu
        messagebox.showerror("Błąd", "Wpisz ID produktu i ilość lub zaznacz produkt na liście.")
        return

    def reset_cart(self):
        self.cart_items.clear()
        self.refresh_cart_tree()

    def clear_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        self.cart_items.clear()
        self.cart_counter = 1

    def refresh_cart_tree(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        for index, item in enumerate(self.cart_items, start=1):
            self.cart_tree.insert("", "end", values=(
                index,
                item["ProduktID"],
                item["Nazwa"],
                item["Ilosc"],
                item["Cena"],
                item["CenaBrutto"]
            ))

        # Oblicz podsumowanie
        total_items = len(self.cart_items)
        total_price = sum(item["CenaBrutto"] for item in self.cart_items)

        self.total_items_label.config(text=f"Łączna liczba pozycji: {total_items}")
        self.total_price_label.config(text=f"Łączna kwota brutto: {total_price:.2f} zł")

            

    def create_cart_tab(self):
        self.cart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cart_frame, text="Koszyk")

        # Konfiguracja głównego układu
        self.cart_frame.grid_rowconfigure(0, weight=5)   # koszyk
        self.cart_frame.grid_rowconfigure(1, weight=1)   # podsumowanie
        self.cart_frame.grid_rowconfigure(2, weight=1)   # dane
        self.cart_frame.grid_columnconfigure(0, weight=1)

        # === Frame Koszyk ===
        self.cart_label = ttk.LabelFrame(self.cart_frame, text="Koszyk")
        self.cart_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.cart_label.grid_rowconfigure(0, weight=1)
        self.cart_label.grid_columnconfigure(0, weight=1)

        self.cart_tree = ttk.Treeview(
            self.cart_label,
            columns=("pozycja", "ID Produktu", "Nazwa", "ilość", "Cena jednost", "cena brutto"),
            show="headings"
        )
        for col in self.cart_tree["columns"]:
            self.cart_tree.heading(col, text=col)
        self.cart_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # === Frame Podsumowanie ===
        self.cart_summary_frame = ttk.LabelFrame(self.cart_frame, text="Podsumowanie koszyka")
        self.cart_summary_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.cart_summary_frame.grid_columnconfigure(0, weight=1)  # To wypycha resztę na prawo
        self.cart_summary_frame.grid_columnconfigure(1, weight=0)
        self.cart_summary_frame.grid_columnconfigure(2, weight=0)

        self.total_items_label = ttk.Label(self.cart_summary_frame, text="Łączna liczba pozycji: 0")
        self.total_items_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        self.total_price_label = ttk.Label(self.cart_summary_frame, text="Łączna kwota brutto: 0.00 zł")
        self.total_price_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        # === Frame Dane ===
        self.cart_data_frame = ttk.LabelFrame(self.cart_frame, text="Dane")
        self.cart_data_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(self.cart_data_frame, text="Nazwisko:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.client_combo = ttk.Combobox(self.cart_data_frame, state="readonly")
        self.client_combo.grid(row=0, column=1, padx=0, pady=5, sticky="ew")
        self.load_clients(combo=self.client_combo)

        refresh_button = ttk.Button(self.cart_data_frame, text="Odśwież koszyk", command=self.refresh_cart_tree)
        refresh_button.grid(row=0, column=2, padx=10, pady=5, sticky="s")

        zapisz_button = ttk.Button(self.cart_data_frame, text="Zapisz zamowienie", command=self.add_zamowienie)
        zapisz_button.grid(row=0, column=3, padx=5, pady=5, sticky="s")

        reset_button = ttk.Button(self.cart_data_frame, text="Reset", command=self.reset_cart)
        reset_button.grid(row=0, column=4, padx=5, pady=5, sticky="s")


    def add_zamowienie(self):
        klient_name = self.client_combo.get()
        if not klient_name or klient_name not in self.client_map:
            messagebox.showerror("Błąd", "Wybierz klienta.")
            return

        if not self.cart_tree.get_children():
            messagebox.showerror("Błąd", "Koszyk jest pusty.")
            return

        klient_id = self.client_map[klient_name]
        data = datetime.now().strftime("%Y-%m-%d")

        # Sumujemy kolumnę 'CenaBrutto' w cart_tree
        laczna_kwota = 0
        for item_id in self.cart_tree.get_children():
            values = self.cart_tree.item(item_id)["values"]
            # Zakładam, że kolumna "CenaBrutto" jest na 6 pozycji (indeks 5)
            try:
                cena_brutto = float(values[5])
            except (ValueError, IndexError):
                cena_brutto = 0
            laczna_kwota += cena_brutto

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            # Dodaj wpis do Zamowienia
            cursor.execute("""
                INSERT INTO Zamowienia (KlientID, DataZamowienia, Kwota)
                VALUES (?, ?, ?)
            """, (klient_id, data, laczna_kwota))
            zamowienie_id = cursor.lastrowid

            # Dodaj wpisy do PozycjeZamowienia na podstawie danych z cart_tree
            for item_id in self.cart_tree.get_children():
                values = self.cart_tree.item(item_id)["values"]
                # Przypuszczalnie masz kolumny:
                # pozycja (0), ID Produktu (1), Nazwa (2), ilość (3), Cena jednost (4), cena brutto (5)
                produkt_id = int(values[1])
                ilosc = float(values[3])
                cena = float(values[4])
                cena_brutto = float(values[5])

                cursor.execute("""
                    INSERT INTO PozycjeZamowienia (ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto)
                    VALUES (?, ?, ?, ?, ?)
                """, (zamowienie_id, produkt_id, ilosc, cena, cena_brutto))

                # Zmniejsz ilość produktu w magazynie
                cursor.execute("""
                    UPDATE Produkty SET Ilosc = Ilosc - ?
                    WHERE ProduktID = ?
                """, (ilosc, produkt_id))

                # Dodaj operację magazynową
                cursor.execute("""
                    INSERT INTO OperacjeMagazynowe (ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi)
                    VALUES (?, 'Zamówienie', ?, ?, ?)
                """, (produkt_id, data, ilosc, f"Zamówienie klienta {klient_name}"))

            conn.commit()
            messagebox.showinfo("Sukces", "Zamówienie zrealizowane!")
            self.clear_cart()
            self.load_products()
            self.load_products_for_order()
            self.load_orders()
            self.load_pozycje()
            self.load_operations()
            self.LoadZamowienieCombo()
            self.refresh_cart_tree()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Błąd", f"Błąd podczas zapisu: {e}")
        finally:
            conn.close()
    

#Frame zamówienia
    def create_orders_tab(self):
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Zamowienia")

        # Orders label
        self.orders_label = ttk.LabelFrame(self.orders_frame, text="Lista")
        self.orders_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.orders_frame.grid_rowconfigure(0, weight=5)
        self.orders_frame.grid_columnconfigure(0, weight=1)  # Umożliwia rozciąganie w poziomie

        # Treeview
        self.orders_tree = ttk.Treeview(
            self.orders_label,
            columns=("ZamowienieID", "KlientID", "DataZamowienia", "Kwota"),
            show="headings"
        )
        for col in self.orders_tree["columns"]:
            self.orders_tree.heading(col, text=col)
        self.orders_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Treeview rozciąganie
        self.orders_label.grid_rowconfigure(0, weight=1)
        self.orders_label.grid_columnconfigure(0, weight=1)

        # Przycisk testowy
        self.test_button = ttk.Button(self.orders_frame, text="Usun zamówienie", command=self.delete_order)
        self.test_button.grid(row=2, column=0, padx=5, pady=5, sticky="n")

        # Filtry label
        self.filtry_label = ttk.LabelFrame(self.orders_frame, text="Filtry")
        self.filtry_label.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.orders_frame.grid_rowconfigure(1, weight=1)

        # Combobox z klientami
        ttk.Label(self.filtry_label, text="ID: ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.orders_client_combo = ttk.Combobox(self.filtry_label, state="readonly")
        self.orders_client_combo.grid(row=0, column=1, padx=0, pady=5, sticky="w")
        self.load_clients(combo=self.orders_client_combo)
        self.load_orders()

        # Przyciski filtrów
        self.filtruj_button = ttk.Button(self.filtry_label, text="Filtruj", command=self.FiltrujKlienta)
        self.filtruj_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.reset_button = ttk.Button(self.filtry_label, text="Reset", command=self.load_orders)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")


    def load_orders(self):
        """Ładuje produkty do tabeli w zakładce Zamówienia"""
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ZamowienieID, KlientID, DataZamowienia, Kwota FROM Zamowienia ORDER BY ZamowienieID DESC")
        for ZamowienieID, KlientID, DataZamowienia, Kwota in cursor.fetchall():
            # Kolumna "Zamawiana ilość" zaczyna od zera
            self.orders_tree.insert("", "end", values=(ZamowienieID, KlientID, DataZamowienia, Kwota))
        conn.close()

    def delete_order(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Błąd", "Nie wybrano żadnej pozycji")
            return

        order_id = self.orders_tree.item(selected_item, "values")[0]

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Pobierz pozycje zamówienia przed usunięciem
            cursor.execute("""
                SELECT ProduktID, Ilosc 
                FROM PozycjeZamowienia 
                WHERE ZamowienieID = ?
            """, (order_id,))
            pozycje = cursor.fetchall()

            data_operacji = datetime.now().strftime("%Y-%m-%d");

            for produkt_id, ilosc in pozycje:
                # Zwiększ stan magazynowy produktu
                cursor.execute("""
                    UPDATE Produkty 
                    SET Ilosc = Ilosc + ? 
                    WHERE ProduktID = ?
                """, (ilosc, produkt_id))

                # Dodaj operację magazynową "Zwrot"
                cursor.execute("""
                    INSERT INTO OperacjeMagazynowe (ProduktID, TypOperacji, DataOperacji, Ilosc, Uwagi)
                    VALUES (?, 'Zwrot', ?, ?, ?)
                """, (produkt_id, data_operacji, ilosc, f"Zwrot z usuniętego zamówienia ID {order_id}"))

            # Usuń pozycje zamówienia
            cursor.execute("DELETE FROM PozycjeZamowienia WHERE ZamowienieID = ?", (order_id,))

            # Usuń samo zamówienie
            cursor.execute("DELETE FROM Zamowienia WHERE ZamowienieID = ?", (order_id,))

            conn.commit()
            messagebox.showinfo("INFO", f"Zamówienie (ID: {order_id}) usunięte, produkty zwrócone do magazynu.")
        
        except sqlite3.Error as e:
            messagebox.showerror("Błąd", f"Błąd podczas usuwania: {e}")
        
        finally:
            conn.close()

        self.load_orders()
        self.load_pozycje()
        self.load_products()
        self.load_operations()
        self.load_products_for_order()


    def FiltrujKlienta(self):
        klient_name=self.orders_client_combo.get()
        if not klient_name or klient_name not in self.client_map:
            messagebox.showerror("Błąd", "Wybierz klienta.")
            return
        klient_id=self.client_map[klient_name]

        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT ZamowienieID, KlientID, DataZamowienia, Kwota FROM Zamowienia WHERE KlientID={klient_id}")
        for ZamowienieID, KlientID, DataZamowienia, Kwota in cursor.fetchall():
            # Kolumna "Zamawiana ilość" zaczyna od zera
            self.orders_tree.insert("", "end", values=(ZamowienieID, KlientID, DataZamowienia, Kwota))
        conn.close()

#Frame pozycja
    def create_PozycjeZam_tab(self):
        self.pozycje_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pozycje_frame, text="PozycjeZamowien")

        # LabelFrame na Treeview
        self.pozycja_label = ttk.LabelFrame(self.pozycje_frame, text="Pozycje")
        self.pozycja_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.pozycje_frame.grid_rowconfigure(0, weight=5)
        self.pozycje_frame.grid_columnconfigure(0, weight=1)

        # Treeview
        self.pozycje_tree = ttk.Treeview(
            self.pozycja_label,
            columns=("PozycjaID", "ZamowienieID", "ProduktID", "Ilosc", "Cena", "CenaBrutto"),
            show="headings"
        )
        for col in self.pozycje_tree["columns"]:
            self.pozycje_tree.heading(col, text=col)

        self.pozycje_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Rozciąganie Treeview w LabelFrame
        self.pozycja_label.grid_rowconfigure(0, weight=1)
        self.pozycja_label.grid_columnconfigure(0, weight=1)

        # Wczytanie danych
        self.load_pozycje()

        # LabelFrame z filtrami
        self.poz_filtry_lab = ttk.LabelFrame(self.pozycje_frame, text="Filtry")
        self.poz_filtry_lab.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.pozycje_frame.grid_rowconfigure(1, weight=1)

        # Combobox z zamówieniami
        ttk.Label(self.poz_filtry_lab, text="ID zamówienia: ").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.poz_id_combo = ttk.Combobox(self.poz_filtry_lab)
        self.poz_id_combo.grid(row=0, column=1, padx=0, pady=5, sticky="w")
        self.LoadZamowienieCombo()

        # Przyciski filtrów
        self.filtruj_button = ttk.Button(self.poz_filtry_lab, text="Filtruj", command=self.FiltrujZamID)
        self.filtruj_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.reset_button = ttk.Button(self.poz_filtry_lab, text="Reset", command=self.load_pozycje)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.odswiez_button = ttk.Button(self.poz_filtry_lab, text="Odśwież", command=self.LoadZamowienieCombo)
        self.odswiez_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")



    
    def load_pozycje(self):
        for row in self.pozycje_tree.get_children():
            self.pozycje_tree.delete(row)

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()
        cursor.execute("SELECT PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto from PozycjeZamowienia ORDER BY PozycjaID DESC")
        for PozID, ZamID, ProID, Il, Cen, CenB in cursor.fetchall():
            self.pozycje_tree.insert("", "end", values=(PozID, ZamID, ProID, Il, Cen, CenB))
        conn.close()

    def LoadZamowienieCombo(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ZamowienieID FROM Zamowienia")
        Zamowienia = cursor.fetchall()
        conn.close()

        self.zam_map = [zid[0] for zid in Zamowienia]
        self.poz_id_combo["values"] = self.zam_map

    def FiltrujZamID(self):
        zam_id = self.poz_id_combo.get()

        try:
            zam_id = int(zam_id)
        except ValueError:
            messagebox.showerror("Błąd", "Wybierz poprawne ID.")
            return

        if zam_id not in self.zam_map:
            messagebox.showerror("Błąd", "Wybierz poprawne ID.")
            return

        for row in self.pozycje_tree.get_children():
            self.pozycje_tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto FROM PozycjeZamowienia WHERE ZamowienieID=?", (zam_id,))
        for PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto in cursor.fetchall():
            self.pozycje_tree.insert("", "end", values=(PozycjaID, ZamowienieID, ProduktID, Ilosc, Cena, CenaBrutto))
        conn.close()



#Frame analiza
    def create_analiza_tab(self): 
        self.analiza_frame = ttk.Frame(self.notebook) 
        self.notebook.add(self.analiza_frame, text="Analiza") 

        # Główny podział na sekcje
        self.analiza_frame.grid_rowconfigure(0, weight=1)
        self.analiza_frame.grid_rowconfigure(1, weight=1)
        self.analiza_frame.grid_columnconfigure(0, weight=1)

        # === SEKCJA ANALIZ PODSTAWOWYCH ===
        self.podstawowe_frame = ttk.LabelFrame(self.analiza_frame, text="Analizy Podstawowe")
        self.podstawowe_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.podstawowe_frame.grid_columnconfigure(0, weight=1)

        # Filtry główne
        filtry_frame = ttk.Frame(self.podstawowe_frame)
        filtry_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Typ analizy
        ttk.Label(filtry_frame, text="Typ analizy:").grid(row=0, column=0, padx=5, sticky="w")
        self.analysis_type = tk.StringVar()
        self.analysis_selector = ttk.Combobox(
            filtry_frame, 
            textvariable=self.analysis_type, 
            values=["Typ operacji", "Miesiąc i typ operacji", "Ranking produktów", 
                   "Przychody w czasie", "Stan magazynu"]
        )
        self.analysis_selector.current(0)
        self.analysis_selector.grid(row=0, column=1, padx=5, sticky="w")
        self.analysis_selector.bind("<<ComboboxSelected>>", lambda e: self.run_analysis())

        # Filtry dat
        ttk.Label(filtry_frame, text="Data od:").grid(row=0, column=2, padx=5, sticky="w")
        self.date_from_entry = ttk.Entry(filtry_frame, width=12)
        self.date_from_entry.grid(row=0, column=3, padx=5, sticky="w")

        ttk.Label(filtry_frame, text="do:").grid(row=0, column=4, padx=5, sticky="w")
        self.date_to_entry = ttk.Entry(filtry_frame, width=12)
        self.date_to_entry.grid(row=0, column=5, padx=5, sticky="w")

        # Filtry dodatkowe
        filtry_frame2 = ttk.Frame(self.podstawowe_frame)
        filtry_frame2.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Filtr produktu
        ttk.Label(filtry_frame2, text="Produkt:").grid(row=0, column=0, padx=5, sticky="w")
        self.produkt_filter = ttk.Combobox(filtry_frame2, state="readonly")
        self.produkt_filter.grid(row=0, column=1, padx=5, sticky="w")
        self.load_produkty_filter()

        # Filtr typu operacji
        ttk.Label(filtry_frame2, text="Typ operacji:").grid(row=0, column=2, padx=5, sticky="w")
        self.operacja_filter = ttk.Combobox(filtry_frame2, state="readonly", 
                                          values=["Wszystkie", "Dostawa", "Zamówienie", "Wysyłka", "Zwrot"])
        self.operacja_filter.current(0)
        self.operacja_filter.grid(row=0, column=3, padx=5, sticky="w")

        # Filtr okresu
        ttk.Label(filtry_frame2, text="Okres:").grid(row=0, column=4, padx=5, sticky="w")
        self.okres_filter = ttk.Combobox(filtry_frame2, state="readonly", 
                                       values=["Miesięcznie", "Kwartalnie", "Rocznie"])
        self.okres_filter.current(0)
        self.okres_filter.grid(row=0, column=5, padx=5, sticky="w")

        # Tabela wyników
        self.analiza_tree = ttk.Treeview(self.podstawowe_frame, show="headings") 
        self.analiza_tree.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.podstawowe_frame.grid_rowconfigure(2, weight=1)

        # Przyciski
        buttons_frame = ttk.Frame(self.podstawowe_frame)
        buttons_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(buttons_frame, text="Wykonaj analizę", command=self.run_analysis).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Wykres słupkowy", command=lambda: self.show_chart("bar")).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Wykres kołowy", command=lambda: self.show_chart("pie")).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Wykres liniowy", command=lambda: self.show_chart("line")).pack(side="left", padx=5)

        # === SEKCJA RAPORTÓW Z BAZY ===
        self.raporty_frame = ttk.LabelFrame(self.analiza_frame, text="Raporty Szczegółowe")
        self.raporty_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.raporty_frame.grid_columnconfigure(0, weight=1)

        # Przyciski raportów
        raporty_buttons = ttk.Frame(self.raporty_frame)
        raporty_buttons.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Button(raporty_buttons, text="Raport Zgodności Zamówień", 
                  command=self.raport_zgodnosc_zamowien).pack(side="left", padx=5)
        ttk.Button(raporty_buttons, text="Raport Przychodów", 
                  command=self.raport_przychodow).pack(side="left", padx=5)
        ttk.Button(raporty_buttons, text="Analiza Trendów", 
                  command=self.analiza_trendow).pack(side="left", padx=5)
        ttk.Button(raporty_buttons, text="Stan Magazynu", 
                  command=self.raport_stanu_magazynu).pack(side="left", padx=5)

        # Filtry dat dla raportów
        raporty_filters = ttk.Frame(self.raporty_frame)
        raporty_filters.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(raporty_filters, text="Data od:").pack(side="left", padx=5)
        self.report_date_from = ttk.Entry(raporty_filters, width=12)
        self.report_date_from.pack(side="left", padx=5)
        
        ttk.Label(raporty_filters, text="do:").pack(side="left", padx=5)
        self.report_date_to = ttk.Entry(raporty_filters, width=12)
        self.report_date_to.pack(side="left", padx=5)

        # Przyciski wykresów dla raportów
        raporty_chart_buttons = ttk.Frame(self.raporty_frame)
        raporty_chart_buttons.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        ttk.Button(raporty_chart_buttons, text="Wykres słupkowy", 
                  command=lambda: self.show_report_chart("bar")).pack(side="left", padx=5)
        ttk.Button(raporty_chart_buttons, text="Wykres kołowy", 
                  command=lambda: self.show_report_chart("pie")).pack(side="left", padx=5)
        ttk.Button(raporty_chart_buttons, text="Wykres liniowy", 
                  command=lambda: self.show_report_chart("line")).pack(side="left", padx=5)

        # Tabela raportów
        self.raporty_tree = ttk.Treeview(self.raporty_frame, show="headings")
        self.raporty_tree.grid(row=1, column=0, padx=5, pady=5, sticky="nsew") 
        self.raporty_frame.grid_rowconfigure(1, weight=1)

    def load_produkty_filter(self):
        """Ładuje produkty do combobox filtru"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Nazwa FROM Produkty ORDER BY Nazwa")
        produkty = ["Wszystkie"] + [row[0] for row in cursor.fetchall()]
        conn.close()
        
        self.produkt_filter["values"] = produkty
        self.produkt_filter.current(0)

    def run_analysis(self): 
        # Czyszczenie poprzednich wyników
        for row in self.analiza_tree.get_children(): 
            self.analiza_tree.delete(row) 

        # Odczyt filtrów
        date_from = self.date_from_entry.get().strip() or "0001-01-01"
        date_to = self.date_to_entry.get().strip() or "9999-12-31"
        produkt_filter = self.produkt_filter.get()
        operacja_filter = self.operacja_filter.get()
        okres = self.okres_filter.get()

        # Połączenie z bazą danych
        conn = sqlite3.connect(DB_PATH) 
        cursor = conn.cursor() 

        selected_analysis = self.analysis_type.get()

        # Budowanie warunków WHERE
        where_conditions = ["date(o.DataOperacji) BETWEEN ? AND ?"]
        params = [date_from, date_to]

        if operacja_filter != "Wszystkie":
            where_conditions.append("o.TypOperacji = ?")
            params.append(operacja_filter)

        if produkt_filter != "Wszystkie":
            where_conditions.append("p.Nazwa = ?")
            params.append(produkt_filter)

        where_clause = " AND ".join(where_conditions)

        if selected_analysis == "Typ operacji":
            # Dodaj grupowanie według okresu jeśli wybrano
            if okres == "Miesięcznie":
                group_by = "strftime('%Y-%m', o.DataOperacji), o.TypOperacji"
                select_period = "strftime('%Y-%m', o.DataOperacji) AS Okres, "
                columns = ("Okres", "Typ operacji", "Liczba operacji", "Suma ilości")
                order_by = "Okres DESC, LiczbaOperacji DESC"
            elif okres == "Kwartalnie":
                group_by = "strftime('%Y', o.DataOperacji) || '-Q' || ((strftime('%m', o.DataOperacji) - 1) / 3 + 1), o.TypOperacji"
                select_period = "strftime('%Y', o.DataOperacji) || '-Q' || ((strftime('%m', o.DataOperacji) - 1) / 3 + 1) AS Okres, "
                columns = ("Okres", "Typ operacji", "Liczba operacji", "Suma ilości")
                order_by = "Okres DESC, LiczbaOperacji DESC"
            elif okres == "Rocznie":
                group_by = "strftime('%Y', o.DataOperacji), o.TypOperacji"
                select_period = "strftime('%Y', o.DataOperacji) AS Okres, "
                columns = ("Okres", "Typ operacji", "Liczba operacji", "Suma ilości")
                order_by = "Okres DESC, LiczbaOperacji DESC"
            else:
                # Bez podziału na okres
                group_by = "o.TypOperacji"
                select_period = ""
                columns = ("Typ operacji", "Liczba operacji", "Suma ilości")
                order_by = "LiczbaOperacji DESC"
                
            query = f"""
                SELECT {select_period}o.TypOperacji, COUNT(*) AS LiczbaOperacji, SUM(o.Ilosc) AS SumaIlosci 
                FROM OperacjeMagazynowe o 
                LEFT JOIN Produkty p ON o.ProduktID = p.ProduktID
                WHERE {where_clause}
                GROUP BY {group_by}
                ORDER BY {order_by}
            """

        elif selected_analysis == "Miesiąc i typ operacji":
            date_format = "'%Y-%m'" if okres == "Miesięcznie" else "'%Y-Q' || ((strftime('%m', o.DataOperacji) - 1) / 3 + 1)" if okres == "Kwartalnie" else "'%Y'"
            query = f"""
                SELECT strftime({date_format}, o.DataOperacji) AS Okres, o.TypOperacji, 
                    COUNT(*) AS LiczbaOperacji, SUM(o.Ilosc) AS SumaIlosci 
                FROM OperacjeMagazynowe o 
                LEFT JOIN Produkty p ON o.ProduktID = p.ProduktID
                WHERE {where_clause}
                GROUP BY Okres, o.TypOperacji 
                ORDER BY Okres DESC
            """
            columns = ("Okres", "Typ operacji", "Liczba operacji", "Suma ilości")

        elif selected_analysis == "Ranking produktów":
            # Dodaj grupowanie według okresu jeśli wybrano
            if okres == "Miesięcznie":
                group_by = "strftime('%Y-%m', o.DataOperacji), p.Nazwa"
                select_period = "strftime('%Y-%m', o.DataOperacji) AS Okres, "
                columns = ("Okres", "Nazwa produktu", "Liczba operacji", "Suma sprzedanych sztuk")
                order_by = "Okres DESC, SumaIlosci DESC"
            elif okres == "Kwartalnie":
                group_by = "strftime('%Y', o.DataOperacji) || '-Q' || ((strftime('%m', o.DataOperacji) - 1) / 3 + 1), p.Nazwa"
                select_period = "strftime('%Y', o.DataOperacji) || '-Q' || ((strftime('%m', o.DataOperacji) - 1) / 3 + 1) AS Okres, "
                columns = ("Okres", "Nazwa produktu", "Liczba operacji", "Suma sprzedanych sztuk")
                order_by = "Okres DESC, SumaIlosci DESC"
            elif okres == "Rocznie":
                group_by = "strftime('%Y', o.DataOperacji), p.Nazwa"
                select_period = "strftime('%Y', o.DataOperacji) AS Okres, "
                columns = ("Okres", "Nazwa produktu", "Liczba operacji", "Suma sprzedanych sztuk")
                order_by = "Okres DESC, SumaIlosci DESC"
            else:
                # Bez podziału na okres
                group_by = "p.Nazwa"
                select_period = ""
                columns = ("Nazwa produktu", "Liczba operacji", "Suma sprzedanych sztuk")
                order_by = "SumaIlosci DESC"
                
            query = f"""
                SELECT {select_period}p.Nazwa, COUNT(o.OperacjaID) AS LiczbaOperacji, SUM(o.Ilosc) AS SumaIlosci 
                FROM OperacjeMagazynowe o 
                JOIN Produkty p ON o.ProduktID = p.ProduktID 
                WHERE o.TypOperacji = 'Zamówienie' AND {where_clause}
                GROUP BY {group_by}
                ORDER BY {order_by}
            """

        elif selected_analysis == "Przychody w czasie":
            if okres == "Miesięcznie":
                date_format = "strftime('%Y-%m', o.DataOperacji)"
                group_by = "strftime('%Y-%m', o.DataOperacji)"
            elif okres == "Kwartalnie":
                date_format = "strftime('%Y', o.DataOperacji) || '-Q' || CAST(((CAST(strftime('%m', o.DataOperacji) AS INTEGER) - 1) / 3 + 1) AS INTEGER)"
                group_by = "strftime('%Y', o.DataOperacji), ((CAST(strftime('%m', o.DataOperacji) AS INTEGER) - 1) / 3 + 1)"
            else:  # Rocznie
                date_format = "strftime('%Y', o.DataOperacji)"
                group_by = "strftime('%Y', o.DataOperacji)"
                
            query = f"""
                SELECT {date_format} AS Okres, 
                    SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN p.Cena * o.Ilosc ELSE 0 END) AS Przychody,
                    COUNT(CASE WHEN o.TypOperacji = 'Zamówienie' THEN 1 END) AS LiczbaZamowien
                FROM OperacjeMagazynowe o 
                JOIN Produkty p ON o.ProduktID = p.ProduktID 
                WHERE {where_clause}
                GROUP BY {group_by}
                ORDER BY Okres DESC
            """
            columns = ("Okres", "Przychody (zł)", "Liczba zamówień")

        elif selected_analysis == "Analiza zyskowności":
            query = f"""
                SELECT 
                    p.Nazwa,
                    SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN p.Cena * o.Ilosc ELSE 0 END) as Przychody,
                    SUM(CASE WHEN o.TypOperacji = 'Zwrot' THEN p.Cena * o.Ilosc ELSE 0 END) as Zwroty,
                    SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN p.Cena * o.Ilosc ELSE 0 END) - 
                    SUM(CASE WHEN o.TypOperacji = 'Zwrot' THEN p.Cena * o.Ilosc ELSE 0 END) as ZyskNetto,
                    COUNT(CASE WHEN o.TypOperacji = 'Zamówienie' THEN 1 END) as LiczbaSprzedaz
                FROM OperacjeMagazynowe o 
                JOIN Produkty p ON o.ProduktID = p.ProduktID 
                WHERE o.TypOperacji IN ('Zamówienie', 'Zwrot') AND {where_clause}
                GROUP BY p.Nazwa 
                HAVING ZyskNetto > 0
                ORDER BY ZyskNetto DESC
            """
            columns = ("Nazwa produktu", "Przychody (zł)", "Zwroty (zł)", "Zysk netto (zł)", "Sprzedaży")

        elif selected_analysis == "Stan magazynu":
            query = f"""
                SELECT p.Nazwa, p.Kategoria, p.Ilosc, p.Cena, (p.Ilosc * p.Cena) AS WartoscMagazynowa
                FROM Produkty p
                WHERE p.Nazwa LIKE '%{produkt_filter if produkt_filter != "Wszystkie" else ""}%'
                ORDER BY WartoscMagazynowa DESC
            """
            params = []  # Reset params dla tego zapytania
            columns = ("Nazwa produktu", "Kategoria", "Ilość", "Cena", "Wartość magazynowa")

        else:
            conn.close()
            return

        # Ustawienie kolumn tabeli
        self.analiza_tree["columns"] = columns
        for col in columns:
            self.analiza_tree.heading(col, text=col)
            self.analiza_tree.column(col, width=120)

        # Wykonanie zapytania i wypełnienie tabeli
        try:
            cursor.execute(query, params)
            for row in cursor.fetchall(): 
                formatted_row = []
                for i, value in enumerate(row):
                    if columns[i].endswith("(zł)") and value:
                        formatted_row.append(f"{value:.2f}")
                    else:
                        formatted_row.append(value)
                self.analiza_tree.insert("", "end", values=formatted_row)
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas analizy: {e}")

        conn.close()

    def show_chart(self, chart_type="bar"):
        """Tworzy wykres w osobnym oknie na podstawie aktualnie wybranych danych"""
        # Sprawdź czy są dane w tabeli
        if not self.analiza_tree.get_children():
            messagebox.showwarning("Brak danych", "Najpierw wykonaj analizę!")
            return

        # Pobierz dane z aktualnej analizy
        columns = self.analiza_tree["columns"]
        data = []
        for item in self.analiza_tree.get_children():
            values = self.analiza_tree.item(item, "values")
            data.append(values)

        if not data:
            return

        # Utwórz nowe okno z większym rozmiarem
        chart_window = tk.Toplevel(self)
        chart_window.title(f"Wykres - {self.analysis_type.get()}")
        chart_window.geometry("1200x800")
        chart_window.configure(bg="#f5f7fa")
        
        # Dodaj zmienne do zarządzania stronnicowaniem
        self.current_page = 0
        self.items_per_page = 20  # Maksymalnie 20 elementów na stronę
        self.chart_data = data
        self.chart_columns = columns
        self.chart_type_current = chart_type
        self.chart_window_ref = chart_window

        # Przygotuj dane do wykresu
        selected_analysis = self.analysis_type.get()
        
        if selected_analysis == "Typ operacji":
            # Sprawdź czy mamy podział na okresy czy nie
            if len(columns) == 4:  # Mamy kolumnę Okres
                if chart_type == "line":
                    # Dla wykresu liniowego - pokaż trendy najpopularniejszego typu operacji
                    type_counts = {}
                    for row in data:
                        op_type = row[1]  # TypOperacji
                        count = int(row[2])  # LiczbaOperacji
                        if op_type in type_counts:
                            type_counts[op_type] += count
                        else:
                            type_counts[op_type] = count
                    
                    main_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "Zamówienie"
                    filtered_data = [(row[0], int(row[2])) for row in data if row[1] == main_type]
                    filtered_data.sort(key=lambda x: x[0])
                    
                    labels = [item[0] for item in filtered_data]
                    values = [item[1] for item in filtered_data]
                    title = f"Trend operacji '{main_type}' w czasie"
                    ylabel = "Liczba operacji"
                elif chart_type == "pie":
                    # Dla wykresu kołowego - agreguj według typu operacji
                    type_totals = {}
                    for row in data:
                        op_type = row[1]  # TypOperacji
                        count = int(row[2])  # LiczbaOperacji
                        if op_type in type_totals:
                            type_totals[op_type] += count
                        else:
                            type_totals[op_type] = count
                    
                    labels = list(type_totals.keys())
                    values = list(type_totals.values())
                    title = "Udział typów operacji w wybranym okresie"
                    ylabel = "Liczba operacji"
                else:  # bar chart
                    limited_data = data[:15]
                    labels = [f"{row[0]}\n{row[1][:8]}" for row in limited_data]
                    values = [int(row[2]) for row in limited_data]
                    title = f"Operacje według okresów i typów (ostatnie {len(limited_data)} wpisów)"
                    ylabel = "Liczba operacji"
            else:  # Bez podziału na okresy
                limited_data = data[:8]  # Maksymalnie 8 typów operacji
                labels = [row[0] for row in limited_data]
                values = [int(row[1]) for row in limited_data]  # Liczba operacji
                title = "Liczba operacji wg typu"
                ylabel = "Liczba operacji"
            
        elif selected_analysis == "Ranking produktów":
            # Sprawdź czy mamy podział na okresy czy nie
            if len(columns) == 4:  # Mamy kolumnę Okres
                if chart_type == "pie":
                    # Dla wykresu kołowego - agreguj według produktów
                    product_totals = {}
                    for row in data:
                        product = row[1]  # Nazwa produktu
                        count = int(row[3])  # Suma sprzedanych sztuk
                        if product in product_totals:
                            product_totals[product] += count
                        else:
                            product_totals[product] = count
                    
                    # Top 8 produktów + reszta
                    sorted_products = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)
                    top_products = sorted_products[:8]
                    if len(sorted_products) > 8:
                        rest_sum = sum(item[1] for item in sorted_products[8:])
                        labels = [item[0][:12] + "..." if len(item[0]) > 12 else item[0] for item in top_products] + ["Pozostałe"]
                        values = [item[1] for item in top_products] + [rest_sum]
                    else:
                        labels = [item[0][:12] + "..." if len(item[0]) > 12 else item[0] for item in top_products]
                        values = [item[1] for item in top_products]
                    title = "Udział produktów w sprzedaży według okresów (top 8)"
                    ylabel = "Sprzedane sztuki"
                elif chart_type == "line":
                    # Dla wykresu liniowego - pokaż trendy najpopularniejszego produktu
                    product_counts = {}
                    for row in data:
                        product = row[1]  # Nazwa produktu
                        count = int(row[3])  # Suma sprzedanych sztuk
                        if product in product_counts:
                            product_counts[product] += count
                        else:
                            product_counts[product] = count
                    
                    main_product = max(product_counts.items(), key=lambda x: x[1])[0] if product_counts else "Laptop"
                    filtered_data = [(row[0], int(row[3])) for row in data if row[1] == main_product]
                    filtered_data.sort(key=lambda x: x[0])
                    
                    labels = [item[0] for item in filtered_data]
                    values = [item[1] for item in filtered_data]
                    title = f"Trend sprzedaży '{main_product[:20]}...' w czasie"
                    ylabel = "Sprzedane sztuki"
                else:  # bar chart
                    labels = [f"{row[0]}\n{row[1][:10]}..." if len(row[1]) > 10 else f"{row[0]}\n{row[1]}" for row in data]
                    values = [int(row[3]) for row in data]  # Suma sprzedanych sztuk
                    title = f"Ranking produktów według okresów ({len(data)} pozycji)"
                    ylabel = "Sprzedane sztuki"
            else:  # Bez podziału na okresy
                if chart_type == "pie":
                    # Dla wykresu kołowego - pokaż top 8 + reszta
                    top_data = data[:8]
                    if len(data) > 8:
                        rest_sum = sum(int(row[2]) for row in data[8:])
                        labels = [row[0][:12] + "..." if len(row[0]) > 12 else row[0] for row in top_data] + ["Pozostałe"]
                        values = [int(row[2]) for row in top_data] + [rest_sum]
                    else:
                        labels = [row[0][:12] + "..." if len(row[0]) > 12 else row[0] for row in top_data]
                        values = [int(row[2]) for row in top_data]
                    title = "Udział produktów w sprzedaży (top 8)"
                    ylabel = "Sprzedane sztuki"
                else:
                    # Dla innych wykresów - wszystkie produkty z krótkimi nazwami
                    labels = [row[0][:10] + "..." if len(row[0]) > 10 else row[0] for row in data]
                    values = [int(row[2]) for row in data]
                    title = f"Ranking produktów ({len(data)} pozycji)"
                    ylabel = "Sprzedane sztuki"
            
        elif selected_analysis == "Miesiąc i typ operacji":
            # Lepsze grupowanie danych dla czytelności
            if chart_type == "pie":
                # Dla wykresu kołowego - agreguj według typu operacji
                type_totals = {}
                for row in data:
                    op_type = row[1]  # TypOperacji
                    count = int(row[2])  # LiczbaOperacji
                    if op_type in type_totals:
                        type_totals[op_type] += count
                    else:
                        type_totals[op_type] = count
                
                labels = list(type_totals.keys())
                values = list(type_totals.values())
                title = "Udział typów operacji (łącznie)"
                ylabel = "Liczba operacji"
                
            elif chart_type == "line":
                # Dla wykresu liniowego - pokaż trendy w czasie, ograniczając do ostatnich okresów
                periods = list(set([row[0] for row in data]))
                periods.sort(reverse=True)
                recent_periods = periods[:12]  # Ostatnie 12 okresów
                
                # Znajdź najpopularniejszy typ operacji
                type_counts = {}
                for row in data:
                    if row[0] in recent_periods:
                        op_type = row[1]
                        count = int(row[2])
                        if op_type in type_counts:
                            type_counts[op_type] += count
                        else:
                            type_counts[op_type] = count
                
                # Weź top 3 typy operacji
                top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                main_type = top_types[0][0] if top_types else "Zamówienie"
                
                # Filtruj dane tylko dla głównego typu operacji w ostatnich okresach
                filtered_data = [(row[0], int(row[2])) for row in data 
                               if row[1] == main_type and row[0] in recent_periods]
                filtered_data.sort(key=lambda x: x[0])
                
                labels = [item[0] for item in filtered_data]
                values = [item[1] for item in filtered_data]
                title = f"Trend operacji '{main_type}' w czasie (ostatnie {len(labels)} okresów)"
                ylabel = "Liczba operacji"
                
            else:  # bar chart
                # Dla wykresu słupkowego - pokaż wszystkie dane
                labels = [f"{row[0]}\n{row[1][:8]}" for row in data]  # Skróć nazwy typów
                values = [int(row[2]) for row in data]
                title = f"Operacje według miesięcy i typów ({len(data)} wpisów)"
                ylabel = "Liczba operacji"
            
        elif selected_analysis == "Przychody w czasie":
            # Ograniczenie do ostatnich okresów dla lepszej czytelności
            if chart_type == "line":
                # Dla wykresu liniowego - pokaż wszystkie dane chronologicznie
                sorted_data = sorted(data, key=lambda x: x[0])
                recent_data = sorted_data[-24:] if len(sorted_data) > 24 else sorted_data  # Ostatnie 24 okresy
            else:
                # Dla innych wykresów - wszystkie dane
                recent_data = data
            
            labels = [row[0] for row in recent_data]
            values = [float(row[1].replace(',', '.')) if isinstance(row[1], str) else float(row[1]) for row in recent_data]
            title = f"Przychody w czasie ({len(recent_data)} okresów)"
            ylabel = "Przychody (zł)"
            
        elif selected_analysis == "Analiza zyskowności":
            # Ograniczenie danych dla lepszej czytelności
            limited_data = data[:12]  # Top 12 dla zyskowności
            labels = [str(row[0])[:15] + "..." if len(str(row[0])) > 15 else str(row[0]) for row in limited_data]
            values = [float(row[1]) if str(row[1]).replace('.', '').replace(',', '').replace('-', '').isdigit() else 0 for row in limited_data]
            title = f"Analiza zyskowności (top {len(limited_data)})"
            ylabel = "Zyskowność"
            
        elif selected_analysis == "Stan magazynu":
            # Ograniczenie do najwartościowszych produktów
            if chart_type == "pie":
                # Dla wykresu kołowego - top 10 + reszta
                top_data = data[:10]
                if len(data) > 10:
                    rest_sum = sum(float(str(row[4]).replace(',', '.')) for row in data[10:] if row[4])
                    labels = [row[0][:15] + "..." if len(row[0]) > 15 else row[0] for row in top_data] + ["Pozostałe"]
                    values = [float(str(row[4]).replace(',', '.')) for row in top_data if row[4]] + [rest_sum]  # Wartość magazynowa
                else:
                    labels = [row[0][:15] + "..." if len(row[0]) > 15 else row[0] for row in top_data]
                    values = [float(str(row[4]).replace(',', '.')) for row in top_data if row[4]]
                title = "Udział wartości magazynowej (top 10)"
                ylabel = "Wartość (zł)"
            else:
                # Dla innych wykresów - wszystkie produkty
                labels = [row[0][:12] + "..." if len(row[0]) > 12 else row[0] for row in data]
                values = [float(str(row[4]).replace(',', '.')) for row in data if row[4]]  # Wartość magazynowa
                title = f"Stan magazynu - wartość ({len(data)} produktów)"
                ylabel = "Wartość (zł)"
            
        else:
            # Domyślny przypadek - wszystkie dane
            labels = [str(row[0])[:20] + "..." if len(str(row[0])) > 20 else str(row[0]) for row in data]
            try:
                values = [float(str(row[1]).replace(',', '.').replace(' ', '')) if str(row[1]).replace('.', '').replace(',', '').replace('-', '').replace(' ', '').isdigit() else 1 for row in data]
            except:
                values = [1] * len(data)  # Fallback wartości
            title = f"Wykres - {selected_analysis} ({len(data)} pozycji)"
            ylabel = "Wartość"

        # Tworzenie wykresu - dostosuj rozmiar do ilości danych
        fig_width = max(10, len(labels) * 0.5)  # Dynamiczny szerokość
        fig_height = max(6, 8)  # Większa wysokość dla lepszej czytelności
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        if chart_type == "bar":
            colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
            bars = ax.bar(labels, values, color=colors)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_xlabel("Kategorie", fontsize=12)
            
            # Dodaj wartości na słupkach z mniejszą czcionką
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                       f'{value:,.0f}', ha='center', va='bottom', fontsize=8, rotation=0)
                       
        elif chart_type == "pie":
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            # Dla wykresu kołowego z wieloma etykietami użyj legendy zamiast etykiet na wykresie
            if len(labels) > 6:
                wedges, texts, autotexts = ax.pie(values, autopct='%1.1f%%', 
                                                colors=colors, startangle=90, 
                                                labels=None)  # Usuń etykiety z wykresu
                # Dodaj legendę z boku
                ax.legend(wedges, labels, title="Kategorie", loc="center left", 
                         bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
            else:
                wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                                colors=colors, startangle=90)
                # Zmniejsz czcionkę etykiet
                for text in texts:
                    text.set_fontsize(9)
            
            # Lepsze formatowanie procentów
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
                
        elif chart_type == "line":
            ax.plot(labels, values, marker='o', linewidth=2, markersize=6, color='steelblue')
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_xlabel("Okres", fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Dodaj wartości na punktach z mniejszą czcionką
            for i, value in enumerate(values):
                ax.annotate(f'{value:,.0f}', (labels[i], value), 
                          textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Lepsza rotacja etykiet z większymi odstępami
        if chart_type != "pie":
            # Dla długich etykiet użyj większej rotacji
            max_label_length = max(len(str(label)) for label in labels) if labels else 0
            if max_label_length > 10:
                plt.xticks(rotation=60, ha='right', fontsize=9)
            else:
                plt.xticks(rotation=45, ha='right', fontsize=10)
            
            # Zwiększ odstępy między etykietami
            ax.tick_params(axis='x', pad=8)
        
        # Dostosuj layout z większymi marginesami
        plt.tight_layout(pad=3.0)

        # Tworzenie wykresów z nawigacją
        self.create_chart_with_navigation(chart_window)

    def create_chart_with_navigation(self, chart_window):
        """Tworzy wykres z nawigacją dla dużych zbiorów danych"""
        # Frame dla nawigacji
        nav_frame = ttk.Frame(chart_window)
        nav_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        total_items = len(self.chart_data)
        total_pages = (total_items - 1) // self.items_per_page + 1 if total_items > 0 else 1
        
        # Informacje o stronie
        page_info = ttk.Label(nav_frame, text=f"Strona {self.current_page + 1} z {total_pages} ({total_items} elementów)")
        page_info.pack(side="left", padx=5)
        
        # Przyciski nawigacji (tylko jeśli więcej niż jedna strona)
        if total_pages > 1:
            ttk.Button(nav_frame, text="◀ Poprzednia", 
                      command=lambda: self.navigate_chart(-1)).pack(side="left", padx=5)
            ttk.Button(nav_frame, text="Następna ▶", 
                      command=lambda: self.navigate_chart(1)).pack(side="left", padx=5)
        
        # Kontrola rozmiaru strony
        ttk.Label(nav_frame, text="Elementów na stronie:").pack(side="left", padx=10)
        page_size_var = tk.StringVar(value=str(self.items_per_page))
        page_size_combo = ttk.Combobox(nav_frame, textvariable=page_size_var, 
                                      values=["10", "20", "30", "50", "100"], width=10)
        page_size_combo.pack(side="left", padx=5)
        page_size_combo.bind("<<ComboboxSelected>>", lambda e: self.change_page_size(int(page_size_var.get())))
        
        # Przycisk "Pokaż wszystko"
        ttk.Button(nav_frame, text="Pokaż wszystko", 
                  command=self.show_all_data).pack(side="left", padx=10)
        
        # Przycisk zamknij
        ttk.Button(nav_frame, text="Zamknij", 
                  command=chart_window.destroy).pack(side="right", padx=5)
        
        # Frame dla wykresu
        self.chart_frame = ttk.Frame(chart_window)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Wygeneruj wykres dla aktualnej strony
        self.update_chart_display()

    def navigate_chart(self, direction):
        """Nawigacja między stronami wykresu"""
        total_pages = (len(self.chart_data) - 1) // self.items_per_page + 1
        new_page = self.current_page + direction
        
        if 0 <= new_page < total_pages:
            self.current_page = new_page
            self.update_chart_display()
            
    def change_page_size(self, new_size):
        """Zmiana liczby elementów na stronie"""
        self.items_per_page = new_size
        self.current_page = 0  # Reset do pierwszej strony
        self.update_chart_display()
        
    def show_all_data(self):
        """Pokaż wszystkie dane na jednym wykresie"""
        self.items_per_page = len(self.chart_data)
        self.current_page = 0
        self.update_chart_display()
        
    def update_chart_display(self):
        """Aktualizuje wyświetlanie wykresu"""
        # Wyczyść poprzedni wykres
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        # Oblicz zakres danych dla aktualnej strony
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.chart_data))
        page_data = self.chart_data[start_idx:end_idx]
        
        if not page_data:
            return
            
        # Aktualizuj nawigację
        self.update_navigation_info()
        
        # Wygeneruj wykres dla aktualnej strony
        self.generate_chart_for_data(page_data)
        
    def update_navigation_info(self):
        """Aktualizuje informacje o nawigacji"""
        total_items = len(self.chart_data)
        total_pages = (total_items - 1) // self.items_per_page + 1 if total_items > 0 else 1
        
        # Znajdź i zaktualizuj etykietę informacyjną
        nav_frame = None
        for widget in self.chart_window_ref.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and "Strona" in child.cget("text"):
                        child.config(text=f"Strona {self.current_page + 1} z {total_pages} ({total_items} elementów)")
                        break

    def generate_chart_for_data(self, page_data):
        """Generuje wykres dla określonych danych"""
        selected_analysis = self.analysis_type.get()
        columns = self.chart_columns
        chart_type = self.chart_type_current
        
        # Przygotuj dane do wykresu na podstawie typu analizy
        if selected_analysis == "Typ operacji":
            if len(columns) == 4:  # Z okresami
                labels = [f"{row[0]}\n{row[1][:8]}" for row in page_data]
                values = [int(row[2]) for row in page_data]
                title = f"Operacje według okresów i typów"
                ylabel = "Liczba operacji"
            else:  # Bez okresów
                labels = [row[0] for row in page_data]
                values = [int(row[1]) for row in page_data]
                title = "Liczba operacji wg typu"
                ylabel = "Liczba operacji"
                
        elif selected_analysis == "Ranking produktów":
            if len(columns) == 4:  # Z okresami
                labels = [f"{row[0]}\n{row[1][:10]}..." if len(row[1]) > 10 else f"{row[0]}\n{row[1]}" for row in page_data]
                values = [int(row[3]) for row in page_data]
                title = "Ranking produktów według okresów"
                ylabel = "Sprzedane sztuki"
            else:  # Bez okresów
                labels = [row[0][:15] + "..." if len(row[0]) > 15 else row[0] for row in page_data]
                values = [int(row[2]) for row in page_data]
                title = "Ranking produktów"
                ylabel = "Sprzedane sztuki"
                
        elif selected_analysis == "Miesiąc i typ operacji":
            labels = [f"{row[0]}\n{row[1][:8]}" for row in page_data]
            values = [int(row[2]) for row in page_data]
            title = "Operacje według miesięcy i typów"
            ylabel = "Liczba operacji"
            
        elif selected_analysis == "Przychody w czasie":
            labels = [row[0] for row in page_data]
            values = [float(str(row[1]).replace(',', '.')) for row in page_data]
            title = "Przychody w czasie"
            ylabel = "Przychody (zł)"
            
        elif selected_analysis == "Stan magazynu":
            labels = [row[0][:15] + "..." if len(row[0]) > 15 else row[0] for row in page_data]
            values = [float(str(row[4]).replace(',', '.')) for row in page_data if row[4]]
            title = "Stan magazynu - wartość"
            ylabel = "Wartość (zł)"
            
        else:  # Domyślny przypadek
            labels = [str(row[0])[:20] + "..." if len(str(row[0])) > 20 else str(row[0]) for row in page_data]
            try:
                values = [float(str(row[1]).replace(',', '.').replace(' ', '')) if str(row[1]).replace('.', '').replace(',', '').replace('-', '').replace(' ', '').isdigit() else 1 for row in page_data]
            except:
                values = [1] * len(page_data)
            title = f"Wykres - {selected_analysis}"
            ylabel = "Wartość"

        # Tworzenie wykresu z adaptywnym rozmiarem
        fig_width = max(8, min(20, len(labels) * 0.8))  # Adaptywna szerokość
        fig_height = max(6, 10)  # Większa wysokość
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        if chart_type == "bar":
            colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
            bars = ax.bar(labels, values, color=colors)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_xlabel("Kategorie", fontsize=12)
            
            # Dodaj wartości na słupkach
            for bar, value in zip(bars, values):
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                           f'{value:,.0f}', ha='center', va='bottom', fontsize=9, rotation=0)
                           
        elif chart_type == "pie":
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                            colors=colors, startangle=90)
            for text in texts:
                text.set_fontsize(9)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
                
        elif chart_type == "line":
            ax.plot(labels, values, marker='o', linewidth=2, markersize=6, color='steelblue')
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_xlabel("Okres", fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Dodaj wartości na punktach
            for i, value in enumerate(values):
                ax.annotate(f'{value:,.0f}', (labels[i], value), 
                          textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)

        ax.set_title(f"{title} (strona {self.current_page + 1})", fontsize=14, fontweight='bold', pad=20)
        
        # Lepsza rotacja etykiet
        if chart_type != "pie":
            max_label_length = max(len(str(label)) for label in labels) if labels else 0
            if max_label_length > 15:
                plt.xticks(rotation=60, ha='right', fontsize=9)
            else:
                plt.xticks(rotation=45, ha='right', fontsize=10)
            ax.tick_params(axis='x', pad=8)
        
        plt.tight_layout(pad=3.0)

        # Wstawienie wykresu do frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_price(self, *args):
        produkt_id_str = self.product_SelectedId.get().strip()
        ilosc_str = self.countInput.get().strip()
        if produkt_id_str.isdigit() and ilosc_str.replace('.', '', 1).isdigit():
            produkt_id = int(produkt_id_str)
            ilosc = float(ilosc_str)
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT Cena FROM Produkty WHERE ProduktID = ?", (produkt_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                cena = row[0]
                self.price_var.set(f"{cena * ilosc:.2f}")
            else:
                self.price_var.set("")
        else:
            self.price_var.set("")

    def on_product_select(self, event):
        selected = self.products_tree.selection()
        if selected:
            produkt_values = self.products_tree.item(selected[0], "values")
            self.product_SelectedId.delete(0, tk.END)
            self.product_SelectedId.insert(0, produkt_values[0])
            self.countInput.delete(0, tk.END)  # Resetuj ilość
            self.update_price()

    def on_id_entry(self, event=None):
        produkt_id = self.product_SelectedId.get().strip()
        if produkt_id.isdigit():
            for item in self.products_tree.get_children():
                values = self.products_tree.item(item, "values")
                if values and str(values[0]) == produkt_id:
                    self.products_tree.selection_set(item)
                    self.products_tree.see(item)
                    break
        self.update_price()

    # === METODY RAPORTÓW Z BAZY DANYCH ===
    
    def raport_zgodnosc_zamowien(self):
        """Raport sprawdzający zgodność zamówień z wysyłkami według produktów"""
        for row in self.raporty_tree.get_children():
            self.raporty_tree.delete(row)

        # Pobierz filtry dat
        date_from = self.report_date_from.get().strip() or "0001-01-01"
        date_to = self.report_date_to.get().strip() or "9999-12-31"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = """
            SELECT 
                p.ProduktID,
                p.Nazwa as NazwaProduktu,
                COALESCE(SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.Ilosc ELSE 0 END), 0) as ZamowioneIlosc,
                COALESCE(SUM(CASE WHEN o.TypOperacji = 'Wysyłka' THEN o.Ilosc ELSE 0 END), 0) as WyslaneIlosc,
                CASE 
                    WHEN COALESCE(SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.Ilosc ELSE 0 END), 0) = 
                         COALESCE(SUM(CASE WHEN o.TypOperacji = 'Wysyłka' THEN o.Ilosc ELSE 0 END), 0) 
                    THEN 'ZGODNE'
                    ELSE 'NIEZGODNE'
                END as Status,
                COALESCE(SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.Ilosc ELSE 0 END), 0) - 
                COALESCE(SUM(CASE WHEN o.TypOperacji = 'Wysyłka' THEN o.Ilosc ELSE 0 END), 0) as Roznica
            FROM Produkty p
            LEFT JOIN OperacjeMagazynowe o ON p.ProduktID = o.ProduktID 
                AND date(o.DataOperacji) BETWEEN ? AND ?
                AND o.TypOperacji IN ('Zamówienie', 'Wysyłka')
            GROUP BY p.ProduktID, p.Nazwa
            HAVING COALESCE(SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.Ilosc ELSE 0 END), 0) > 0 
                OR COALESCE(SUM(CASE WHEN o.TypOperacji = 'Wysyłka' THEN o.Ilosc ELSE 0 END), 0) > 0
            ORDER BY Status DESC, p.ProduktID
        """

        columns = ("ID Produktu", "Nazwa Produktu", "Zamówione ilość", "Wysłane ilość", "Status", "Różnica")
        self.raporty_tree["columns"] = columns
        for col in columns:
            self.raporty_tree.heading(col, text=col)
            self.raporty_tree.column(col, width=140)

        cursor.execute(query, (date_from, date_to))
        for row in cursor.fetchall():
            self.raporty_tree.insert("", "end", values=row)
        
        conn.close()

    def raport_przychodow(self):
        """Raport przychodów w podziale na miesiące"""
        for row in self.raporty_tree.get_children():
            self.raporty_tree.delete(row)

        # Pobierz filtry dat
        date_from = self.report_date_from.get().strip() or "0001-01-01"
        date_to = self.report_date_to.get().strip() or "9999-12-31"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = """
            SELECT 
                strftime('%Y-%m', o.DataOperacji) as Miesiac,
                COUNT(DISTINCT CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.OperacjaID END) as LiczbaZamowien,
                SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN p.Cena * o.Ilosc ELSE 0 END) as Przychody,
                SUM(CASE WHEN o.TypOperacji = 'Zwrot' THEN p.Cena * o.Ilosc ELSE 0 END) as Zwroty,
                SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN p.Cena * o.Ilosc ELSE 0 END) - 
                SUM(CASE WHEN o.TypOperacji = 'Zwrot' THEN p.Cena * o.Ilosc ELSE 0 END) as PrzychodNetto
            FROM OperacjeMagazynowe o
            JOIN Produkty p ON o.ProduktID = p.ProduktID
            WHERE o.TypOperacji IN ('Zamówienie', 'Zwrot')
            AND date(o.DataOperacji) BETWEEN ? AND ?
            GROUP BY strftime('%Y-%m', o.DataOperacji)
            ORDER BY Miesiac DESC
        """

        columns = ("Miesiąc", "Zamówienia", "Przychody (zł)", "Zwroty (zł)", "Przychód netto (zł)")
        self.raporty_tree["columns"] = columns
        for col in columns:
            self.raporty_tree.heading(col, text=col)
            self.raporty_tree.column(col, width=140)

        cursor.execute(query, (date_from, date_to))
        for row in cursor.fetchall():
            formatted_row = [row[0], row[1]]
            for i in range(2, len(row)):
                formatted_row.append(f"{row[i]:.2f}" if row[i] else "0.00")
            self.raporty_tree.insert("", "end", values=formatted_row)
        
        conn.close()

    def analiza_trendow(self):
        """Analiza trendów sprzedaży w czasie"""
        for row in self.raporty_tree.get_children():
            self.raporty_tree.delete(row)

        # Pobierz filtry dat
        date_from = self.report_date_from.get().strip() or "0001-01-01"
        date_to = self.report_date_to.get().strip() or "9999-12-31"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = """
            SELECT 
                p.Nazwa as Produkt,
                strftime('%Y-%m', o.DataOperacji) as Miesiac,
                SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.Ilosc ELSE 0 END) as SprzedaneIlosc,
                SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN p.Cena * o.Ilosc ELSE 0 END) as WartoscSprzedazy,
                RANK() OVER (PARTITION BY strftime('%Y-%m', o.DataOperacji) ORDER BY SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.Ilosc ELSE 0 END) DESC) as RankingMiesieczny
            FROM OperacjeMagazynowe o
            JOIN Produkty p ON o.ProduktID = p.ProduktID
            WHERE o.TypOperacji = 'Zamówienie'
            AND date(o.DataOperacji) BETWEEN ? AND ?
            GROUP BY p.Nazwa, strftime('%Y-%m', o.DataOperacji)
            HAVING SUM(CASE WHEN o.TypOperacji = 'Zamówienie' THEN o.Ilosc ELSE 0 END) > 0
            ORDER BY Miesiac DESC, RankingMiesieczny ASC
        """

        columns = ("Produkt", "Miesiąc", "Sprzedane szt.", "Wartość (zł)", "Ranking")
        self.raporty_tree["columns"] = columns
        for col in columns:
            self.raporty_tree.heading(col, text=col)
            self.raporty_tree.column(col, width=140)

        cursor.execute(query, (date_from, date_to))
        for row in cursor.fetchall():
            formatted_row = [row[0], row[1], row[2], f"{row[3]:.2f}", row[4]]
            self.raporty_tree.insert("", "end", values=formatted_row)
        
        conn.close()

    def raport_stanu_magazynu(self):
        """Raport aktualnego stanu magazynu z analizą wartości"""
        for row in self.raporty_tree.get_children():
            self.raporty_tree.delete(row)

        # Pobierz filtry dat (dla analizy sprzedaży w wybranym okresie)
        date_from = self.report_date_from.get().strip() or "0001-01-01"
        date_to = self.report_date_to.get().strip() or "9999-12-31"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = """
            SELECT 
                p.Nazwa,
                p.Kategoria,
                p.Ilosc as StanMagazynowy,
                p.Cena,
                (p.Ilosc * p.Cena) as WartoscMagazynowa,
                COALESCE(sprzedaz.SprzedaneWOkresie, 0) as SprzedaneWOkresie,
                CASE 
                    WHEN p.Ilosc = 0 THEN 'BRAK TOWARU'
                    WHEN p.Ilosc < 5 THEN 'NISKI STAN'
                    WHEN p.Ilosc < 20 THEN 'ŚREDNI STAN'
                    ELSE 'WYSOKI STAN'
                END as StatusStanu
            FROM Produkty p
            LEFT JOIN (
                SELECT 
                    ProduktID,
                    SUM(Ilosc) as SprzedaneWOkresie
                FROM OperacjeMagazynowe 
                WHERE TypOperacji = 'Zamówienie' 
                AND date(DataOperacji) BETWEEN ? AND ?
                GROUP BY ProduktID
            ) sprzedaz ON p.ProduktID = sprzedaz.ProduktID
            ORDER BY WartoscMagazynowa DESC
        """

        columns = ("Produkt", "Kategoria", "Stan", "Cena", "Wartość (zł)", "Sprzedane (okres)", "Status")
        self.raporty_tree["columns"] = columns
        for col in columns:
            self.raporty_tree.heading(col, text=col)
            self.raporty_tree.column(col, width=120)

        cursor.execute(query, (date_from, date_to))
        for row in cursor.fetchall():
            formatted_row = [row[0], row[1], row[2], f"{row[3]:.2f}", f"{row[4]:.2f}", row[5], row[6]]
            self.raporty_tree.insert("", "end", values=formatted_row)
        
        conn.close()

    def show_report_chart(self, chart_type="bar"):
        """Tworzy wykres w osobnym oknie dla raportów szczegółowych"""
        # Sprawdź czy są dane w tabeli raportów
        if not self.raporty_tree.get_children():
            messagebox.showwarning("Brak danych", "Najpierw uruchom raport!")
            return

        # Pobierz dane z aktualnego raportu
        columns = self.raporty_tree["columns"]
        data = []
        for item in self.raporty_tree.get_children():
            values = self.raporty_tree.item(item, "values")
            data.append(values)

        if not data:
            return

        # Utwórz nowe okno
        chart_window = tk.Toplevel(self)
        chart_window.title(f"Wykres raportu")
        chart_window.geometry("800x600")
        chart_window.configure(bg="#f5f7fa")

        # Przygotuj dane do wykresu na podstawie kolumn
        try:
            if "Przychody" in columns[2] or "Wartość" in columns[4]:  # Raport przychodów lub stan magazynu
                if "Miesiąc" in columns[0]:  # Raport przychodów
                    labels = [row[0] for row in data[:12]]  # Ostatnie 12 miesięcy
                    values = [float(row[2].replace(',', '.')) if isinstance(row[2], str) else float(row[2]) for row in data[:12]]
                    title = "Przychody według miesięcy"
                    ylabel = "Przychody (zł)"
                elif "Produkt" in columns[0]:  # Stan magazynu
                    limited_data = data[:15]
                    labels = [row[0][:15] + "..." if len(row[0]) > 15 else row[0] for row in limited_data]
                    values = [float(str(row[4]).replace(',', '.')) for row in limited_data if row[4]]
                    title = "Wartość magazynowa produktów"
                    ylabel = "Wartość (zł)"
                else:
                    labels = [str(row[0])[:20] for row in data[:10]]
                    values = [1] * len(labels)
                    title = "Wykres raportu"
                    ylabel = "Wartość"
            elif "Ranking" in columns[4]:  # Analiza trendów
                limited_data = data[:15]
                labels = [f"{row[0][:12]}\n{row[1]}" for row in limited_data]
                values = [int(row[2]) for row in limited_data]
                title = "Sprzedaż produktów według miesięcy"
                ylabel = "Sprzedane sztuki"
            elif "Status" in columns[5]:  # Raport zgodności
                status_counts = {}
                for row in data:
                    status = row[5]
                    if status in status_counts:
                        status_counts[status] += 1
                    else:
                        status_counts[status] = 1
                labels = list(status_counts.keys())
                values = list(status_counts.values())
                title = "Zgodność zamówień z wysyłkami"
                ylabel = "Liczba zamówień"
            else:
                # Domyślne przetwarzanie
                labels = [str(row[0])[:20] for row in data[:10]]
                values = [1] * len(labels)
                title = "Wykres raportu"
                ylabel = "Wartość"

            # Tworzenie wykresu
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if chart_type == "bar":
                colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
                bars = ax.bar(labels, values, color=colors)
                ax.set_ylabel(ylabel, fontsize=12)
                ax.set_xlabel("Kategorie", fontsize=12)
                
                # Dodaj wartości na słupkach
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                           f'{value:,.0f}', ha='center', va='bottom', fontsize=9)
                           
            elif chart_type == "pie":
                colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
                if len(labels) > 8:
                    # Grupa małe wartości w "Pozostałe"
                    top_data = list(zip(labels, values))[:8]
                    rest_sum = sum(values[8:])
                    if rest_sum > 0:
                        labels = [item[0] for item in top_data] + ["Pozostałe"]
                        values = [item[1] for item in top_data] + [rest_sum]
                    else:
                        labels = [item[0] for item in top_data]
                        values = [item[1] for item in top_data]
                
                wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                                colors=colors, startangle=90)
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    
            elif chart_type == "line":
                ax.plot(labels, values, marker='o', linewidth=2, markersize=6, color='steelblue')
                ax.set_ylabel(ylabel, fontsize=12)
                ax.set_xlabel("Okres", fontsize=12)
                ax.grid(True, alpha=0.3)
                
                # Dodaj wartości na punktach
                for i, value in enumerate(values):
                    ax.annotate(f'{value:,.0f}', (labels[i], value), 
                              textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)

            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Rotacja etykiet
            if chart_type != "pie":
                plt.xticks(rotation=45, ha='right', fontsize=10)
                ax.tick_params(axis='x', pad=8)
            
            plt.tight_layout(pad=3.0)

            # Wstawienie wykresu do okna
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

            # Przycisk zamknij
            close_button = ttk.Button(chart_window, text="Zamknij", 
                                    command=chart_window.destroy)
            close_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas tworzenia wykresu: {e}")
            chart_window.destroy()


if __name__ == "__main__":
    app = MagazynApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass

