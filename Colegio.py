import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cadastro de Colegio")
        self.geometry("700x500")

        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',       
            password='',       
            database='colegio' 
        )
        self.cursor = self.conn.cursor()

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (TelaAlunos, TelaTurmas):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.create_menu()
        self.show_frame(TelaAlunos)

    def create_menu(self):
        menubar = tk.Menu(self)

        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(label="Alunos", command=lambda: self.show_frame(TelaAlunos))
        nav_menu.add_command(label="Turmas", command=lambda: self.show_frame(TelaTurmas))
        menubar.add_cascade(label="Navegação", menu=nav_menu)

        ajuda_menu = tk.Menu(menubar, tearoff=0)
        ajuda_menu.add_command(label="Créditos", command=self.show_credits)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)

        self.config(menu=menubar)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.atualizar_dados()
        frame.tkraise()

    def show_credits(self):
        messagebox.showinfo(
            "Créditos",
            "Projeto: Cadastro de Colegio\nEquipe:\n- Matheus Henrique\n- Pedro Lucio\n- Rosembergue Andrade\n- Marleu Antonio\n\n"
            "DESCRIÇÃO\n\n"
            "Matheus e Pedro, Conexão com Banco de Dados e Class TelaAlunos\n\n"
            "Marley e Rosembergue, Class app e Class Telaturma"
        )

class TelaAlunos(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Cadastro de Alunos", font=("Arial", 18))
        label.pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky="e")
        self.nome_entry = ttk.Entry(form_frame, width=30)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Idade:").grid(row=1, column=0, sticky="e")
        self.idade_entry = ttk.Entry(form_frame, width=30)
        self.idade_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Turma:").grid(row=2, column=0, sticky="e")
        self.combo_turma = ttk.Combobox(form_frame, state="readonly", width=28)
        self.combo_turma.grid(row=2, column=1, padx=5, pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Cadastrar", command=self.cadastrar_aluno).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self.limpar_form).grid(row=0, column=1, padx=5)

        self.tree = ttk.Treeview(self, columns=("ID", "Nome", "Idade", "Turma"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Idade", text="Idade")
        self.tree.heading("Turma", text="Turma")

        self.tree.column("ID", width=50)
        self.tree.column("Nome", width=200)
        self.tree.column("Idade", width=80)
        self.tree.column("Turma", width=150)

        self.tree.pack(fill="both", expand=True, pady=10)

    def atualizar_dados(self):
        self.atualizar_combo()
        self.atualizar_tree()

    def atualizar_combo(self):
        self.controller.cursor.execute("SELECT id, nome FROM turma")
        turmas = self.controller.cursor.fetchall()
        self.turmas_dict = {nome: id_ for (id_, nome) in turmas}
        self.combo_turma['values'] = list(self.turmas_dict.keys())
        if turmas:
            self.combo_turma.current(0)

    def atualizar_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT aluno.id, aluno.nome, aluno.idade, turma.nome
            FROM aluno
            JOIN turma ON aluno.turma_id = turma.id
            ORDER BY aluno.id
        """
        self.controller.cursor.execute(query)
        for row in self.controller.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def cadastrar_aluno(self):
        nome = self.nome_entry.get().strip()
        idade = self.idade_entry.get().strip()
        turma_nome = self.combo_turma.get()

        if not nome or not idade or not turma_nome:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            idade_int = int(idade)
        except ValueError:
            messagebox.showwarning("Aviso", "Idade deve ser um número inteiro.")
            return

        turma_id = self.turmas_dict.get(turma_nome)
        if not turma_id:
            messagebox.showerror("Erro", "Turma selecionada inválida.")
            return

        sql = "INSERT INTO aluno (nome, idade, turma_id) VALUES (%s, %s, %s)"
        try:
            self.controller.cursor.execute(sql, (nome, idade_int, turma_id))
            self.controller.conn.commit()
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            self.limpar_form()
            self.atualizar_tree()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar aluno:\n{e}")

    def limpar_form(self):
        self.nome_entry.delete(0, tk.END)
        self.idade_entry.delete(0, tk.END)
        if self.combo_turma['values']:
            self.combo_turma.current(0)

class TelaTurmas(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Cadastro de Turmas", font=("Arial", 18))
        label.pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Nome da Turma:").grid(row=0, column=0, sticky="e")
        self.nome_entry = ttk.Entry(form_frame, width=30)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Cadastrar", command=self.cadastrar_turma).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self.limpar_form).grid(row=0, column=1, padx=5)

        self.tree = ttk.Treeview(self, columns=("ID", "Nome"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")

        self.tree.column("ID", width=50)
        self.tree.column("Nome", width=200)

        self.tree.pack(fill="both", expand=True, pady=10)

    def atualizar_dados(self):
        self.atualizar_tree()

    def atualizar_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.controller.cursor.execute("SELECT id, nome FROM turma ORDER BY id")
        for row in self.controller.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def cadastrar_turma(self):
        nome = self.nome_entry.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Digite o nome da turma.")
            return

        sql = "INSERT INTO turma (nome) VALUES (%s)"
        try:
            self.controller.cursor.execute(sql, (nome,))
            self.controller.conn.commit()
            messagebox.showinfo("Sucesso", "Turma cadastrada com sucesso!")
            self.limpar_form()
            self.atualizar_tree()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar turma:\n{e}")

    def limpar_form(self):
        self.nome_entry.delete(0, tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()
