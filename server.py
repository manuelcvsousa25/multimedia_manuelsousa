"""Servidor HTTP local, sem frameworks, para o projeto educativo FinanceLab."""

import errno
from datetime import date
from decimal import Decimal, localcontext
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from python.investing import (
    ErroDadosMercado,
    calcular_projecao,
    obter_historico_mensal,
)
from python.personal_finance import (
    CATEGORIAS_DESPESA,
    adicionar_despesa,
    carregar_despesas,
    calcular_despesas,
    guardar_despesas,
    remover_despesa,
)


PASTA_PROJETO = Path(__file__).resolve().parent
ANFITRIAO = "127.0.0.1"
PORTA = 8000
ENDERECOS_PUBLICOS = {
    "/": "paginainicial.html",
    "/index.html": "paginainicial.html",
    "/paginainicial.html": "paginainicial.html",
    "/money_catcher": "moneycatcher.html",
    "/money_catcher.html": "moneycatcher.html",
    "/moneycatcher": "moneycatcher.html",
    "/moneycatcher.html": "moneycatcher.html",
    "/trading": "moneycatcher.html",
    "/trading.html": "moneycatcher.html",
    "/investing": "pages/investing.html",
    "/pages/investing.html": "pages/investing.html",
    "/investimentos.html": "pages/investing.html",
    "/personal_finance.html": "personal_finance.html",
    "/financas_pessoais.html": "personal_finance.html",
    "/paginainicial.css": "paginainicial.css",
    "/money_catcher.js": "money_catcher.js",
}
MARCADORES_FINANCAS = {
    "__DESPESA_DESCRICAO__": "descricao_despesa",
    "__DESPESA_VALOR__": "valor_despesa",
    "__DATA_DESPESA__": "data_despesa",
}
MARCADORES_INVESTIMENTO = {
    "__MONTANTE_ETF__": "montante_etf",
    "__APORTE_ETF__": "aporte_etf",
    "__ANOS_ETF__": "anos_etf",
    "__RETORNO_ETF__": "retorno_etf",
    "__CUSTOS_ETF__": "custos_etf",
    "__INFLACAO_ETF__": "inflacao_etf",
    "__SIMBOLO_ETF__": "simbolo_etf",
}
class FinanceLabHTTPServer(HTTPServer):
    """HTTPServer separado para permitir testes com uma porta temporária."""


def formatar_euros(valor):
    """Formata um Decimal com separadores e vírgula decimal portugueses."""
    texto = format(valor, ",.2f")
    return texto.replace(",", "_").replace(".", ",").replace("_", ".") + " €"


def formatar_numero(valor):
    """Formata uma quantidade sem acrescentar casas decimais desnecessárias."""
    with localcontext() as contexto:
        contexto.prec = max(50, valor.adjusted() + 8) if valor else 50
        valor_arredondado = valor.quantize(Decimal("0.000001"))
    texto = format(valor_arredondado, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def formatar_percentagem(valor):
    """Apresenta percentagens com duas casas decimais e vírgula decimal."""
    texto = format(valor, ",.2f")
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def renderizar_tabela_projecao(projecao):
    """Gera uma tabela acessível com os valores anuais da projeção."""
    linhas = "".join(
        "<tr><th scope=\"row\">Ano {}</th><td>{}</td></tr>".format(
            linha["ano"], escape(formatar_euros(linha["valor"]))
        )
        for linha in projecao["tabela_anual"]
    )
    return (
        '<div class="invest-table-wrap"><table class="invest-table">'
        "<thead><tr><th>Ano</th><th>Valor projetado</th></tr></thead>"
        "<tbody>{}</tbody></table></div>".format(linhas)
    )


def renderizar_resultado_etf(projecao):
    """Apresenta contribuições, retorno, custos e valor real estimados."""
    return """
        <section class="invest-result-card" aria-live="polite">
            <p class="invest-eyebrow">PROJEÇÃO HIPOTÉTICA · {anos} ANOS</p>
            <h3>Valor final nominal: {valor_final}</h3>
            <dl class="invest-quote-grid">
                <div><dt>Capital inicial</dt><dd>{inicial}</dd></div>
                <div><dt>Total de reforços</dt><dd>{contribuicoes}</dd></div>
                <div><dt>Total investido</dt><dd>{investido}</dd></div>
                <div><dt>Ganho estimado</dt><dd>{ganho}</dd></div>
                <div><dt>Rentabilidade acumulada</dt><dd>{retorno}%</dd></div>
                <div><dt>Valor após inflação estimada</dt><dd>{real}</dd></div>
                <div><dt>Impacto estimado dos custos</dt><dd>{custos}</dd></div>
                <div><dt>Rentabilidade anual usada</dt><dd>{taxa_anual}%</dd></div>
            </dl>
            {tabela}
            <p class="invest-muted">
                Valores estimados, sem impostos, dividendos ou variações reais de preço.
            </p>
        </section>
    """.format(
        anos=projecao["anos"],
        valor_final=escape(formatar_euros(projecao["valor_final"])),
        inicial=escape(formatar_euros(projecao["montante_inicial"])),
        contribuicoes=escape(formatar_euros(projecao["total_contribuicoes"])),
        investido=escape(formatar_euros(projecao["total_investido"])),
        ganho=escape(formatar_euros(projecao["ganho_estimado"])),
        retorno=escape(formatar_percentagem(projecao["retorno_acumulado"])),
        real=escape(formatar_euros(projecao["valor_final_real"])),
        custos=escape(formatar_euros(projecao["impacto_custos_estimado"])),
        taxa_anual=escape(formatar_percentagem(projecao["retorno_anual"])),
        tabela=renderizar_tabela_projecao(projecao),
    )


def renderizar_resultado_historico(historico):
    """Mostra dados históricos mensais reais retornados pela API configurada."""
    return """
        <section class="invest-result-card" aria-live="polite">
            <p class="invest-eyebrow">DADOS HISTÓRICOS · {simbolo}</p>
            <h3>Variação de preço: {variacao}%</h3>
            <dl class="invest-quote-grid">
                <div><dt>Período consultado</dt><dd>{inicio} a {fim}</dd></div>
                <div><dt>Fecho mensal inicial</dt><dd>{fecho_inicial}</dd></div>
                <div><dt>Fecho mensal final</dt><dd>{fecho_final}</dd></div>
            </dl>
            <p class="invest-muted">
                Variação entre fechos mensais completos; não inclui dividendos nem custos.
                Os preços são apresentados sem moeda porque a fonte não a identifica.
                Dados atrasados não representam uma cotação em tempo real.
            </p>
        </section>
    """.format(
        simbolo=escape(historico["simbolo"]),
        variacao=escape(formatar_percentagem(historico["variacao_percentual"])),
        inicio=escape(historico["data_inicial"].strftime("%d/%m/%Y")),
        fim=escape(historico["data_final"].strftime("%d/%m/%Y")),
        fecho_inicial=escape(formatar_numero(historico["fecho_inicial"])),
        fecho_final=escape(formatar_numero(historico["fecho_final"])),
    )


def renderizar_pagina_investimentos(
    formulario=None, mensagem="", tipo_mensagem="error",
    resultado_etf="", resultado_historico="",
):
    """Preenche o simulador de ETFs com os valores e resultados do pedido."""
    pagina = (PASTA_PROJETO / "pages" / "investing.html").read_text(encoding="utf-8")
    dados = formulario or {}
    for marcador, nome_campo in MARCADORES_INVESTIMENTO.items():
        pagina = pagina.replace(
            marcador, escape(dados.get(nome_campo, ""), quote=True)
        )
    pagina = pagina.replace(
        "__CONSULTAR_HISTORICO__",
        "checked" if dados.get("consultar_historico") == "sim" else "",
    )

    bloco_mensagem = ""
    if mensagem:
        classe = "error" if tipo_mensagem == "error" else "success"
        bloco_mensagem = (
            '<div class="invest-message {}" role="{}">{}</div>'.format(
                classe,
                "alert" if classe == "error" else "status",
                escape(mensagem),
            )
        )
    pagina = pagina.replace("<!-- MENSAGEM_INVESTIMENTO -->", bloco_mensagem)
    pagina = pagina.replace("<!-- RESULTADO_ETF -->", resultado_etf)
    pagina = pagina.replace("<!-- RESULTADO_HISTORICO -->", resultado_historico)
    return pagina


def renderizar_registo_despesas(despesas):
    """Gera resumo por categoria e tabela ordenada das despesas persistentes."""
    resultados = calcular_despesas(despesas)
    linhas_categoria = "".join(
        "<div><dt>{}</dt><dd>{}</dd></div>".format(
            escape(categoria),
            escape(formatar_euros(resultados["totais_por_categoria"][categoria])),
        )
        for categoria in CATEGORIAS_DESPESA
    )
    maior = resultados["maior_despesa"]
    maior_texto = (
        "{} · {}".format(
            escape(maior["descricao"]),
            escape(formatar_euros(maior["valor"])),
        )
        if maior else "—"
    )
    resumo = """
        <section class="expense-summary" aria-live="polite">
            <h3>Resumo das despesas</h3>
            <dl class="finance-metrics expense-metrics">
                <div><dt>Total registado</dt><dd>{total}</dd></div>
                <div><dt>Número de despesas</dt><dd>{quantidade}</dd></div>
                <div><dt>Despesa mais elevada</dt><dd>{maior}</dd></div>
                <div><dt>Média por despesa</dt><dd>{media}</dd></div>
            </dl>
            <h4>Totais por categoria</h4>
            <dl class="category-totals">{categorias}</dl>
        </section>
    """.format(
        total=escape(formatar_euros(resultados["total"])),
        quantidade=resultados["quantidade"],
        maior=maior_texto,
        media=escape(formatar_euros(resultados["media"])),
        categorias=linhas_categoria,
    )

    ordenadas = sorted(
        enumerate(resultados["despesas"]),
        key=lambda item: (item[1]["data"], item[0]),
        reverse=True,
    )
    if ordenadas:
        linhas = "".join(
            "<tr><td><time datetime=\"{data}\">{data_legivel}</time></td>"
            "<td>{descricao}</td><td>{categoria}</td><td>{valor}</td><td>"
            "<form class=\"expense-row-form\" method=\"post\" action=\"/personal_finance.html\">"
            "<input type=\"hidden\" name=\"ferramenta\" value=\"pedir_eliminacao\">"
            "<input type=\"hidden\" name=\"id_despesa\" value=\"{identificador}\">"
            "<button class=\"expense-action-button\" type=\"submit\">Eliminar</button>"
            "</form></td></tr>".format(
                data=escape(registo["data"], quote=True),
                data_legivel=escape(date.fromisoformat(registo["data"]).strftime("%d/%m/%Y")),
                descricao=escape(registo["descricao"]),
                categoria=escape(registo["categoria"]),
                valor=escape(formatar_euros(registo["valor"])),
                identificador=escape(registo["id"], quote=True),
            )
            for _, registo in ordenadas
        )
    else:
        linhas = '<tr><td class="empty-expenses" colspan="5">Ainda não há despesas registadas.</td></tr>'

    tabela = """
        <div class="expense-table-wrap">
            <table class="expense-table">
                <thead><tr><th>Data</th><th>Descrição</th><th>Categoria</th>
                    <th>Valor</th><th>Ação</th></tr></thead>
                <tbody>{linhas}</tbody>
            </table>
        </div>
        <form class="expense-clear-form" method="post" action="/personal_finance.html">
            <input type="hidden" name="ferramenta" value="pedir_limpeza">
            <button class="expense-action-button expense-clear-button" type="submit">
                Limpar todos os registos
            </button>
        </form>
    """.format(linhas=linhas)
    return resumo, tabela


def renderizar_confirmacao_eliminacao(despesa):
    """Pede uma confirmação explícita antes de apagar uma despesa."""
    return """
        <section class="finance-message finance-confirmation" aria-labelledby="confirm-title">
            <h2 id="confirm-title">Confirmar eliminação</h2>
            <p>Queres eliminar «{descricao}» ({valor})?</p>
            <form method="post" action="/personal_finance.html">
                <input type="hidden" name="ferramenta" value="eliminar_confirmado">
                <input type="hidden" name="id_despesa" value="{identificador}">
                <button class="finance-primary-button" type="submit">Confirmar eliminação</button>
                <a class="expense-cancel-link" href="/personal_finance.html#registo-despesas">Cancelar</a>
            </form>
        </section>
    """.format(
        descricao=escape(despesa["descricao"]),
        valor=escape(formatar_euros(Decimal(despesa["valor"]))),
        identificador=escape(despesa["id"], quote=True),
    )


def renderizar_confirmacao_limpeza():
    """Pede uma confirmação explícita antes de limpar todo o histórico."""
    return """
        <section class="finance-message finance-confirmation" aria-labelledby="confirm-clear-title">
            <h2 id="confirm-clear-title">Confirmar limpeza do histórico</h2>
            <p>Esta ação elimina permanentemente todas as despesas guardadas no ficheiro local.</p>
            <form method="post" action="/personal_finance.html">
                <input type="hidden" name="ferramenta" value="limpar_confirmado">
                <button class="finance-primary-button" type="submit">Confirmar limpeza</button>
                <a class="expense-cancel-link" href="/personal_finance.html#registo-despesas">Cancelar</a>
            </form>
        </section>
    """


def renderizar_pagina_financas(
    despesas, formulario=None, mensagem="", tipo_mensagem="success",
    confirmacao="",
):
    """Insere os registos, mensagens e valores do formulário de despesas."""
    pagina = (PASTA_PROJETO / "personal_finance.html").read_text(encoding="utf-8")
    dados = formulario or {}
    for marcador, nome_campo in MARCADORES_FINANCAS.items():
        valor = dados.get(nome_campo, "")
        if nome_campo == "data_despesa" and nome_campo not in dados:
            valor = date.today().isoformat()
        pagina = pagina.replace(marcador, escape(valor, quote=True))

    categorias_marcadores = {
        "Alimentação": "__CAT_ALIMENTACAO__",
        "Habitação": "__CAT_HABITACAO__",
        "Transportes": "__CAT_TRANSPORTES__",
        "Saúde": "__CAT_SAUDE__",
        "Educação": "__CAT_EDUCACAO__",
        "Lazer": "__CAT_LAZER__",
        "Compras": "__CAT_COMPRAS__",
        "Subscrições": "__CAT_SUBSCRICOES__",
        "Outros": "__CAT_OUTROS__",
    }
    for categoria, marcador in categorias_marcadores.items():
        pagina = pagina.replace(
            marcador,
            "selected" if dados.get("categoria_despesa") == categoria else "",
        )

    bloco_mensagem = ""
    if mensagem:
        bloco_mensagem = '<div class="finance-message {}" role="{}">{}</div>'.format(
            "error" if tipo_mensagem == "error" else "success",
            "alert" if tipo_mensagem == "error" else "status",
            escape(mensagem),
        )
    resumo, tabela = renderizar_registo_despesas(despesas)
    pagina = pagina.replace("<!-- MENSAGEM_FINANCAS -->", bloco_mensagem)
    pagina = pagina.replace("<!-- CONFIRMACAO_ACAO -->", confirmacao)
    pagina = pagina.replace("<!-- RESUMO_DESPESAS -->", resumo)
    return pagina.replace("<!-- TABELA_DESPESAS -->", tabela)


class FinanceLabHandler(BaseHTTPRequestHandler):
    """Atende as páginas e formulários dos três recursos ativos."""

    def send_error(self, code, message=None, explain=None):
        """Devolve erros HTTP numa página simples e compreensível em português."""
        mensagens = {
            400: "O pedido é inválido.",
            404: "A página ou rota solicitada não existe.",
            405: "Este método não é permitido para o recurso solicitado.",
            411: "O pedido não indicou o seu tamanho.",
            413: "O conteúdo enviado é demasiado grande.",
            414: "O endereço pedido é demasiado longo.",
            415: "O formato enviado não é suportado.",
            500: "O servidor não conseguiu concluir o pedido.",
            501: "Este método HTTP não é suportado.",
        }
        detalhe = message or mensagens.get(code, "O pedido não pôde ser processado.")
        conteudo = (
            '<!DOCTYPE html><html lang="pt-PT"><meta charset="utf-8">'
            "<title>Erro HTTP {}</title><h1>Erro HTTP {}</h1><p>{}</p></html>"
        ).format(code, code, escape(str(detalhe))).encode("utf-8")
        self.log_error("Erro HTTP %s: %s", code, detalhe)
        self.close_connection = True
        cabecalhos = {"Allow": "GET"} if code == 405 else None
        self.enviar_conteudo(
            conteudo, "text/html; charset=utf-8", code, cabecalhos=cabecalhos
        )

    def enviar_html(self, pagina, codigo=200):
        conteudo = pagina.encode("utf-8")
        self.enviar_conteudo(conteudo, "text/html; charset=utf-8", codigo)

    def enviar_conteudo(
        self, conteudo, tipo_conteudo, codigo=200, cache="no-store",
        cabecalhos=None,
    ):
        """Escreve a resposta e ignora apenas ligações canceladas pelo navegador."""
        try:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo_conteudo)
            self.send_header("Content-Length", str(len(conteudo)))
            self.send_header("Cache-Control", cache)
            self.send_header("X-Content-Type-Options", "nosniff")
            for nome, valor in (cabecalhos or {}).items():
                self.send_header(nome, valor)
            self.end_headers()
            self.wfile.write(conteudo)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            self.close_connection = True

    def ler_formulario(self):
        """Lê um formulário URL-encoded e rejeita pedidos demasiado grandes."""
        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            self.send_error(415, "O formulário tem de usar codificação URL-encoded.")
            return None
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "Pedido inválido")
            return None
        if tamanho <= 0 or tamanho > 16384:
            self.send_error(400, "Tamanho do formulário inválido")
            return None
        try:
            corpo = self.rfile.read(tamanho).decode("utf-8")
        except UnicodeDecodeError:
            self.send_error(400, "O formulário contém texto inválido")
            return None
        campos = parse_qs(corpo, keep_blank_values=True)
        return {nome: valores[0] for nome, valores in campos.items() if valores}

    def do_GET(self):
        caminho_url = urlsplit(self.path).path
        if caminho_url == "/favicon.ico":
            self.send_response(204)
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            return
        ficheiro_publico = ENDERECOS_PUBLICOS.get(caminho_url)
        if ficheiro_publico is None:
            self.send_error(404, "Página não encontrada")
            return

        if ficheiro_publico == "pages/investing.html":
            self.enviar_html(renderizar_pagina_investimentos())
            return
        if ficheiro_publico == "personal_finance.html":
            try:
                despesas = carregar_despesas()
                pagina = renderizar_pagina_financas(despesas)
            except (OSError, ValueError) as erro:
                self.send_error(500, str(erro))
                return
            self.enviar_html(pagina)
            return

        caminho_ficheiro = PASTA_PROJETO / ficheiro_publico
        try:
            conteudo = caminho_ficheiro.read_bytes()
        except OSError:
            self.send_error(500, "Não foi possível ler o recurso solicitado.")
            return
        tipo_conteudo = (
            "text/css; charset=utf-8" if ficheiro_publico.endswith(".css")
            else "application/javascript; charset=utf-8"
            if ficheiro_publico.endswith(".js")
            else "text/html; charset=utf-8"
        )
        self.enviar_conteudo(conteudo, tipo_conteudo, cache="no-store")

    def do_POST(self):
        caminho_url = urlsplit(self.path).path
        if caminho_url in (
            "/money_catcher", "/money_catcher.html", "/trading", "/trading.html"
        ):
            self.send_error(405, "O Money Catcher recebe apenas pedidos GET.")
            return
        caminhos_validos = (
            "/investing", "/personal_finance.html", "/financas_pessoais.html",
        )
        if caminho_url not in caminhos_validos:
            self.send_error(404, "Página não encontrada")
            return
        formulario = self.ler_formulario()
        if formulario is None:
            return

        if caminho_url == "/investing":
            self.processar_formulario_investimentos(formulario)
        else:
            self.processar_formulario_financas(formulario)

    def processar_formulario_investimentos(self, formulario):
        if formulario.get("ferramenta") != "etf":
            self.enviar_html(
                renderizar_pagina_investimentos(
                    formulario, "Seleciona o simulador de ETFs."
                ),
                codigo=400,
            )
            return
        try:
            projecao = calcular_projecao(
                formulario.get("montante_etf", ""),
                formulario.get("aporte_etf", ""),
                formulario.get("anos_etf", ""),
                formulario.get("retorno_etf", ""),
                formulario.get("custos_etf", ""),
                formulario.get("inflacao_etf", ""),
            )
        except ValueError as erro_validacao:
            self.enviar_html(
                renderizar_pagina_investimentos(formulario, str(erro_validacao)),
                codigo=400,
            )
            return

        resultado_historico = ""
        mensagem = ""
        if formulario.get("consultar_historico") == "sim":
            try:
                historico = obter_historico_mensal(
                    formulario.get("simbolo_etf", "")
                )
                resultado_historico = renderizar_resultado_historico(historico)
            except (ErroDadosMercado, ValueError) as erro_mercado:
                mensagem = (
                    "A consulta histórica não ficou disponível: {} "
                    "A projeção manual foi calculada normalmente."
                ).format(erro_mercado)

        self.enviar_html(
            renderizar_pagina_investimentos(
                formulario,
                mensagem,
                resultado_etf=renderizar_resultado_etf(projecao),
                resultado_historico=resultado_historico,
            )
        )

    def processar_formulario_financas(self, formulario):
        ferramenta = formulario.get("ferramenta", "")
        try:
            despesas = carregar_despesas()
        except (OSError, ValueError) as erro:
            self.send_error(500, str(erro))
            return

        mensagem = ""
        tipo_mensagem = "success"
        confirmacao = ""
        dados_a_mostrar = formulario
        try:
            if ferramenta == "adicionar":
                novo_registo = adicionar_despesa(
                    formulario.get("descricao_despesa", ""),
                    formulario.get("categoria_despesa", ""),
                    formulario.get("valor_despesa", ""),
                    formulario.get("data_despesa", ""),
                )
                guardar_despesas(despesas + [novo_registo])
                despesas.append(novo_registo)
                mensagem = "Despesa adicionada ao teu registo persistente."
                dados_a_mostrar = {}
            elif ferramenta == "pedir_eliminacao":
                identificador = formulario.get("id_despesa", "")
                despesa = next(
                    (item for item in despesas if item["id"] == identificador),
                    None,
                )
                if despesa is None:
                    raise ValueError("A despesa selecionada já não existe.")
                confirmacao = renderizar_confirmacao_eliminacao(despesa)
                dados_a_mostrar = {}
            elif ferramenta == "eliminar_confirmado":
                restantes = remover_despesa(
                    despesas, formulario.get("id_despesa", "")
                )
                guardar_despesas(restantes)
                despesas = restantes
                mensagem = "A despesa selecionada foi eliminada."
                dados_a_mostrar = {}
            elif ferramenta == "pedir_limpeza":
                if despesas:
                    confirmacao = renderizar_confirmacao_limpeza()
                else:
                    mensagem = "O registo já não contém despesas."
                dados_a_mostrar = {}
            elif ferramenta == "limpar_confirmado":
                guardar_despesas([])
                despesas = []
                mensagem = "Todos os registos de despesas foram eliminados."
                dados_a_mostrar = {}
            else:
                raise ValueError("Seleciona uma ação válida para o registo de despesas.")
        except ValueError as erro_validacao:
            mensagem = str(erro_validacao)
            tipo_mensagem = "error"
            dados_a_mostrar = formulario
        except OSError as erro:
            self.send_error(500, "Não foi possível guardar o registo de despesas: {}".format(erro))
            return

        self.enviar_html(
            renderizar_pagina_financas(
                despesas,
                dados_a_mostrar,
                mensagem,
                tipo_mensagem,
                confirmacao,
            ),
            codigo=400 if tipo_mensagem == "error" else 200,
        )


if __name__ == "__main__":
    try:
        servidor = FinanceLabHTTPServer((ANFITRIAO, PORTA), FinanceLabHandler)
    except OSError as erro:
        if erro.errno == errno.EADDRINUSE:
            raise SystemExit(
                "A porta {} está ocupada. Fecha o processo que a está a usar "
                "e volta a executar python server.py.".format(PORTA)
            )
        raise

    print(
        "FinanceLab disponível em http://localhost:{}/".format(PORTA),
        flush=True,
    )
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor FinanceLab encerrado.")
    finally:
        servidor.server_close()
