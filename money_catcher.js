// Controlos e regras do Money Catcher, executados apenas nesta página.
(() => {
    "use strict";

    const DURACAO_MS = 60_000;
    const VIDAS_INICIAIS = 3;
    const NUMERO_PISTAS = 7;
    const CHAVE_RECORDE = "financelab.money-catcher.best.v1";
    const ALTURA_OBJETO = 38;

    const objetosPositivos = [
        { texto: "1 €", pontos: 1, classe: "coin-one", nome: "Moeda de 1 euro" },
        { texto: "1 €", pontos: 1, classe: "coin-one", nome: "Moeda de 1 euro" },
        { texto: "1 €", pontos: 1, classe: "coin-one", nome: "Moeda de 1 euro" },
        { texto: "2 €", pontos: 2, classe: "coin-two", nome: "Moeda de 2 euros" },
        { texto: "2 €", pontos: 2, classe: "coin-two", nome: "Moeda de 2 euros" },
        { texto: "5 €", pontos: 5, classe: "note-five", nome: "Nota de 5 euros" },
        { texto: "+10", pontos: 10, classe: "bonus", nome: "Bónus de 10 pontos" },
    ];
    const objetosNegativos = [
        { texto: "Fatura", vidas: 1, classe: "bill", nome: "Fatura: menos uma vida" },
        {
            texto: "Imprevisto",
            vidas: 2,
            classe: "unexpected-expense",
            nome: "Despesa inesperada: menos duas vidas",
        },
    ];

    const elementos = {
        inicio: document.getElementById("game-intro"),
        jogo: document.getElementById("game-play"),
        fim: document.getElementById("game-over"),
        tabuleiro: document.getElementById("game-board"),
        cesto: document.getElementById("game-catcher"),
        pontuacao: document.getElementById("score-value"),
        vidas: document.getElementById("lives-value"),
        tempo: document.getElementById("time-value"),
        melhorAtivo: document.getElementById("active-best-score"),
        melhorInicial: document.getElementById("intro-best-score"),
        melhorFinal: document.getElementById("final-best-score"),
        pontuacaoFinal: document.getElementById("final-score"),
        motivoFim: document.getElementById("end-reason"),
        mensagemArmazenamento: document.getElementById("storage-message"),
        comecar: document.getElementById("start-game"),
        recomecar: document.getElementById("restart-game"),
        esquerda: document.getElementById("move-left"),
        direita: document.getElementById("move-right"),
    };

    const estado = {
        ativa: false,
        pontuacao: 0,
        vidas: VIDAS_INICIAIS,
        melhor: 0,
        posicaoCesto: Math.floor(NUMERO_PISTAS / 2),
        objetos: [],
        inicio: 0,
        ultimoQuadro: 0,
        ultimoSegundo: DURACAO_MS / 1000,
        acumuladorAparecimento: 0,
        direcaoTeclado: 0,
    };

    function mostrarErroArmazenamento(mensagem) {
        elementos.mensagemArmazenamento.textContent = mensagem;
        elementos.mensagemArmazenamento.hidden = false;
    }

    function lerRecorde() {
        try {
            const valor = window.localStorage.getItem(CHAVE_RECORDE);
            if (valor === null) {
                return 0;
            }
            const pontuacao = Number(valor);
            if (!Number.isSafeInteger(pontuacao) || pontuacao < 0) {
                throw new Error("O valor guardado não é uma pontuação válida.");
            }
            return pontuacao;
        } catch (erro) {
            mostrarErroArmazenamento(
                "O navegador não permitiu ler o recorde; a partida continua disponível."
            );
            return 0;
        }
    }

    function atualizarMelhorPontuacao() {
        const pontuacaoApresentada = String(estado.melhor);
        elementos.melhorInicial.textContent = pontuacaoApresentada;
        elementos.melhorAtivo.textContent = pontuacaoApresentada;
        elementos.melhorFinal.textContent = pontuacaoApresentada;
    }

    function guardarNovoRecorde() {
        if (estado.pontuacao <= estado.melhor) {
            return;
        }
        estado.melhor = estado.pontuacao;
        atualizarMelhorPontuacao();
        try {
            window.localStorage.setItem(CHAVE_RECORDE, String(estado.melhor));
        } catch (erro) {
            mostrarErroArmazenamento(
                "A pontuação foi atualizada, mas o navegador não permitiu guardar o novo recorde."
            );
        }
    }

    function atualizarCesto() {
        const centro = (estado.posicaoCesto + 0.5) / NUMERO_PISTAS * 100;
        elementos.cesto.style.left = `${centro}%`;
    }

    function moverCesto(deslocamento) {
        estado.posicaoCesto = Math.max(
            0,
            Math.min(NUMERO_PISTAS - 1, estado.posicaoCesto + deslocamento)
        );
        atualizarCesto();
    }

    function atualizarIndicadores() {
        elementos.pontuacao.textContent = String(estado.pontuacao);
        elementos.vidas.textContent =
            "♥".repeat(estado.vidas) + "♡".repeat(VIDAS_INICIAIS - estado.vidas);
        elementos.vidas.setAttribute(
            "aria-label",
            `${estado.vidas} ${estado.vidas === 1 ? "vida" : "vidas"} restantes`
        );
    }

    function criarObjeto() {
        const eNegativo = Math.random() < 0.2;
        const lista = eNegativo ? objetosNegativos : objetosPositivos;
        const tipo = lista[Math.floor(Math.random() * lista.length)];
        const elemento = document.createElement("span");
        const pista = Math.floor(Math.random() * NUMERO_PISTAS);

        elemento.className = `falling-object ${tipo.classe}`;
        elemento.textContent = tipo.texto;
        elemento.setAttribute("aria-label", tipo.nome);
        elemento.style.left = `${(pista + 0.5) / NUMERO_PISTAS * 100}%`;
        elementos.tabuleiro.appendChild(elemento);
        estado.objetos.push({ elemento, pista, tipo, posicaoY: -ALTURA_OBJETO });
    }

    function removerObjeto(indice) {
        const [objeto] = estado.objetos.splice(indice, 1);
        objeto.elemento.remove();
    }

    function terminarJogo() {
        estado.ativa = false;
        estado.direcaoTeclado = 0;
        estado.objetos.forEach((objeto) => objeto.elemento.remove());
        estado.objetos = [];
        document.body.classList.remove("game-running");
        elementos.jogo.hidden = true;
        elementos.fim.hidden = false;
        elementos.pontuacaoFinal.textContent =
            `Pontuação final: ${estado.pontuacao}`;
        elementos.motivoFim.textContent = estado.vidas === 0
            ? "Ficaste sem vidas."
            : "O tempo terminou.";
        guardarNovoRecorde();
        atualizarMelhorPontuacao();
    }

    function iniciarJogo() {
        if (estado.ativa) {
            return;
        }
        estado.ativa = true;
        estado.pontuacao = 0;
        estado.vidas = VIDAS_INICIAIS;
        estado.posicaoCesto = Math.floor(NUMERO_PISTAS / 2);
        estado.acumuladorAparecimento = 0;
        estado.direcaoTeclado = 0;
        estado.objetos.forEach((objeto) => objeto.elemento.remove());
        estado.objetos = [];
        estado.inicio = performance.now();
        estado.ultimoQuadro = estado.inicio;
        estado.ultimoSegundo = DURACAO_MS / 1000;
        elementos.inicio.hidden = true;
        elementos.fim.hidden = true;
        elementos.jogo.hidden = false;
        elementos.mensagemArmazenamento.hidden = true;
        document.body.classList.add("game-running");
        atualizarCesto();
        atualizarIndicadores();
        elementos.tempo.textContent = String(estado.ultimoSegundo);
        atualizarMelhorPontuacao();
        requestAnimationFrame(atualizarJogo);
    }

    function atualizarJogo(instante) {
        if (!estado.ativa) {
            return;
        }
        const delta = Math.min((instante - estado.ultimoQuadro) / 1000, 0.05);
        const decorrido = instante - estado.inicio;
        estado.ultimoQuadro = instante;

        if (decorrido >= DURACAO_MS) {
            elementos.tempo.textContent = "0";
            terminarJogo();
            return;
        }

        const segundos = Math.ceil((DURACAO_MS - decorrido) / 1000);
        if (segundos !== estado.ultimoSegundo) {
            estado.ultimoSegundo = segundos;
            elementos.tempo.textContent = String(segundos);
        }

        if (estado.direcaoTeclado !== 0) {
            estado.posicaoCesto = Math.max(
                0,
                Math.min(
                    NUMERO_PISTAS - 1,
                    estado.posicaoCesto + estado.direcaoTeclado * delta * 4
                )
            );
            atualizarCesto();
        }

        estado.acumuladorAparecimento += delta;
        const intervalo = Math.max(0.35, 1 - estado.pontuacao * 0.012);
        if (estado.acumuladorAparecimento >= intervalo) {
            estado.acumuladorAparecimento -= intervalo;
            criarObjeto();
        }

        const velocidade = 145 + Math.min(estado.pontuacao * 4, 190);
        const alturaTabuleiro = elementos.tabuleiro.clientHeight;
        const limiteApanha = alturaTabuleiro - 52;
        for (let indice = estado.objetos.length - 1; indice >= 0; indice -= 1) {
            const objeto = estado.objetos[indice];
            objeto.posicaoY += velocidade * delta;
            objeto.elemento.style.transform =
                `translate(-50%, ${objeto.posicaoY}px)`;

            if (objeto.posicaoY + ALTURA_OBJETO >= limiteApanha) {
                if (Math.abs(estado.posicaoCesto - objeto.pista) < 0.58) {
                    if (objeto.tipo.pontos) {
                        estado.pontuacao += objeto.tipo.pontos;
                    } else {
                        estado.vidas = Math.max(0, estado.vidas - objeto.tipo.vidas);
                    }
                    atualizarIndicadores();
                    removerObjeto(indice);
                    if (estado.vidas === 0) {
                        terminarJogo();
                        return;
                    }
                } else if (objeto.posicaoY > alturaTabuleiro) {
                    removerObjeto(indice);
                }
            }
        }
        requestAnimationFrame(atualizarJogo);
    }

    function direcaoDaTecla(tecla) {
        if (tecla === "ArrowLeft" || tecla.toLowerCase() === "a") {
            return -1;
        }
        if (tecla === "ArrowRight" || tecla.toLowerCase() === "d") {
            return 1;
        }
        return 0;
    }

    function tratarTeclaPremida(evento) {
        const direcao = direcaoDaTecla(evento.key);
        if (!estado.ativa || direcao === 0) {
            return;
        }
        evento.preventDefault();
        estado.direcaoTeclado = direcao;
    }

    function tratarTeclaSolta(evento) {
        if (direcaoDaTecla(evento.key) === estado.direcaoTeclado) {
            estado.direcaoTeclado = 0;
        }
    }

    estado.melhor = lerRecorde();
    atualizarMelhorPontuacao();
    elementos.comecar.addEventListener("click", iniciarJogo);
    elementos.recomecar.addEventListener("click", iniciarJogo);
    elementos.esquerda.addEventListener("click", () => moverCesto(-1));
    elementos.direita.addEventListener("click", () => moverCesto(1));
    document.addEventListener("keydown", tratarTeclaPremida);
    document.addEventListener("keyup", tratarTeclaSolta);
    window.addEventListener("blur", () => {
        estado.direcaoTeclado = 0;
    });
})();
