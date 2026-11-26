
Dashboard Web: FinanceLab

Disciplina: Oficina de Multimédia - 12.o Ano - CRSI

Ano Letivo: 2026/2027

Autor: Manuel Sousa nº14
Turma: 12º A3

Link da Aplicação Web: http://localhost:8000/ 
(Antes, no terminal VSCode: cd .\Projeto_23_11; python server.py;)

1. Visão Geral do Projeto
Descrição: A FinanceLab é uma página web, programada e,m HMTL, CSS e Python, que tem como objetivo compreender, ao simular, investimentos em ETFs, usando o Laboratório de Investimentos. A FinanceLab tem projetada também uma lista de despesas para organização pessoal nas Finanças Pessoais. No widget final, Money Catcher, está programado um jogo para aliviar o stress :)

Proposta Escolhida: Proposta 1 

2. Estrutura do Código e Funcionalidades Integradas
Para o desenvolvimento da Dashboard recorri a código HTML dado em aula, na criação dos widgets, mas para código Python e CSS, recorri a IA.

3. Registo de Utilização da IA
Para demonstrares como trabalhaste em parceria com o Copilot, Gemini, Claude,
Mistral, etc., regista:
1. Prompt para conversão Web/HTML

-Cria um Dashboard web com o nome FinanceLab, utilizando HTML, CSS e Python. Organiza o projeto em diferentes secções, com uma página inicial e ferramentas financeiras interativas. Utiliza um design moderno, responsivo e profissional, com uma identidade visual relacionada com o setor financeiro. Mantém o código organizado, comentado e fácil de compreender.

2. Prompt para ampliação e construção de funcionalidades

-Desenvolve um Simulador de ETFs que permita introduzir capital inicial, contribuições mensais, rentabilidade anual estimada e duração do investimento e outros usos que aches pertinentes. Utiliza Python para realizar os cálculos e HTML e CSS para apresentar os resultados. Implementa uma projeção clara e organizada.
-Cria um jogo em que o jogador controla um recipiente e tem de apanhar moedas e notas que caem do topo do ecrã, evitando obstáculos inesperados. Quero que o jogo fique um aspeto de arcade moderno, mas que continuasse a combinar com o design azul-escuro do FinanceLab. Quero que seja realmente funcional no navegador.
-Quero que analises o meu código como se estivesses a fazer uma revisão antes da entrega do projeto. Verifica todas as páginas, os botões, os links e as funcionalidades. Quero que confirmes se o Simulador de ETFs calcula corretamente, se o Registo de Despesas permite adicionar e eliminar despesas e se o Money Catcher funciona como esperado. Analisa também o aspeto visual, a organização dos elementos e a sua utilizaçao. Explica os problemas e corrige-os sem alterar o design ou as funcionalidades que já estão a funcionar.

3. Dificuldades e erros corrigidos com a IA:
-Quero que analises o código HTML, CSS e Python, especialmente no servidor. Verifica erros como páginas que não abrem, botões que não respondem, o nao envio dos dados e páginas que atualizam inesperadamente. Também quero que verifiques os erros HTTP 405 e ERR_CONNECTION_REFUSED que apareceram durante o uso da página no browser. Identifica a causa de cada erro, depois implementa a correção e testa se ficou resolvido. Tem cuidado para não estragar as funcionalidades que já estão a funcionar e explica-me, de forma simples, o que estava errado e como foi corrigido.
   
4. Otimização de Layout: O que sugeriste à IA para alterar no design - cores,
margens, fontes, botões?
No meu dashboard, fui eu que personalizei manualmente as cores, fontes e designs da página. Já os botoes, foi o Copilot que os criou automaticamente.

5. Estrutura de Ficheiros do Repositório
Listagem simples dos ficheiros presentes na pasta:
1. paginainicial.html – página principal do Dashboard / Web App; investimentos.html - página HTML do widget Laboratório de Investimentos; finanças_pessoais / finanças_pessoais2.html - página HTML do widget Finanças Pessoais; money_catcher.html - página HTML do mini-jogo
2. server.py - Ficheiro principal da aplicação.
3. paginainicial.css - Folha de estilos para o layout Web
4. README.md - Este relatório de projeto.
   
6. Reflexão Crítica e Aprendizagem
Ao longo do desenvolvimento deste projeto, considero que um dos aspetos que correu melhor foi a integração da IA e o suporte que nos proporciona, especialmente no desenvolvimento de código mais complexo. Gostei particularmente de desenvolver o Money Catcher, porque permitiu acrescentar uma componente mais criativa e interativa ao projeto, tornando a plataforma mais dinâmica ,interessante e aplativa.
A maior dificuldade que enfrentei foi garantir que todas as funcionalidades funcionavam corretamente em conjunto, sobretudo na comunicação entre HTML e Python e na resolução de erros do servidor. Surgiram problemas como o erro HTTP 405, dificuldades em iniciar o servidor local e atualizações inesperadas da página durante a utilização do jogo. Estas situações obrigaram-me a analisar o código, testar diferentes soluções e corrigir vários erros. A IA do GitHub Copilot, ajudou-me imenso a programar, também com ajuda do ChatGPT, pois permitiu-me desenvolver o código com maior rapidez, encontrar erros e compreender diferentes formas de resolver problemas. No entanto, percebi que não basta aceitar o código criado, mas também é necessário analisá-lo, testá-lo e compreender o seu funcionamento. No final, este projeto permitiu-me melhorar as minhas competências de programação, desenvolver o pensamento lógico e perceber como a IA pode ser uma ferramenta de apoio à aprendizagem e à resolução de problemas.
