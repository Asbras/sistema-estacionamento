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
        "Dados importados",
        "Exportar dados",
        "Sobre",
    )

    def __init__(self, master, usuario, ao_abrir_entrada, ao_abrir_saida,
                 ao_abrir_veiculos, ao_abrir_vagas, ao_abrir_historico,
                 ao_abrir_usuarios, ao_abrir_sobre, ao_abrir_importacao,
                 ao_abrir_dados_importados, ao_abrir_exportacao, ao_sair):
        super().__init__(master, padding=28)
        self.usuario = usuario
        self.ao_abrir_entrada = ao_abrir_entrada
        self.ao_abrir_saida = ao_abrir_saida
        self.ao_abrir_veiculos = ao_abrir_veiculos
        self.ao_abrir_vagas = ao_abrir_vagas
        self.ao_abrir_historico = ao_abrir_historico
        self.ao_abrir_usuarios = ao_abrir_usuarios
        self.ao_abrir_sobre = ao_abrir_sobre
        self.ao_abrir_importacao = ao_abrir_importacao
        self.ao_abrir_dados_importados = ao_abrir_dados_importados
        self.ao_abrir_exportacao = ao_abrir_exportacao
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
            opcoes = {"state": "disabled"}
            if acao == "Entrada de veículo":
                opcoes = {"command": self.ao_abrir_entrada}
            if acao == "Saída de veículo":
                opcoes = {"command": self.ao_abrir_saida}
            if acao == "Veículos":
                opcoes = {"command": self.ao_abrir_veiculos}
            if acao == "Vagas":
                opcoes = {"command": self.ao_abrir_vagas}
            if acao == "Histórico":
                opcoes = {"command": self.ao_abrir_historico}
            if acao == "Usuários":
                opcoes = {"command": self.ao_abrir_usuarios}
            if acao == "Sobre":
                opcoes = {"command": self.ao_abrir_sobre}
            if acao == "Importar dados":
                opcoes = {"command": self.ao_abrir_importacao}
            if acao == "Dados importados":
                opcoes = {"command": self.ao_abrir_dados_importados}
            if acao == "Exportar dados":
                opcoes = {"command": self.ao_abrir_exportacao}
            botao = ttk.Button(grade, text=acao, **opcoes)
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
        for linha in range((len(self.ACOES_FUTURAS) + 2) // 3):
            grade.rowconfigure(linha, weight=1)

        ttk.Button(self, text="Sair", command=self.ao_sair).pack(
            anchor="e", pady=(16, 0)
        )
