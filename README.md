# FinanceLab

FinanceLab é um projeto educativo de literacia financeira com três secções: projeção de ETFs, registo de despesas e o mini-jogo Money Catcher.

## Requisitos e execução

- Python 3.9 ou superior.
- Não são necessárias dependências nem frameworks externas.

Na pasta principal, inicia o servidor:

```powershell
python server.py
```

Abre no navegador o endereço indicado pelo terminal: `http://localhost:8000/`. A página inicial também está disponível em `/index.html`; ambas usam a página existente `paginainicial.html`.

Usa o servidor Python para abrir o projeto. O VS Code Live Server e os endereços `file://` não executam os cálculos Python nem guardam as despesas.

## Secções

- **Página inicial (`/`)**: navegação para as três secções.
- **Simulador de ETFs (`/pages/investing.html`)**: calcula uma projeção hipotética com capital inicial, reforços mensais, rentabilidade, custos e inflação. Uma consulta histórica opcional requer uma chave Alpha Vantage no ambiente; sem chave ou rede, a projeção manual continua a funcionar.
- **Finanças Pessoais (`/personal_finance.html`)**: regista, resume e elimina despesas. Os dados ficam em `data/despesas.json` e mantêm-se após reiniciar o servidor. Esse ficheiro é ignorado pelo Git para evitar publicar dados financeiros pessoais.
- **Money Catcher (`/money_catcher`)**: jogo com moedas, notas, bónus e despesas. O servidor Python serve a página; a interação em tempo real usa JavaScript simples, local e exclusivo do jogo. As setas ou A/D e os botões no ecrã movem o cesto sem recarregar a página. O recorde fica no armazenamento local do navegador (`localStorage`) para a mesma origem.

O estado de uma partida ativa existe no navegador e termina se a página for recarregada ou fechada; o recorde guardado não é afetado. O recorde é específico do navegador e da origem (nome do anfitrião e porta).

## Estrutura

```text
FinanceLab/
├── server.py
├── money_catcher.js
├── paginainicial.html
├── paginainicial.css
├── moneycatcher.html
├── personal_finance.html
├── pages/
│   └── investing.html
├── python/
│   ├── investing.py
│   └── personal_finance.py
├── data/                 # dados JSON locais; ignorados pelo Git
└── tests/
    └── test_financelab.py
```

O projeto usa Python e a biblioteca padrão `http.server` no servidor, HTML e CSS nas páginas e JavaScript simples apenas no Money Catcher. Não requer `requirements.txt`.

## Testes

Executa os testes automáticos na pasta principal:

```powershell
python -m unittest discover -s tests -v
```

Os testes exercitam cálculos financeiros, validação, persistência JSON, respostas HTTP, navegação e os recursos servidos pelo servidor.

## Publicar no GitHub

1. Confirma que `data/despesas.json`, chaves API e outros dados privados não serão publicados. Os ficheiros JSON locais da pasta `data` já estão no `.gitignore`.
2. Cria um repositório vazio no GitHub, sem adicionar outro README.
3. Na pasta do projeto, inicializa o Git e liga o repositório remoto:

```powershell
git init
git add .
git status
git commit -m "Preparar FinanceLab para entrega"
git branch -M main
git remote add origin https://github.com/UTILIZADOR/FinanceLab.git
git push -u origin main
```

Substitui o endereço de exemplo pelo endereço do teu repositório. Revê `git status` antes do commit e não coloques chaves API ou dados pessoais no README ou no código.

## Aviso educativo

O FinanceLab não executa ordens, não movimenta dinheiro e não constitui aconselhamento financeiro. O servidor local destina-se a avaliação e uso educativo; não o publiques diretamente na Internet.
