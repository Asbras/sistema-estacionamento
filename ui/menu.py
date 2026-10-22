"""Menu principal com atalhos reservados para próximas etapas."""

from tkinter import ttk


class MenuFrame(ttk.Frame):
    ACOES_FUTURAS = (
        "Entrada de veículo",
        "Saída de veículo",
        "Veículos",
        "Vagas",
        "Histórico",
        "Usuários",
        "Importar dados",
        "Exportar dados",
        "Sobre",
    )

    def __init__(self, master, usuario, ao_sair):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_sair = ao_sair

        ttk.Label(self, text="Menu principal", font=("TkDefaultFont", 18, "bold")).pack(
            anchor="w"
        )
        ttk.Label(self, text=f"Funcionário: {usuario['username']}").pack(
            anchor="w", pady=(6, 18)
        )

        grade = ttk.Frame(self)
        grade.pack(fill="both", expand=True)
        for indice, acao in enumerate(self.ACOES_FUTURAS):
            botao = ttk.Button(grade, text=acao, state="disabled")
            botao.grid(
                row=indice // 3,
                column=indice % 3,
                sticky="nsew",
                padx=5,
                pady=5,
                ipadx=4,
                ipady=9,
            )
        for coluna in range(3):
            grade.columnconfigure(coluna, weight=1)
        for linha in range(3):
            grade.rowconfigure(linha, weight=1)

        ttk.Button(self, text="Sair", command=self.ao_sair).pack(
            anchor="e", pady=(16, 0)
        )
