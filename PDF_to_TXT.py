import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2
import re
import threading


class ConversorPartituraViolaoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Partitura de Violão")
        self.root.geometry("1660x1660")
        self.root.resizable(True, True)

        # Variáveis
        self.arquivo_entrada = tk.StringVar()
        self.arquivo_saida = tk.StringVar()
        self.progresso = tk.DoubleVar(value=0)
        self.status = tk.StringVar(value="Pronto para iniciar")

        # Criar widgets da interface
        self.criar_widgets()

        # Mapeamento de notas e acordes para violão
        self.notas_violao = {
            'E': 'Mi (1ª corda)',
            'B': 'Si (2ª corda)',
            'G': 'Sol (3ª corda)',
            'D': 'Ré (4ª corda)',
            'A': 'Lá (5ª corda)',
            'E2': 'Mi (6ª corda)',
            # Acordes comuns de violão
            'C': 'Dó maior',
            'Cm': 'Dó menor',
            'D': 'Ré maior',
            'Dm': 'Ré menor',
            'E': 'Mi maior',
            'Em': 'Mi menor',
            'F': 'Fá maior',
            'Fm': 'Fá menor',
            'G': 'Sol maior',
            'Gm': 'Sol menor',
            'A': 'Lá maior',
            'Am': 'Lá menor',
            'B': 'Si maior',
            'Bm': 'Si menor',
            # Sustenidos e bemóis
            'C#': 'Dó sustenido',
            'Db': 'Ré bemol',
            'D#': 'Ré sustenido',
            'Eb': 'Mi bemol',
            'F#': 'Fá sustenido',
            'Gb': 'Sol bemol',
            'G#': 'Sol sustenido',
            'Ab': 'Lá bemol',
            'A#': 'Lá sustenido',
            'Bb': 'Si bemol'
        }

        # Padrões de reconhecimento específicos para tablatura de violão
        self.padroes_tab = {
            'corda': r'(e|B|G|D|A|E)\|',  # Cordas de violão em notação de tablatura
            'casa': r'-(\d+)-',  # Número de casa
            'acorde': r'\b([A-G][#b]?(?:m|M|7|dim|aug|sus[24]|maj7|min7|add\d|9)?)\b',  # Acordes em notação musical
            'compasso': r'(\d+/\d+)'  # Fórmula de compasso
        }

    def criar_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(main_frame, text="Conversor de Partitura de Violão para Texto",
                  font=("Arial", 14, "bold")).pack(pady=(0, 20))

        # Frame de arquivo de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Arquivo de Entrada")
        input_frame.pack(fill=tk.X, pady=10)

        input_file_frame = ttk.Frame(input_frame)
        input_file_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Entry(input_file_frame, textvariable=self.arquivo_entrada, width=60).pack(side=tk.LEFT, fill=tk.X,
                                                                                      expand=True, padx=(0, 10))
        ttk.Button(input_file_frame, text="Procurar...", command=self.selecionar_arquivo_entrada).pack(side=tk.RIGHT)

        # Frame de arquivo de saída
        output_frame = ttk.LabelFrame(main_frame, text="Arquivo de Saída")
        output_frame.pack(fill=tk.X, pady=10)

        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Entry(output_file_frame, textvariable=self.arquivo_saida, width=60).pack(side=tk.LEFT, fill=tk.X,
                                                                                     expand=True, padx=(0, 10))
        ttk.Button(output_file_frame, text="Procurar...", command=self.selecionar_arquivo_saida).pack(side=tk.RIGHT)

        # Frame de opções
        options_frame = ttk.LabelFrame(main_frame, text="Opções de Processamento")
        options_frame.pack(fill=tk.X, pady=10)

        self.opcao_tab = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Reconhecer tablatura de violão", variable=self.opcao_tab).pack(anchor=tk.W,
                                                                                                            padx=10,
                                                                                                            pady=5)

        self.opcao_acordes = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Reconhecer acordes", variable=self.opcao_acordes).pack(anchor=tk.W,
                                                                                                    padx=10, pady=5)

        # Área de visualização
        preview_frame = ttk.LabelFrame(main_frame, text="Visualização")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Texto de visualização com scrollbar
        self.texto_visualizacao = tk.Text(preview_frame, wrap=tk.WORD, height=15)
        self.texto_visualizacao.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(preview_frame, command=self.texto_visualizacao.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        self.texto_visualizacao.config(yscrollcommand=scrollbar.set)

        # Barra de progresso
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 5))

        ttk.Label(progress_frame, textvariable=self.status).pack(anchor=tk.W)
        ttk.Progressbar(progress_frame, variable=self.progresso, maximum=100).pack(fill=tk.X, pady=5)

        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Converter", command=self.iniciar_conversao).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.limpar).pack(side=tk.RIGHT, padx=5)

    def selecionar_arquivo_entrada(self):
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo da partitura",
            filetypes=[
                ("Arquivos PDF", "*.pdf"),
                ("Arquivos de imagem", "*.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivo:
            self.arquivo_entrada.set(arquivo)

            # Sugerir nome de arquivo de saída
            nome_base = os.path.splitext(os.path.basename(arquivo))[0]
            diretorio = os.path.dirname(arquivo)
            saida_sugerida = os.path.join(diretorio, f"{nome_base}_convertido.txt")
            self.arquivo_saida.set(saida_sugerida)

    def selecionar_arquivo_saida(self):
        arquivo = filedialog.asksaveasfilename(
            title="Salvar arquivo de texto",
            defaultextension=".txt",
            filetypes=[
                ("Arquivos de texto", "*.txt"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if arquivo:
            self.arquivo_saida.set(arquivo)

    def extrair_texto_pdf(self, caminho_pdf):
        """Extrai texto diretamente de um PDF"""
        try:
            texto = ""
            with open(caminho_pdf, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                for pagina in leitor.pages:
                    texto += pagina.extract_text() + "\n\n"
            return texto
        except Exception as e:
            return f"Erro ao extrair texto do PDF: {e}"

    def analisar_partitura(self, texto):
        """Analisa o texto extraído para identificar elementos de partitura de violão"""
        if not texto or len(texto.strip()) == 0:
            return "Não foi possível extrair texto da partitura. O arquivo pode estar em formato de imagem ou ser uma partitura escaneada."

        linhas = texto.strip().split('\n')
        resultado = ["Análise da Partitura de Violão:", ""]

        # Procurar por elementos de tablatura
        tem_tab = False
        tem_acordes = False

        # Primeiro passo: identificar se é uma tablatura
        for linha in linhas:
            if re.search(r'(e|B|G|D|A|E)\|[-\d\|]+', linha):
                tem_tab = True
                break

            if re.search(self.padroes_tab['acorde'], linha):
                tem_acordes = True

        if tem_tab:
            resultado.append("TABLATURA IDENTIFICADA")
            resultado.append("-" * 30)
            resultado.append("")

            # Analisar linhas como tablatura
            tab_atual = []

            for linha in linhas:
                # Verificar se é uma linha de tablatura
                if re.search(r'[eEBGDA]\|', linha):
                    tab_atual.append(linha)
                elif len(tab_atual) > 0:
                    # Processar tab acumulada
                    resultado.append("Trecho de tablatura:")
                    resultado.extend(tab_atual)
                    resultado.append("")

                    # Analisar o que foi encontrado
                    resultado.append("Interpretação:")
                    notas_encontradas = []

                    for l in tab_atual:
                        # Identificar corda
                        match_corda = re.search(r'([eEBGDA])\|', l)
                        if match_corda:
                            corda = match_corda.group(1)
                            # Identificar casas
                            casas = re.findall(r'-(\d+)-', l)
                            if casas:
                                for casa in casas:
                                    if corda in "eE" and corda == "e":
                                        notas_encontradas.append(f"Corda Mi (1ª) - Casa {casa}")
                                    elif corda == "B":
                                        notas_encontradas.append(f"Corda Si (2ª) - Casa {casa}")
                                    elif corda == "G":
                                        notas_encontradas.append(f"Corda Sol (3ª) - Casa {casa}")
                                    elif corda == "D":
                                        notas_encontradas.append(f"Corda Ré (4ª) - Casa {casa}")
                                    elif corda == "A":
                                        notas_encontradas.append(f"Corda Lá (5ª) - Casa {casa}")
                                    elif corda in "eE" and corda == "E":
                                        notas_encontradas.append(f"Corda Mi (6ª) - Casa {casa}")

                    resultado.extend(notas_encontradas)
                    resultado.append("")
                    tab_atual = []
                else:
                    # Verificar acordes na linha
                    acordes = re.findall(self.padroes_tab['acorde'], linha)
                    if acordes and self.opcao_acordes.get():
                        resultado.append(f"Acordes encontrados: {linha}")
                        acordes_traduzidos = []
                        for acorde in acordes:
                            traducao = self.notas_violao.get(acorde, acorde)
                            acordes_traduzidos.append(f"{acorde} = {traducao}")
                        resultado.append("  " + ", ".join(acordes_traduzidos))
                        resultado.append("")

            # Processar última tablatura se houver
            if len(tab_atual) > 0:
                resultado.append("Trecho de tablatura:")
                resultado.extend(tab_atual)
                resultado.append("")

        elif tem_acordes and self.opcao_acordes.get():
            resultado.append("ACORDES IDENTIFICADOS")
            resultado.append("-" * 30)
            resultado.append("")

            for linha in linhas:
                acordes = re.findall(self.padroes_tab['acorde'], linha)
                if acordes:
                    resultado.append(f"Linha: {linha}")
                    acordes_traduzidos = []
                    for acorde in acordes:
                        traducao = self.notas_violao.get(acorde, acorde)
                        acordes_traduzidos.append(f"{acorde} = {traducao}")
                    resultado.append("  " + ", ".join(acordes_traduzidos))
                    resultado.append("")

        else:
            resultado.append("Não foi possível identificar elementos específicos de tablatura ou acordes de violão.")
            resultado.append("Conteúdo extraído do arquivo:")
            resultado.append("-" * 30)
            resultado.append("")

            # Limitar a 50 linhas para não sobrecarregar
            linhas_limitadas = linhas[:50]
            resultado.extend(linhas_limitadas)

            if len(linhas) > 50:
                resultado.append("...")
                resultado.append(f"[+{len(linhas) - 50} linhas não exibidas]")

        return "\n".join(resultado)

    def atualizar_progresso(self, valor, mensagem):
        """Atualiza a barra de progresso e o status"""
        self.progresso.set(valor)
        self.status.set(mensagem)
        self.root.update_idletasks()

    def processar_conversao(self):
        """Processa a conversão em uma thread separada"""
        try:
            arquivo_entrada = self.arquivo_entrada.get()
            arquivo_saida = self.arquivo_saida.get()

            if not arquivo_entrada or not os.path.isfile(arquivo_entrada):
                messagebox.showerror("Erro", "Selecione um arquivo de entrada válido")
                self.atualizar_progresso(0, "Erro: arquivo de entrada inválido")
                return

            if not arquivo_saida:
                messagebox.showerror("Erro", "Selecione um local para salvar o arquivo de saída")
                self.atualizar_progresso(0, "Erro: arquivo de saída não especificado")
                return

            # Extrair texto
            self.atualizar_progresso(20, "Extraindo texto do arquivo...")
            texto_extraido = self.extrair_texto_pdf(arquivo_entrada)

            # Analisar conteúdo
            self.atualizar_progresso(50, "Analisando conteúdo musical...")
            resultado = self.analisar_partitura(texto_extraido)

            # Mostrar visualização
            self.atualizar_progresso(80, "Preparando visualização...")
            self.texto_visualizacao.delete(1.0, tk.END)
            self.texto_visualizacao.insert(tk.END, resultado)

            # Salvar resultado
            try:
                with open(arquivo_saida, 'w', encoding='utf-8') as f:
                    f.write(resultado)
                self.atualizar_progresso(100, "Conversão concluída com sucesso")
                messagebox.showinfo("Sucesso", f"Conversão concluída! Arquivo salvo em:\n{arquivo_saida}")
            except Exception as e:
                self.atualizar_progresso(0, f"Erro ao salvar arquivo: {e}")
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {e}")

        except Exception as e:
            self.atualizar_progresso(0, f"Erro durante a conversão: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a conversão: {e}")

    def iniciar_conversao(self):
        """Inicia o processo de conversão em uma thread separada"""
        self.atualizar_progresso(10, "Iniciando conversão...")
        threading.Thread(target=self.processar_conversao, daemon=True).start()

    def limpar(self):
        """Limpa todos os campos"""
        self.arquivo_entrada.set("")
        self.arquivo_saida.set("")
        self.texto_visualizacao.delete(1.0, tk.END)
        self.atualizar_progresso(0, "Pronto para iniciar")


# Função para verificar dependências
def verificar_dependencias():
    dependencias_faltantes = []

    try:
        import PyPDF2
    except ImportError:
        dependencias_faltantes.append("PyPDF2")

    try:
        import tkinter
    except ImportError:
        dependencias_faltantes.append("tkinter")

    if dependencias_faltantes:
        print("AVISO: As seguintes dependências estão faltando:")
        for dep in dependencias_faltantes:
            print(f"  - {dep}")
        print("\nInstale-as usando pip:")
        print(f"pip install {' '.join(dependencias_faltantes)}")
        return False

    return True


# Função principal
if __name__ == "__main__":
    if verificar_dependencias():
        root = tk.Tk()
        app = ConversorPartituraViolaoApp(root)
        root.mainloop()
    else:
        print("Não foi possível iniciar o aplicativo devido a dependências faltantes.")