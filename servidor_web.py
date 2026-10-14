import http.server
import json
import socket
import threading
import webbrowser
import math
import numpy as np

from simulador_passos import (
    compilar_funcao,
    gerar_passos_bisseccao,
    gerar_passos_falsa_posicao,
    gerar_passos_newton,
    gerar_passos_secante
)
from medicao import executar_comparativo
from gerador_relatorio import exportar_para_excel, gerar_graficos

# HTML Template com o Design System autêntico
HTML_SHADCN = """<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Simulador de Zeros de Funções</title>
  
  <!-- Fontes Inter & Tailwind CSS CDN -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Plotly.js para gráficos interativos 60fps -->
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          },
          colors: {
            border: "hsl(var(--border))",
            input: "hsl(var(--input))",
            ring: "hsl(var(--ring))",
            background: "hsl(var(--background))",
            foreground: "hsl(var(--foreground))",
            primary: {
              DEFAULT: "hsl(var(--primary))",
              foreground: "hsl(var(--primary-foreground))",
            },
            secondary: {
              DEFAULT: "hsl(var(--secondary))",
              foreground: "hsl(var(--secondary-foreground))",
            },
            muted: {
              DEFAULT: "hsl(var(--muted))",
              foreground: "hsl(var(--muted-foreground))",
            },
            accent: {
              DEFAULT: "hsl(var(--accent))",
              foreground: "hsl(var(--accent-foreground))",
            },
            card: {
              DEFAULT: "hsl(var(--card))",
              foreground: "hsl(var(--card-foreground))",
            },
          }
        }
      }
    }
  </script>

  <style>
    :root {
      --background: 0 0% 100%;
      --foreground: 240 10% 3.9%;
      --card: 0 0% 100%;
      --card-foreground: 240 10% 3.9%;
      --primary: 240 5.9% 10%;
      --primary-foreground: 0 0% 98%;
      --secondary: 240 4.8% 95.9%;
      --secondary-foreground: 240 5.9% 10%;
      --muted: 240 4.8% 95.9%;
      --muted-foreground: 240 3.8% 46.1%;
      --accent: 240 4.8% 95.9%;
      --accent-foreground: 240 5.9% 10%;
      --border: 240 5.9% 90%;
      --input: 240 5.9% 90%;
      --ring: 240 5.9% 10%;
    }
    .dark {
      --background: 240 10% 3.9%;
      --foreground: 0 0% 98%;
      --card: 240 10% 3.9%;
      --card-foreground: 0 0% 98%;
      --primary: 0 0% 98%;
      --primary-foreground: 240 5.9% 10%;
      --secondary: 240 3.7% 15.9%;
      --secondary-foreground: 0 0% 98%;
      --muted: 240 3.7% 15.9%;
      --muted-foreground: 240 5% 64.9%;
      --accent: 240 3.7% 15.9%;
      --accent-foreground: 0 0% 98%;
      --border: 240 3.7% 15.9%;
      --input: 240 3.7% 15.9%;
      --ring: 240 4.9% 83.9%;
    }
    body {
      background-color: hsl(var(--background));
      color: hsl(var(--foreground));
      font-feature-settings: "rlig" 1, "calt" 1;
    }
    /* Estilização de scrollbar fina */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: hsl(var(--muted)); border-radius: 4px; }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans antialiased selection:bg-primary selection:text-primary-foreground">

  <!-- Navbar Superior (shadcn style) -->
  <header class="sticky top-0 z-40 w-full border-b border-border/60 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
    <div class="container flex h-14 max-w-screen-2xl items-center justify-between px-6">
      <div class="flex items-center gap-2.5">
        <span class="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground font-mono font-bold text-xs shadow-sm">f(x)</span>
        <span class="font-semibold tracking-tight text-base text-foreground">Simulador de Zeros</span>
      </div>

      <div class="flex items-center gap-3">
        <!-- Toggle Dark/Light Mode -->
        <button id="themeToggleBtn" onclick="toggleTheme()" class="inline-flex h-9 w-9 items-center justify-center rounded-md border border-input bg-background text-foreground shadow-sm hover:bg-accent hover:text-accent-foreground transition-colors" title="Alternar Tema">
          <i data-lucide="sun" id="sunIcon" class="h-4 w-4"></i>
          <i data-lucide="moon" id="moonIcon" class="h-4 w-4 hidden"></i>
        </button>
      </div>
    </div>
  </header>

  <!-- Conteúdo Principal em Grid Responsivo -->
  <main class="flex-1 container max-w-screen-2xl p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

    <!-- COLUNA ESQUERDA: Configurações e Controles (4 cols) -->
    <div class="lg:col-span-4 flex flex-col gap-5">

      <!-- Card Unificado: Modo de Entrada da Equação -->
      <div class="rounded-xl border border-border bg-card p-5 shadow-sm flex flex-col gap-4">
        
        <!-- Tabs Principais: Pré-definido vs Digitação Livre -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <h2 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <i data-lucide="sliders" class="h-3.5 w-3.5"></i> Modo de Entrada
            </h2>
            <span id="badgeModo" class="text-[10px] font-medium text-blue-500 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-full">Problema Pré-definido</span>
          </div>

          <div class="grid grid-cols-2 p-1 bg-muted rounded-lg text-xs font-medium">
            <button id="tabModoPre" onclick="setModoEntrada('predefinido')" class="py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 bg-background text-foreground shadow-sm">
              <i data-lucide="bookmark" class="h-3.5 w-3.5 text-blue-500"></i> Problemas Resolvidos
            </button>
            <button id="tabModoCustom" onclick="setModoEntrada('personalizado')" class="py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 text-muted-foreground hover:text-foreground">
              <i data-lucide="pen-tool" class="h-3.5 w-3.5 text-emerald-500"></i> Digitar Função Livre
            </button>
          </div>
        </div>

        <!-- Seção 1: Botões dos Problemas Resolvidos -->
        <div id="secaoPredefinido" class="flex flex-col gap-2 p-2.5 rounded-lg bg-muted/40 border border-border/50">
          <label class="text-[11px] font-medium text-muted-foreground">Escolha um dos problemas para carregar:</label>
          <div class="flex flex-col gap-1.5">
            <button type="button" onclick="selecionarPreset(0)" id="presetBtn0" class="flex items-center justify-between px-3 py-2 text-xs rounded-md border border-blue-500 bg-blue-500/10 text-blue-500 font-medium transition-all text-left">
              <span>Exemplo: cos(x) − x = 0</span>
              <span class="text-[10px] text-muted-foreground font-mono">[0, 1]</span>
            </button>
            <button type="button" onclick="selecionarPreset(1)" id="presetBtn1" class="flex items-center justify-between px-3 py-2 text-xs rounded-md border border-border hover:bg-muted/60 text-foreground transition-all text-left">
              <span>Problema 1: Resfriamento</span>
              <span class="text-[10px] text-muted-foreground font-mono">20+90e^-0.15t = 50</span>
            </button>
            <button type="button" onclick="selecionarPreset(2)" id="presetBtn2" class="flex items-center justify-between px-3 py-2 text-xs rounded-md border border-border hover:bg-muted/60 text-foreground transition-all text-left">
              <span>Problema 2: Circuito RC</span>
              <span class="text-[10px] text-muted-foreground font-mono">5(1-e^-t) = 3.8</span>
            </button>
          </div>
        </div>

        <!-- Campos de Entrada (editáveis) -->
        <div class="flex flex-col gap-3.5 pt-1 border-t border-border/50">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-medium text-foreground flex items-center justify-between">
              <span>Função f(x):</span>
              <span class="text-[10px] text-muted-foreground">ex: cos(x) - x, x^3 - 9*x + 3</span>
            </label>
            <input type="text" id="inpF" value="cos(x) - x" oninput="marcarComoCustomizado()" class="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-medium text-foreground flex items-center justify-between">
              <span>Derivada f'(x):</span>
              <span class="text-[10px] text-muted-foreground">(Opcional para Newton)</span>
            </label>
            <input type="text" id="inpDf" value="-sin(x) - 1" oninput="marcarComoCustomizado()" class="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-medium text-foreground">Intervalo a:</label>
              <input type="number" id="inpA" value="0.0" step="any" oninput="marcarComoCustomizado()" class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-medium text-foreground">Intervalo b:</label>
              <input type="number" id="inpB" value="1.0" step="any" oninput="marcarComoCustomizado()" class="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <div class="flex flex-col gap-1.5">
              <label class="text-[11px] font-medium text-foreground">Newton x0:</label>
              <input type="number" id="inpX0N" value="0.5" step="any" oninput="marcarComoCustomizado()" class="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[11px] font-medium text-foreground">Secante x0:</label>
              <input type="number" id="inpX0S" value="0.0" step="any" oninput="marcarComoCustomizado()" class="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-[11px] font-medium text-foreground">Secante x1:</label>
              <input type="number" id="inpX1S" value="1.0" step="any" oninput="marcarComoCustomizado()" class="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-medium text-foreground">Tolerância (ε):</label>
              <input type="text" id="inpTol" value="1e-6" oninput="marcarComoCustomizado()" class="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-medium text-foreground">Máx Iterações:</label>
              <input type="number" id="inpMax" value="100" oninput="marcarComoCustomizado()" class="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono">
            </div>
          </div>

          <button type="button" onclick="simularFuncaoEditada()" class="w-full inline-flex items-center justify-center gap-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm text-xs font-medium h-9 px-3 transition-colors">
            <i data-lucide="play" class="h-3.5 w-3.5"></i> Simular Função Editada
          </button>
        </div>

      </div>

      <!-- Card: Método e Controles -->
      <div class="rounded-xl border border-border bg-card p-5 shadow-sm flex flex-col gap-4">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
          <i data-lucide="play" class="h-3.5 w-3.5"></i> Método e Execução
        </h2>

        <!-- Segmented Tabs (shadcn style) -->
        <div class="grid grid-cols-4 p-1 bg-muted rounded-lg text-xs font-medium">
          <button onclick="setMetodo('Bissecção')" id="tabB" class="py-1.5 rounded-md transition-all text-center">Bissecção</button>
          <button onclick="setMetodo('Falsa Posição')" id="tabF" class="py-1.5 rounded-md transition-all text-center">Falsa Pos.</button>
          <button onclick="setMetodo('Newton-Raphson')" id="tabN" class="py-1.5 rounded-md transition-all text-center bg-background text-foreground shadow-sm">Newton</button>
          <button onclick="setMetodo('Secante')" id="tabS" class="py-1.5 rounded-md transition-all text-center">Secante</button>
        </div>

        <!-- Botões de Ação -->
        <div class="grid grid-cols-2 gap-2">
          <button onclick="avancarPasso()" class="inline-flex items-center justify-center gap-1.5 rounded-md bg-blue-600 hover:bg-blue-700 text-white shadow text-sm font-medium h-9 px-3 transition-colors">
            <i data-lucide="step-forward" class="h-4 w-4"></i> Próximo Passo
          </button>
          <button id="btnPlay" onclick="togglePlay()" class="inline-flex items-center justify-center gap-1.5 rounded-md border border-input bg-background hover:bg-accent text-foreground shadow-sm text-sm font-medium h-9 px-3 transition-colors">
            <i data-lucide="play" id="iconPlay" class="h-4 w-4"></i> <span id="txtPlay">Auto Play</span>
          </button>
          <button onclick="executarTudo()" class="inline-flex items-center justify-center gap-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white shadow text-sm font-medium h-9 px-3 transition-colors">
            <i data-lucide="fast-forward" class="h-4 w-4"></i> Resolver Tudo
          </button>
          <button onclick="reiniciarSimulacao()" class="inline-flex items-center justify-center gap-1.5 rounded-md border border-input bg-background hover:bg-accent text-foreground shadow-sm text-sm font-medium h-9 px-3 transition-colors">
            <i data-lucide="rotate-ccw" class="h-4 w-4"></i> Reiniciar
          </button>
        </div>

        <button onclick="abrirModalComparativo()" class="w-full inline-flex items-center justify-center gap-2 rounded-md bg-purple-600 hover:bg-purple-700 text-white shadow text-sm font-medium h-10 px-4 transition-colors">
          <i data-lucide="bar-chart-2" class="h-4 w-4"></i> Comparar Todos os 4 Métodos
        </button>
      </div>

      <!-- Card: Métricas Rápidas -->
      <div class="rounded-xl border border-border bg-card p-5 shadow-sm flex flex-col gap-3">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
          <i data-lucide="check-circle-2" class="h-3.5 w-3.5"></i> Status e Métricas
        </h2>
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div class="rounded-lg bg-muted/60 p-3">
            <div class="text-[11px] text-muted-foreground">Raiz Atual:</div>
            <div id="metricRaiz" class="font-mono font-semibold text-foreground text-sm truncate">-</div>
          </div>
          <div class="rounded-lg bg-muted/60 p-3">
            <div class="text-[11px] text-muted-foreground">Precisão |f(x)|:</div>
            <div id="metricRes" class="font-mono font-semibold text-foreground text-sm truncate">-</div>
          </div>
        </div>
        <div class="flex items-center justify-between text-xs text-muted-foreground px-1">
          <span id="metricStatus">Aguardando início...</span>
          <span id="metricIter" class="font-mono">Iteração: 0 / 0</span>
        </div>
      </div>

    </div>

    <!-- COLUNA DIREITA: Gráfico Interativo e Tabela (8 cols) -->
    <div class="lg:col-span-8 flex flex-col gap-5">

      <!-- Card do Gráfico Interativo com Plotly -->
      <div class="rounded-xl border border-border bg-card p-5 shadow-sm flex flex-col gap-3.5">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <h2 class="text-sm font-semibold tracking-tight text-foreground flex items-center gap-2">
              <i data-lucide="line-chart" class="h-4 w-4 text-blue-500"></i> Visualização Geométrica da Iteração
            </h2>
            <span id="badgeMetodo" class="rounded-md border border-border bg-secondary px-2.5 py-0.5 text-xs font-medium text-secondary-foreground font-mono">Newton-Raphson</span>
          </div>

          <!-- Controle de Câmera: Foco Dinâmico vs Visão Global -->
          <div class="flex items-center gap-1 p-0.5 bg-muted rounded-lg text-xs font-medium">
            <button id="btnZoomFoco" onclick="setModoZoom('foco')" class="px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 bg-background text-foreground shadow-sm" title="Enquadrar dinamicamente nos pontos ativos da iteração">
              <i data-lucide="zoom-in" class="h-3.5 w-3.5 text-blue-500"></i> Foco na Iteração
            </button>
            <button id="btnZoomGlobal" onclick="setModoZoom('global')" class="px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 text-muted-foreground hover:text-foreground" title="Exibir domínio completo da função">
              <i data-lucide="maximize-2" class="h-3.5 w-3.5"></i> Panorâmico
            </button>
          </div>
        </div>

        <!-- Container do Gráfico Plotly -->
        <div id="plotlyChart" class="w-full h-[450px] rounded-lg border border-border/40 overflow-hidden bg-background"></div>

        <!-- Controles de Navegação Passo a Passo e Slider -->
        <div class="flex items-center gap-2.5 pt-0.5">
          <button onclick="passoAnterior()" class="h-8 px-2.5 rounded-md border border-input bg-background hover:bg-accent text-foreground text-xs font-medium flex items-center gap-1 transition-colors shadow-sm" title="Voltar uma iteração">
            <i data-lucide="chevron-left" class="h-4 w-4"></i> Anterior
          </button>
          
          <input type="range" id="sliderPasso" min="0" max="0" value="0" oninput="irParaPasso(parseInt(this.value))" class="w-full h-1.5 bg-muted rounded-lg appearance-none cursor-pointer accent-primary">
          <span id="lblSlider" class="text-xs font-mono text-muted-foreground w-12 text-right">0/0</span>

          <button onclick="avancarPasso()" class="h-8 px-2.5 rounded-md border border-input bg-background hover:bg-accent text-foreground text-xs font-medium flex items-center gap-1 transition-colors shadow-sm" title="Avançar uma iteração">
            Próximo <i data-lucide="chevron-right" class="h-4 w-4"></i>
          </button>
        </div>

        <!-- Card Didático: O que está acontecendo neste passo? -->
        <div id="cardExplicacaoPasso" class="rounded-lg border border-border bg-muted/30 p-3.5 flex items-start gap-3 text-xs transition-colors">
          <div class="mt-0.5 p-1.5 rounded-md bg-blue-500/10 text-blue-500 flex-shrink-0">
            <i data-lucide="info" class="h-4 w-4"></i>
          </div>
          <div class="flex-1 flex flex-col gap-1">
            <div class="flex items-center justify-between flex-wrap gap-1">
              <span id="explicacaoTitulo" class="font-semibold text-foreground text-xs">Passo 0 • Estado Inicial da Função</span>
              <span id="explicacaoFormula" class="font-mono text-[11px] text-muted-foreground px-2 py-0.5 rounded bg-muted border border-border/50">f(x) = 0</span>
            </div>
            <p id="explicacaoTexto" class="text-muted-foreground leading-relaxed text-[11px]">
              A curva representa a função f(x). Utilize os botões 'Próximo Passo' ou o controle deslizante para iniciar a resolução e acompanhar o passo a passo com a construção geométrica detalhada.
            </p>
          </div>
        </div>
      </div>

      <!-- Card da Tabela de Iterações -->
      <div class="rounded-xl border border-border bg-card p-5 shadow-sm flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-semibold tracking-tight text-foreground flex items-center gap-2">
            <i data-lucide="table" class="h-4 w-4 text-emerald-500"></i> Histórico Detalhado das Iterações
          </h2>
          <div class="flex items-center gap-2">
            <span id="tabelaBadgeCount" class="text-xs text-muted-foreground font-mono">0 iterações</span>
            <button onclick="exportarPassosCSV()" class="inline-flex items-center gap-1.5 rounded-md border border-input bg-background hover:bg-accent px-2.5 py-1 text-xs font-medium text-foreground transition-colors shadow-sm" title="Baixar passos em formato CSV para Excel/Word">
              <i data-lucide="download" class="h-3.5 w-3.5"></i> Exportar Passos (.csv)
            </button>
          </div>
        </div>

        <div class="rounded-lg border border-border overflow-hidden">
          <div class="max-h-[220px] overflow-y-auto">
            <table class="w-full text-left text-xs font-sans">
              <thead class="sticky top-0 bg-muted/80 backdrop-blur border-b border-border text-muted-foreground uppercase text-[10px] font-semibold tracking-wider">
                <tr>
                  <th class="py-2.5 px-3 w-16 text-center"># Iter</th>
                  <th class="py-2.5 px-3">Estimativa (x)</th>
                  <th class="py-2.5 px-3">f(x)</th>
                  <th class="py-2.5 px-3">Precisão |f(x)|</th>
                  <th class="py-2.5 px-3">Detalhes / Intervalo</th>
                </tr>
              </thead>
              <tbody id="tabelaBody" class="divide-y divide-border/50 font-mono">
                <!-- Linhas inseridas dinamicamente -->
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

  </main>

  <!-- MODAL: Comparativo dos 4 Métodos (shadcn dialog) -->
  <div id="modalComp" class="fixed inset-0 z-50 hidden bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="rounded-xl border border-border bg-card p-6 shadow-xl max-w-3xl w-full flex flex-col gap-5 animate-in fade-in zoom-in-95 duration-150">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold tracking-tight text-foreground">Comparativo dos 4 Métodos Numéricos</h3>
          <p class="text-xs text-muted-foreground">Execução unificada com tempo de CPU, iterações e resíduos calculados.</p>
        </div>
        <button onclick="fecharModal()" class="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground">
          <i data-lucide="x" class="h-5 w-5"></i>
        </button>
      </div>

      <!-- Tabela Comparativa -->
      <div class="rounded-lg border border-border overflow-hidden">
        <table class="w-full text-left text-xs font-sans">
          <thead class="bg-muted text-muted-foreground uppercase text-[10px] font-semibold tracking-wider border-b border-border">
            <tr>
              <th class="py-2.5 px-3">Método</th>
              <th class="py-2.5 px-3">Raiz Encontrada</th>
              <th class="py-2.5 px-3 text-center">Iterações</th>
              <th class="py-2.5 px-3 text-right">Tempo (ms)</th>
              <th class="py-2.5 px-3 text-right">Precisão |f(raiz)|</th>
              <th class="py-2.5 px-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody id="modalTbody" class="divide-y divide-border font-mono">
            <!-- Linhas inseridas dinamicamente -->
          </tbody>
        </table>
      </div>

      <!-- Gráficos de Barras no Relatório -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
        <div class="rounded-lg border border-border bg-muted/20 p-3 flex flex-col gap-1.5">
          <span class="text-xs font-semibold text-foreground flex items-center gap-1.5">
            <i data-lucide="bar-chart-2" class="h-3.5 w-3.5 text-blue-500"></i> Iterações por Método
          </span>
          <div id="modalChartIter" style="height: 180px;" class="w-full"></div>
        </div>
        <div class="rounded-lg border border-border bg-muted/20 p-3 flex flex-col gap-1.5">
          <span class="text-xs font-semibold text-foreground flex items-center gap-1.5">
            <i data-lucide="clock" class="h-3.5 w-3.5 text-amber-500"></i> Tempo de Execução (ms)
          </span>
          <div id="modalChartTempo" style="height: 180px;" class="w-full"></div>
        </div>
      </div>

      <!-- Ações do Modal -->
      <div class="flex items-center justify-between pt-2">
        <div class="flex items-center gap-2">
          <button onclick="exportarExcel()" class="inline-flex items-center gap-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white shadow text-xs font-medium h-9 px-3 transition-colors">
            <i data-lucide="file-spreadsheet" class="h-4 w-4"></i> Exportar Planilha (.xlsx)
          </button>
          <button onclick="exportarGraficos()" class="inline-flex items-center gap-1.5 rounded-md border border-input bg-background hover:bg-accent text-foreground shadow-sm text-xs font-medium h-9 px-3 transition-colors">
            <i data-lucide="image" class="h-4 w-4"></i> Salvar Gráficos (.png)
          </button>
        </div>
        <button onclick="fecharModal()" class="inline-flex items-center justify-center rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 text-xs font-medium h-9 px-4 transition-colors">
          Fechar
        </button>
      </div>
      <div id="modalExportFeedback" class="text-xs text-emerald-500 font-medium hidden"></div>
    </div>
  </div>

  <script>
    // Estado Global da Aplicação
    let modoAtual = "Newton-Raphson";
    let dadosSimulacao = { passos: [], curva_x: [], curva_y: [], status_final: "" };
    let passoIndex = 0;
    let timerAutoPlay = null;

    const PRESETS = [
      {
        nome: "Exemplo: cos(x) − x = 0",
        f: "cos(x) - x",
        df: "-sin(x) - 1",
        a: 0.0,
        b: 1.0,
        x0_n: 0.5,
        x0_s: 0.0,
        x1_s: 1.0,
        tol: 1e-6,
        max_iter: 100
      },
      {
        nome: "Problema 1: Resfriamento (Lei de Newton)",
        f: "20 + 90*exp(-0.15*x) - 50",
        df: "-13.5*exp(-0.15*x)",
        a: 0.0,
        b: 10.0,
        x0_n: 0.0,
        x0_s: 0.0,
        x1_s: 10.0,
        tol: 1e-6,
        max_iter: 100
      },
      {
        nome: "Problema 2: Circuito RC (Capacitor)",
        f: "5*(1 - exp(-x)) - 3.8",
        df: "5*exp(-x)",
        a: 0.0,
        b: 3.0,
        x0_n: 0.0,
        x0_s: 0.0,
        x1_s: 3.0,
        tol: 1e-6,
        max_iter: 100
      }
    ];

    let modoEntrada = "predefinido"; // 'predefinido' | 'personalizado'
    let presetAtivo = 0;
    let nomeProblemaAtual = PRESETS[0].nome;

    // Inicialização ao carregar página
    document.addEventListener("DOMContentLoaded", () => {
      lucide.createIcons();
      solicitarSimulacao();

      // Permitir submeter ao pressionar Enter em qualquer campo
      document.querySelectorAll("#inpF, #inpDf, #inpA, #inpB, #inpX0N, #inpX0S, #inpX1S, #inpTol, #inpMax").forEach(el => {
        el.addEventListener("keypress", (e) => {
          if (e.key === "Enter") {
            simularFuncaoEditada();
          }
        });
      });
    });

    // Toggle de Tema (Dark / Light)
    function toggleTheme() {
      const html = document.documentElement;
      const isDark = html.classList.contains("dark");
      if (isDark) {
        html.classList.remove("dark");
        document.getElementById("sunIcon").classList.add("hidden");
        document.getElementById("moonIcon").classList.remove("hidden");
      } else {
        html.classList.add("dark");
        document.getElementById("sunIcon").classList.remove("hidden");
        document.getElementById("moonIcon").classList.add("hidden");
      }
      lucide.createIcons();
      desenharGraficoPasso(passoIndex);
    }

    // Controle de Modo de Entrada (Pré-definido vs Customizado)
    function setModoEntrada(modo) {
      modoEntrada = modo;
      const tabPre = document.getElementById("tabModoPre");
      const tabCustom = document.getElementById("tabModoCustom");
      const secaoPre = document.getElementById("secaoPredefinido");
      const badgeModo = document.getElementById("badgeModo");

      if (modo === "predefinido") {
        secaoPre.classList.remove("hidden");

        tabPre.className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 bg-background text-foreground shadow-sm";
        tabCustom.className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 text-muted-foreground hover:text-foreground";

        badgeModo.innerText = "Problema Pré-definido";
        badgeModo.className = "text-[10px] font-medium text-blue-500 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-full";

        selecionarPreset(presetAtivo);
      } else {
        secaoPre.classList.add("hidden");

        tabCustom.className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 bg-background text-foreground shadow-sm";
        tabPre.className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 text-muted-foreground hover:text-foreground";

        badgeModo.innerText = "Função Personalizada";
        badgeModo.className = "text-[10px] font-medium text-emerald-500 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full";

        [0, 1, 2].forEach(i => {
          const btn = document.getElementById(`presetBtn${i}`);
          if (btn) {
            btn.className = "flex items-center justify-between px-3 py-2 text-xs rounded-md border border-border hover:bg-muted/60 text-foreground transition-all text-left";
          }
        });
        nomeProblemaAtual = "Função Personalizada";
      }
      lucide.createIcons();
    }

    function selecionarPreset(idx) {
      presetAtivo = idx;
      const p = PRESETS[idx];
      if (!p) return;

      nomeProblemaAtual = p.nome;

      document.getElementById("inpF").value = p.f;
      document.getElementById("inpDf").value = p.df;
      document.getElementById("inpA").value = p.a;
      document.getElementById("inpB").value = p.b;
      document.getElementById("inpX0N").value = p.x0_n;
      document.getElementById("inpX0S").value = p.x0_s;
      document.getElementById("inpX1S").value = p.x1_s;
      document.getElementById("inpTol").value = p.tol;
      document.getElementById("inpMax").value = p.max_iter;

      [0, 1, 2].forEach(i => {
        const btn = document.getElementById(`presetBtn${i}`);
        if (btn) {
          if (i === idx) {
            btn.className = "flex items-center justify-between px-3 py-2 text-xs rounded-md border border-blue-500 bg-blue-500/10 text-blue-500 font-medium transition-all text-left";
          } else {
            btn.className = "flex items-center justify-between px-3 py-2 text-xs rounded-md border border-border hover:bg-muted/60 text-foreground transition-all text-left";
          }
        }
      });

      if (modoEntrada !== "predefinido") {
        modoEntrada = "predefinido";
        document.getElementById("secaoPredefinido").classList.remove("hidden");
        document.getElementById("tabModoPre").className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 bg-background text-foreground shadow-sm";
        document.getElementById("tabModoCustom").className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 text-muted-foreground hover:text-foreground";
        const badgeModo = document.getElementById("badgeModo");
        badgeModo.innerText = "Problema Pré-definido";
        badgeModo.className = "text-[10px] font-medium text-blue-500 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-full";
      }

      solicitarSimulacao();
    }

    function marcarComoCustomizado() {
      if (modoEntrada !== "personalizado") {
        modoEntrada = "personalizado";
        document.getElementById("secaoPredefinido").classList.add("hidden");

        document.getElementById("tabModoCustom").className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 bg-background text-foreground shadow-sm";
        document.getElementById("tabModoPre").className = "py-1.5 rounded-md transition-all flex items-center justify-center gap-1.5 text-muted-foreground hover:text-foreground";

        const badgeModo = document.getElementById("badgeModo");
        badgeModo.innerText = "Função Personalizada";
        badgeModo.className = "text-[10px] font-medium text-emerald-500 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full";

        [0, 1, 2].forEach(i => {
          const btn = document.getElementById(`presetBtn${i}`);
          if (btn) {
            btn.className = "flex items-center justify-between px-3 py-2 text-xs rounded-md border border-border hover:bg-muted/60 text-foreground transition-all text-left";
          }
        });
        nomeProblemaAtual = "Função Personalizada";
        lucide.createIcons();
      }
    }

    function setMetodo(metodo) {
      modoAtual = metodo;
      document.getElementById("badgeMetodo").innerText = metodo;

      const tabs = { "Bissecção": "tabB", "Falsa Posição": "tabF", "Newton-Raphson": "tabN", "Secante": "tabS" };
      Object.keys(tabs).forEach(m => {
        const el = document.getElementById(tabs[m]);
        if (m === metodo) {
          el.className = "py-1.5 rounded-md transition-all text-center bg-background text-foreground shadow-sm";
        } else {
          el.className = "py-1.5 rounded-md transition-all text-center text-muted-foreground hover:text-foreground";
        }
      });
      reiniciarSimulacao();
    }

    // Ação acionada pelo botão 'Simular Função Editada'
    async function simularFuncaoEditada() {
      await solicitarSimulacao();
      if (dadosSimulacao.passos && dadosSimulacao.passos.length > 0) {
        executarTudo();
      } else if (dadosSimulacao.status_final) {
        document.getElementById("metricStatus").innerText = `⚠️ ${dadosSimulacao.status_final}`;
      }
    }

    // Exportação em formato CSV com UTF-8 BOM para Excel / Word
    function exportarPassosCSV() {
      if (!dadosSimulacao.passos || dadosSimulacao.passos.length === 0) {
        alert("Nenhum passo para exportar. Execute ou avance a simulação primeiro.");
        return;
      }

      const linhas = [];
      const funcAtual = document.getElementById("inpF").value;
      linhas.push(`# Relatório de Passos - Método: ${modoAtual} | Função: ${funcAtual} | Status: ${dadosSimulacao.status_final}`);
      linhas.push("Iteração;Estimativa (x);f(x);Precisão |f(x)|;Detalhes");

      dadosSimulacao.passos.forEach(p => {
        const rVal = p.x_novo !== undefined ? p.x_novo : (p.x !== undefined ? p.x : p.x_prox);
        const fxVal = p.fx_novo !== undefined ? p.fx_novo : p.fx;
        const resVal = p.residuo !== undefined ? p.residuo : Math.abs(fxVal);
        linhas.push(`${p.iter};${rVal.toString().replace('.', ',')};${fxVal.toString().replace('.', ',')};${resVal.toString().replace('.', ',')};"${p.detalhes || ''}"`);
      });

      const csvContent = "\\uFEFF" + linhas.join("\\r\\n");
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const nomeLimpo = modoAtual.toLowerCase().replace(/[^a-z0-9]/g, "_");
      link.setAttribute("href", url);
      link.setAttribute("download", `historico_passos_${nomeLimpo}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    // Comunicação com o Backend Python
    async function solicitarSimulacao() {
      pararPlay();
      const payload = {
        f: document.getElementById("inpF").value,
        df: document.getElementById("inpDf").value,
        a: parseFloat(document.getElementById("inpA").value),
        b: parseFloat(document.getElementById("inpB").value),
        x0_n: parseFloat(document.getElementById("inpX0N").value),
        x0_s: parseFloat(document.getElementById("inpX0S").value),
        x1_s: parseFloat(document.getElementById("inpX1S").value),
        tol: parseFloat(document.getElementById("inpTol").value) || 1e-6,
        max_iter: parseInt(document.getElementById("inpMax").value) || 100,
        metodo: modoAtual
      };

      try {
        const resp = await fetch("/api/simular", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        dadosSimulacao = await resp.json();

        if (dadosSimulacao.erro) {
          document.getElementById("metricStatus").innerText = `⚠️ ${dadosSimulacao.erro}`;
          return;
        }

        passoIndex = 0;
        const total = dadosSimulacao.passos ? dadosSimulacao.passos.length : 0;
        document.getElementById("sliderPasso").max = total;
        document.getElementById("sliderPasso").value = 0;
        document.getElementById("lblSlider").innerText = `0/${total}`;
        document.getElementById("metricStatus").innerText = `Pronto (${total} iterações)`;
        document.getElementById("metricIter").innerText = `Iteração: 0 / ${total}`;
        document.getElementById("tabelaBadgeCount").innerText = `${total} iterações`;

        limparTabela();
        desenharGraficoPasso(0);
      } catch (err) {
        console.error("Erro na simulação:", err);
        document.getElementById("metricStatus").innerText = "⚠️ Erro na simulação";
      }
    }

    function reiniciarSimulacao() {
      solicitarSimulacao();
    }

    function avancarPasso() {
      if (passoIndex < dadosSimulacao.passos.length) {
        passoIndex++;
        atualizarVisualPasso(passoIndex);
      } else {
        pararPlay();
        document.getElementById("metricStatus").innerText = `✓ ${dadosSimulacao.status_final}`;
      }
    }

    function irParaPasso(idx) {
      passoIndex = idx;
      atualizarVisualPasso(passoIndex);
    }

    function executarTudo() {
      passoIndex = dadosSimulacao.passos.length;
      atualizarVisualPasso(passoIndex);
      document.getElementById("metricStatus").innerText = `✓ ${dadosSimulacao.status_final}`;
    }

    function togglePlay() {
      if (timerAutoPlay) {
        pararPlay();
      } else {
        document.getElementById("iconPlay").setAttribute("data-lucide", "pause");
        document.getElementById("txtPlay").innerText = "Pausar";
        lucide.createIcons();
        timerAutoPlay = setInterval(() => {
          if (passoIndex < dadosSimulacao.passos.length) {
            avancarPasso();
          } else {
            pararPlay();
          }
        }, 450);
      }
    }

    function pararPlay() {
      if (timerAutoPlay) {
        clearInterval(timerAutoPlay);
        timerAutoPlay = null;
        document.getElementById("iconPlay").setAttribute("data-lucide", "play");
        document.getElementById("txtPlay").innerText = "Auto Play";
        lucide.createIcons();
      }
    }

    let modoZoom = 'foco'; // 'foco' | 'global'

    function setModoZoom(modo) {
      modoZoom = modo;
      const btnFoco = document.getElementById("btnZoomFoco");
      const btnGlobal = document.getElementById("btnZoomGlobal");

      if (modo === "foco") {
        btnFoco.className = "px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 bg-background text-foreground shadow-sm";
        btnGlobal.className = "px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 text-muted-foreground hover:text-foreground";
      } else {
        btnGlobal.className = "px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 bg-background text-foreground shadow-sm";
        btnFoco.className = "px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 text-muted-foreground hover:text-foreground";
      }
      desenharGraficoPasso(passoIndex);
    }

    function passoAnterior() {
      if (passoIndex > 0) {
        passoIndex--;
        atualizarVisualPasso(passoIndex);
      }
    }

    function gerarTextoExplicacao(idx) {
      if (idx === 0) {
        return {
          titulo: "Passo 0 • Estado Inicial da Função",
          formula: "f(x) = 0",
          texto: "A curva azul ilustra o comportamento de f(x). Pressione <b>'Próximo'</b> ou <b>'Auto Play'</b> para acompanhar a resolução passo a passo com a construção geométrica detalhada."
        };
      }

      const p = dadosSimulacao.passos[idx - 1];
      const isUltimo = (idx === dadosSimulacao.passos.length);

      if (modoAtual === "Bissecção") {
        const lado = (p.fa * p.fx < 0) ? "esquerda [a, xm]" : "direita [xm, b]";
        return {
          titulo: `Iteração ${p.iter} • Bissecção: Redução do Intervalo`,
          formula: `x_m = (${p.a.toFixed(4)} + ${p.b.toFixed(4)}) / 2 = ${p.x.toFixed(6)}`,
          texto: `Intervalo ativo atual: <b>[${p.a.toFixed(5)}, ${p.b.toFixed(5)}]</b>. O ponto médio calculado é <b>x<sub>m</sub> = ${p.x.toFixed(6)}</b>, onde f(x<sub>m</sub>) = ${p.fx.toExponential(3)}. Como f(a) e f(x<sub>m</sub>) têm ${p.fa * p.fx < 0 ? 'sinais opostos' : 'mesmo sinal'}, a raiz é garantida na <b>metade ${lado}</b>. Precisão atual: |f(x)| = <b>${p.residuo.toExponential(2)}</b>.${isUltimo ? ' <span class=\"text-emerald-500 font-semibold\">✓ Convergência atingida!</span>' : ''}`
        };
      } else if (modoAtual === "Falsa Posição") {
        return {
          titulo: `Iteração ${p.iter} • Falsa Posição: Interseção da Corda`,
          formula: `x = [a·f(b) - b·f(a)] / [f(b) - f(a)] = ${p.x.toFixed(6)}`,
          texto: `A reta conectando A(${p.a.toFixed(4)}, ${p.fa.toFixed(2)}) e B(${p.b.toFixed(4)}, ${p.fb.toFixed(2)}) cruza o eixo em <b>x = ${p.x.toFixed(6)}</b>. Avaliação da função: f(x) = ${p.fx.toExponential(3)}. Resíduo atual: <b>${p.residuo.toExponential(2)}</b>.${isUltimo ? ' <span class=\"text-emerald-500 font-semibold\">✓ Tolerância atingida!</span>' : ''}`
        };
      } else if (modoAtual === "Newton-Raphson") {
        return {
          titulo: `Iteração ${p.iter} • Newton-Raphson: Reta Tangente`,
          formula: `x_{${p.iter}} = ${p.x.toFixed(5)} - (${p.fx.toFixed(3)}) / (${p.dfx.toFixed(3)}) = ${p.x_prox.toFixed(6)}`,
          texto: `No ponto x = ${p.x.toFixed(5)}, temos f(x) = ${p.fx.toFixed(4)} e derivada f'(x) = ${p.dfx.toFixed(4)}. A reta tangente projetada intercepta o eixo y=0 em <b>x<sub>novo</sub> = ${p.x_prox.toFixed(6)}</b>. Resíduo: <b>${p.residuo.toExponential(2)}</b>.${isUltimo ? ' <span class=\"text-emerald-500 font-semibold\">✓ Raiz encontrada!</span>' : ''}`
        };
      } else if (modoAtual === "Secante") {
        return {
          titulo: `Iteração ${p.iter} • Secante: Interseção por Dois Pontos`,
          formula: `x_m = [x_e·f(x_d) - x_d·f(x_e)] / [f(x_d) - f(x_e)] = ${p.x.toFixed(6)}`,
          texto: `Utilizando os pontos anteriores x<sub>e</sub> = ${p.xe.toFixed(4)} e x<sub>d</sub> = ${p.xd.toFixed(4)}, a reta secante interceptou o eixo em <b>x<sub>m</sub> = ${p.x.toFixed(6)}</b>. Resíduo: <b>${p.residuo.toExponential(2)}</b>.${isUltimo ? ' <span class=\"text-emerald-500 font-semibold\">✓ Convergência finalizada!</span>' : ''}`
        };
      }
      return { titulo: `Iteração ${idx}`, formula: "", texto: "" };
    }

    function atualizarVisualPasso(idx) {
      document.getElementById("sliderPasso").value = idx;
      const total = dadosSimulacao.passos.length;
      document.getElementById("lblSlider").innerText = `${idx}/${total}`;
      document.getElementById("metricIter").innerText = `Iteração: ${idx} / ${total}`;

      if (idx > 0) {
        const p = dadosSimulacao.passos[idx - 1];
        const rVal = p.x_novo !== undefined ? p.x_novo : (p.x !== undefined ? p.x : p.x_prox);
        const fxVal = p.fx_novo !== undefined ? p.fx_novo : (p.fx !== undefined ? p.fx : 0);
        document.getElementById("metricRaiz").innerText = rVal.toFixed(8);
        document.getElementById("metricRes").innerText = (p.residuo !== undefined ? p.residuo : Math.abs(fxVal)).toExponential(2);
        document.getElementById("metricStatus").innerText = `Iteração ${p.iter}...`;
      } else {
        document.getElementById("metricRaiz").innerText = "Aguardando início...";
        document.getElementById("metricRes").innerText = "-";
        document.getElementById("metricStatus").innerText = `Pronto (${total} iterações)`;
      }

      // Atualiza o Card Didático
      const exp = gerarTextoExplicacao(idx);
      document.getElementById("explicacaoTitulo").innerText = exp.titulo;
      document.getElementById("explicacaoFormula").innerText = exp.formula;
      document.getElementById("explicacaoTexto").innerHTML = exp.texto;

      desenharGraficoPasso(idx);
      atualizarTabela(idx);
      lucide.createIcons();
    }

    function limparTabela() {
      document.getElementById("tabelaBody").innerHTML = "";
    }

    function atualizarTabela(idx) {
      limparTabela();
      const tbody = document.getElementById("tabelaBody");

      for (let i = 0; i < idx; i++) {
        const p = dadosSimulacao.passos[i];
        const rVal = p.x_novo !== undefined ? p.x_novo : (p.x !== undefined ? p.x : p.x_prox);
        const fxVal = p.fx_novo !== undefined ? p.fx_novo : (p.fx !== undefined ? p.fx : 0);
        const isLast = i === idx - 1;

        const tr = document.createElement("tr");
        tr.className = isLast ? "bg-primary/10 text-primary font-medium" : "hover:bg-muted/40 transition-colors";

        tr.innerHTML = `
          <td class="py-2 px-3 text-center text-xs">${p.iter}</td>
          <td class="py-2 px-3 text-xs">${rVal.toFixed(7)}</td>
          <td class="py-2 px-3 text-xs text-muted-foreground">${fxVal.toExponential(3)}</td>
          <td class="py-2 px-3 text-xs font-semibold ${p.residuo < 1e-6 ? 'text-emerald-500' : ''}">${p.residuo.toExponential(2)}</td>
          <td class="py-2 px-3 text-xs text-muted-foreground">${p.detalhes}</td>
        `;
        tbody.appendChild(tr);
      }
    }

    // Renderização do Gráfico com Plotly.js (Trabalho Ostensivo e Pedagógico)
    function desenharGraficoPasso(idx) {
      const isDark = document.documentElement.classList.contains("dark");
      const bgColor = isDark ? "#09090b" : "#ffffff";
      const plotBg = isDark ? "#121215" : "#f8fafc";
      const txtColor = isDark ? "#fafafa" : "#09090b";
      const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";

      const traces = [];
      const annotations = [];
      const shapes = [];

      // 1. Curva f(x)
      if (dadosSimulacao.curva_x && dadosSimulacao.curva_x.length > 0) {
        traces.push({
          x: dadosSimulacao.curva_x,
          y: dadosSimulacao.curva_y,
          type: 'scatter',
          mode: 'lines',
          name: 'f(x)',
          line: { color: isDark ? '#38bdf8' : '#0284c7', width: 3 },
          hoverinfo: 'x+y'
        });
      }

      // 2. Linha do Eixo Y=0
      if (dadosSimulacao.curva_x && dadosSimulacao.curva_x.length > 0) {
        const xMinAll = Math.min(...dadosSimulacao.curva_x);
        const xMaxAll = Math.max(...dadosSimulacao.curva_x);
        traces.push({
          x: [xMinAll, xMaxAll],
          y: [0, 0],
          type: 'scatter',
          mode: 'lines',
          name: 'Eixo y = 0',
          line: { color: isDark ? '#52525b' : '#a1a1aa', width: 1.5, dash: 'dash' },
          hoverinfo: 'none',
          showlegend: false
        });
      }

      // 3. Elementos geométricos da iteração ativa
      if (idx > 0 && idx <= dadosSimulacao.passos.length) {
        const p = dadosSimulacao.passos[idx - 1];

        if (modoAtual === "Bissecção") {
          const a = p.a;
          const b = p.b;
          const fa = p.fa || 0;
          const fb = p.fb || 0;
          const xm = p.x;
          const fxm = p.fx;

          // Região ativa sombreada entre a e b
          shapes.push({
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: Math.min(a, b),
            x1: Math.max(a, b),
            y0: 0,
            y1: 1,
            fillcolor: isDark ? 'rgba(14, 165, 233, 0.15)' : 'rgba(14, 165, 233, 0.10)',
            line: { color: '#0ea5e9', width: 1, dash: 'dot' }
          });

          // Linhas verticais pontilhadas nos limites a e b
          traces.push({
            x: [a, a],
            y: [0, fa],
            type: 'scatter',
            mode: 'lines+markers',
            name: `Limite a = ${a.toFixed(4)}`,
            line: { color: '#0ea5e9', width: 2, dash: 'dot' },
            marker: { color: '#0ea5e9', size: 8 }
          });

          traces.push({
            x: [b, b],
            y: [0, fb],
            type: 'scatter',
            mode: 'lines+markers',
            name: `Limite b = ${b.toFixed(4)}`,
            line: { color: '#f97316', width: 2, dash: 'dot' },
            marker: { color: '#f97316', size: 8 }
          });

          // Faixa no eixo horizontal destacando o intervalo [a, b]
          traces.push({
            x: [a, b],
            y: [0, 0],
            type: 'scatter',
            mode: 'lines',
            name: `Intervalo [${a.toFixed(3)}, ${b.toFixed(3)}]`,
            line: { color: '#06b6d4', width: 5 }
          });

          // Projeção vertical no ponto médio xm
          traces.push({
            x: [xm, xm],
            y: [0, fxm],
            type: 'scatter',
            mode: 'lines',
            name: `Projeção f(xm)`,
            line: { color: '#10b981', dash: 'dash', width: 2.5 }
          });

          // Ponto na curva (xm, f(xm))
          traces.push({
            x: [xm],
            y: [fxm],
            type: 'scatter',
            mode: 'markers',
            name: `(xm, f(xm))`,
            marker: { color: '#10b981', size: 8 }
          });

          // Raiz xm no eixo y=0
          traces.push({
            x: [xm],
            y: [0],
            type: 'scatter',
            mode: 'markers',
            name: `Ponto Médio xm = ${xm.toFixed(5)}`,
            marker: { color: '#10b981', size: 12, symbol: 'diamond', line: { color: isDark ? '#ffffff' : '#000000', width: 1.5 } }
          });

          // Anotações explicativas no gráfico
          annotations.push({
            x: a, y: fa,
            text: `<b>a</b> = ${a.toFixed(4)}<br>f(a) = ${fa.toExponential(2)}`,
            showarrow: true, arrowhead: 2, arrowcolor: '#0ea5e9',
            bgcolor: isDark ? '#0c4a6e' : '#e0f2fe', bordercolor: '#0ea5e9', borderwidth: 1,
            font: { size: 10, color: isDark ? '#f0f9ff' : '#0369a1' },
            ax: -35, ay: -25
          });

          annotations.push({
            x: b, y: fb,
            text: `<b>b</b> = ${b.toFixed(4)}<br>f(b) = ${fb.toExponential(2)}`,
            showarrow: true, arrowhead: 2, arrowcolor: '#f97316',
            bgcolor: isDark ? '#7c2d12' : '#ffedd5', bordercolor: '#f97316', borderwidth: 1,
            font: { size: 10, color: isDark ? '#fff7ed' : '#c2410c' },
            ax: 35, ay: -25
          });

          annotations.push({
            x: xm, y: 0,
            text: `<b>x<sub>m</sub></b> = ${xm.toFixed(6)}<br>|f(x<sub>m</sub>)| = ${p.residuo.toExponential(2)}`,
            showarrow: true, arrowhead: 2, arrowsize: 1.2, arrowcolor: '#10b981',
            bgcolor: isDark ? '#064e3b' : '#d1fae5', bordercolor: '#10b981', borderwidth: 1.5,
            font: { size: 11, color: isDark ? '#ecfdf5' : '#047857', family: 'JetBrains Mono' },
            ax: 0, ay: 45
          });

        } else if (modoAtual === "Falsa Posição") {
          const a = p.a;
          const b = p.b;
          const fa = p.fa;
          const fb = p.fb;
          const x = p.x;
          const fx = p.fx;

          // Região ativa sombreada
          shapes.push({
            type: 'rect',
            xref: 'x', yref: 'paper',
            x0: Math.min(a, b), x1: Math.max(a, b),
            y0: 0, y1: 1,
            fillcolor: isDark ? 'rgba(245, 158, 11, 0.12)' : 'rgba(245, 158, 11, 0.08)',
            line: { color: '#f59e0b', width: 1, dash: 'dot' }
          });

          // Corda Secante completa entre (a, fa) e (b, fb)
          const ptsCorda = [{x: a, y: fa}, {x: x, y: 0}, {x: b, y: fb}].sort((p1, p2) => p1.x - p2.x);
          traces.push({
            x: ptsCorda.map(pt => pt.x),
            y: ptsCorda.map(pt => pt.y),
            type: 'scatter',
            mode: 'lines',
            name: 'Corda Secante [a, b]',
            line: { color: '#f59e0b', width: 2.5 }
          });

          // Pontos A e B
          traces.push({
            x: [a, b],
            y: [fa, fb],
            type: 'scatter',
            mode: 'markers',
            name: 'Pontos A e B',
            marker: { color: '#f59e0b', size: 9, symbol: 'circle' }
          });

          // Projeção vertical da nova estimativa x até f(x)
          traces.push({
            x: [x, x],
            y: [0, fx],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Resíduo f(x)',
            line: { color: '#10b981', dash: 'dash', width: 2 },
            marker: { color: '#10b981', size: 7 }
          });

          // Raiz x no eixo y=0
          traces.push({
            x: [x],
            y: [0],
            type: 'scatter',
            mode: 'markers',
            name: `Raiz Secante x = ${x.toFixed(5)}`,
            marker: { color: '#10b981', size: 12, symbol: 'diamond', line: { color: isDark ? '#ffffff' : '#000000', width: 1.5 } }
          });

          // Anotações
          annotations.push({
            x: a, y: fa,
            text: `<b>A</b> (${a.toFixed(4)}, ${fa.toFixed(2)})`,
            showarrow: true, arrowhead: 2, arrowcolor: '#f59e0b',
            bgcolor: isDark ? '#451a03' : '#fef3c7', bordercolor: '#f59e0b', borderwidth: 1,
            font: { size: 10, color: isDark ? '#fffbeb' : '#b45309' },
            ax: -35, ay: -25
          });

          annotations.push({
            x: b, y: fb,
            text: `<b>B</b> (${b.toFixed(4)}, ${fb.toFixed(2)})`,
            showarrow: true, arrowhead: 2, arrowcolor: '#f59e0b',
            bgcolor: isDark ? '#451a03' : '#fef3c7', bordercolor: '#f59e0b', borderwidth: 1,
            font: { size: 10, color: isDark ? '#fffbeb' : '#b45309' },
            ax: 35, ay: -25
          });

          annotations.push({
            x: x, y: 0,
            text: `<b>Raiz Secante: x</b> = ${x.toFixed(6)}<br>|f(x)| = ${p.residuo.toExponential(2)}`,
            showarrow: true, arrowhead: 2, arrowsize: 1.2, arrowcolor: '#10b981',
            bgcolor: isDark ? '#064e3b' : '#d1fae5', bordercolor: '#10b981', borderwidth: 1.5,
            font: { size: 11, color: isDark ? '#ecfdf5' : '#047857', family: 'JetBrains Mono' },
            ax: 0, ay: 45
          });

        } else if (modoAtual === "Newton-Raphson") {
          const x0 = p.x;
          const fx0 = p.fx;
          const dfx0 = p.dfx;
          const x1 = p.x_prox;
          const fx1 = p.fx_prox;

          // Extensão visual da tangente
          const dx = Math.abs(x1 - x0);
          const spanT = Math.max(dx * 0.35, 0.15);
          const xStart = Math.min(x0, x1) - spanT;
          const xEnd = Math.max(x0, x1) + spanT;
          const yStart = fx0 + dfx0 * (xStart - x0);
          const yEnd = fx0 + dfx0 * (xEnd - x0);

          // Reta Tangente estendida
          const ptsTang = [
            { x: xStart, y: yStart },
            { x: x0, y: fx0 },
            { x: x1, y: 0 },
            { x: xEnd, y: yEnd }
          ].sort((p1, p2) => p1.x - p2.x);

          traces.push({
            x: ptsTang.map(pt => pt.x),
            y: ptsTang.map(pt => pt.y),
            type: 'scatter',
            mode: 'lines',
            name: `Reta Tangente (m = ${dfx0.toFixed(3)})`,
            line: { color: '#f43f5e', width: 2.5 }
          });

          // Linha guia vertical conectando (x0, 0) ao ponto de tangência (x0, fx0)
          traces.push({
            x: [x0, x0],
            y: [0, fx0],
            type: 'scatter',
            mode: 'lines',
            name: `Origem x = ${x0.toFixed(4)}`,
            line: { color: isDark ? '#71717a' : '#a1a1aa', width: 1.5, dash: 'dot' }
          });

          // Ponto de tangência na curva
          traces.push({
            x: [x0],
            y: [fx0],
            type: 'scatter',
            mode: 'markers',
            name: `Ponto Tangente (${x0.toFixed(4)}, ${fx0.toFixed(3)})`,
            marker: { color: '#38bdf8', size: 9, line: { color: isDark ? '#ffffff' : '#000000', width: 1.5 } }
          });

          // Projeção vertical da nova raiz x1 até a curva fx1
          traces.push({
            x: [x1, x1],
            y: [0, fx1],
            type: 'scatter',
            mode: 'lines+markers',
            name: `Novo f(x) = ${fx1.toExponential(2)}`,
            line: { color: '#10b981', width: 2, dash: 'dash' },
            marker: { color: '#10b981', size: 7 }
          });

          // Nova raiz x1 no eixo y=0
          traces.push({
            x: [x1],
            y: [0],
            type: 'scatter',
            mode: 'markers',
            name: `Nova Raiz x = ${x1.toFixed(6)}`,
            marker: { color: '#10b981', size: 12, symbol: 'diamond', line: { color: isDark ? '#ffffff' : '#000000', width: 1.5 } }
          });

          // Anotações
          annotations.push({
            x: x0, y: fx0,
            text: `<b>Tangência (x<sub>k</sub>, f(x<sub>k</sub>))</b><br>x = ${x0.toFixed(5)}<br>f'(x) = ${dfx0.toFixed(4)}`,
            showarrow: true, arrowhead: 2, arrowcolor: '#38bdf8',
            bgcolor: isDark ? '#082f49' : '#e0f2fe', bordercolor: '#38bdf8', borderwidth: 1,
            font: { size: 10, color: isDark ? '#f0f9ff' : '#0369a1' },
            ax: -45, ay: -35
          });

          annotations.push({
            x: x1, y: 0,
            text: `<b>Nova Raiz: x<sub>k+1</sub></b> = ${x1.toFixed(6)}<br>|f(x<sub>k+1</sub>)| = ${p.residuo.toExponential(2)}`,
            showarrow: true, arrowhead: 2, arrowsize: 1.2, arrowcolor: '#10b981',
            bgcolor: isDark ? '#064e3b' : '#d1fae5', bordercolor: '#10b981', borderwidth: 1.5,
            font: { size: 11, color: isDark ? '#ecfdf5' : '#047857', family: 'JetBrains Mono' },
            ax: 0, ay: 45
          });

        } else if (modoAtual === "Secante") {
          const xe = p.xe;
          const xd = p.xd;
          const fxe = p.fxe;
          const fxd = p.fxd;
          const xm = p.x;
          const fxm = p.fx;

          // Inclinação da secante
          const den = xd - xe;
          const mSec = (Math.abs(den) > 1e-12) ? (fxd - fxe) / den : 0;

          // Extensão suave da reta secante
          const allXSec = [xe, xd, xm];
          const xMinS = Math.min(...allXSec);
          const xMaxS = Math.max(...allXSec);
          const spanS = Math.max((xMaxS - xMinS) * 0.25, 0.15);
          const xStart = xMinS - spanS;
          const xEnd = xMaxS + spanS;
          const yStart = fxe + mSec * (xStart - xe);
          const yEnd = fxe + mSec * (xEnd - xe);

          const ptsSec = [
            { x: xStart, y: yStart },
            { x: xe, y: fxe },
            { x: xm, y: 0 },
            { x: xd, y: fxd },
            { x: xEnd, y: yEnd }
          ].sort((a, b) => a.x - b.x);

          traces.push({
            x: ptsSec.map(pt => pt.x),
            y: ptsSec.map(pt => pt.y),
            type: 'scatter',
            mode: 'lines',
            name: `Reta Secante`,
            line: { color: '#a855f7', width: 2.5 }
          });

          // Pontos Base P0 e P1
          traces.push({
            x: [xe, xd],
            y: [fxe, fxd],
            type: 'scatter',
            mode: 'markers',
            name: `Pontos Base Secante`,
            marker: { color: '#a855f7', size: 9, symbol: 'circle', line: { color: isDark ? '#ffffff' : '#000000', width: 1.5 } }
          });

          // Projeção vertical até o novo f(xm)
          traces.push({
            x: [xm, xm],
            y: [0, fxm],
            type: 'scatter',
            mode: 'lines+markers',
            name: `f(xm) = ${fxm.toExponential(2)}`,
            line: { color: '#10b981', width: 2, dash: 'dash' },
            marker: { color: '#10b981', size: 7 }
          });

          // Raiz xm no eixo y=0
          traces.push({
            x: [xm],
            y: [0],
            type: 'scatter',
            mode: 'markers',
            name: `Nova Raiz xm = ${xm.toFixed(5)}`,
            marker: { color: '#10b981', size: 12, symbol: 'diamond', line: { color: isDark ? '#ffffff' : '#000000', width: 1.5 } }
          });

          // Anotações
          annotations.push({
            x: xe, y: fxe,
            text: `<b>P<sub>0</sub></b> (${xe.toFixed(4)}, ${fxe.toFixed(2)})`,
            showarrow: true, arrowhead: 2, arrowcolor: '#a855f7',
            bgcolor: isDark ? '#3b0764' : '#f3e8ff', bordercolor: '#a855f7', borderwidth: 1,
            font: { size: 10, color: isDark ? '#faf5ff' : '#7e22ce' },
            ax: -35, ay: -25
          });

          annotations.push({
            x: xd, y: fxd,
            text: `<b>P<sub>1</sub></b> (${xd.toFixed(4)}, ${fxd.toFixed(2)})`,
            showarrow: true, arrowhead: 2, arrowcolor: '#a855f7',
            bgcolor: isDark ? '#3b0764' : '#f3e8ff', bordercolor: '#a855f7', borderwidth: 1,
            font: { size: 10, color: isDark ? '#faf5ff' : '#7e22ce' },
            ax: 35, ay: -25
          });

          annotations.push({
            x: xm, y: 0,
            text: `<b>Raiz Secante: x<sub>m</sub></b> = ${xm.toFixed(6)}<br>|f(x<sub>m</sub>)| = ${p.residuo.toExponential(2)}`,
            showarrow: true, arrowhead: 2, arrowsize: 1.2, arrowcolor: '#10b981',
            bgcolor: isDark ? '#064e3b' : '#d1fae5', bordercolor: '#10b981', borderwidth: 1.5,
            font: { size: 11, color: isDark ? '#ecfdf5' : '#047857', family: 'JetBrains Mono' },
            ax: 0, ay: 45
          });
        }
      }

      // 4. Layout e Enquadramento Inteligente (Smart Auto-Framing)
      const layout = {
        paper_bgcolor: bgColor,
        plot_bgcolor: plotBg,
        font: { family: 'Inter, sans-serif', color: txtColor, size: 11 },
        margin: { l: 55, r: 35, t: 30, b: 45 },
        xaxis: { gridcolor: gridColor, zeroline: false, title: { text: 'x', font: { size: 12, color: txtColor } } },
        yaxis: { gridcolor: gridColor, zeroline: false, title: { text: 'f(x)', font: { size: 12, color: txtColor } } },
        legend: {
          x: 0.02, y: 0.98, xanchor: 'left', yanchor: 'top',
          bgcolor: isDark ? 'rgba(9, 9, 11, 0.85)' : 'rgba(255, 255, 255, 0.85)',
          bordercolor: isDark ? '#27272a' : '#e4e4e7',
          borderwidth: 1,
          font: { size: 10 }
        },
        annotations: annotations,
        shapes: shapes
      };

      // Se o modo de Zoom estiver em FOCO e houver passo ativo:
      if (modoZoom === 'foco' && idx > 0 && idx <= dadosSimulacao.passos.length) {
        const p = dadosSimulacao.passos[idx - 1];
        const ptsFoco = [];

        if (modoAtual === "Bissecção" || modoAtual === "Falsa Posição") {
          if (p.a !== undefined && p.b !== undefined) {
            ptsFoco.push({ x: p.a, y: p.fa || 0 });
            ptsFoco.push({ x: p.b, y: p.fb || 0 });
          }
          ptsFoco.push({ x: p.x, y: p.fx || 0 });
          ptsFoco.push({ x: p.x, y: 0 });
        } else if (modoAtual === "Newton-Raphson") {
          ptsFoco.push({ x: p.x, y: p.fx || 0 });
          ptsFoco.push({ x: p.x, y: 0 });
          ptsFoco.push({ x: p.x_prox, y: 0 });
          ptsFoco.push({ x: p.x_prox, y: p.fx_prox || 0 });
        } else if (modoAtual === "Secante") {
          ptsFoco.push({ x: p.xe, y: p.fxe || 0 });
          ptsFoco.push({ x: p.xd, y: p.fxd || 0 });
          ptsFoco.push({ x: p.x, y: 0 });
          ptsFoco.push({ x: p.x, y: p.fx || 0 });
        }

        const xs = ptsFoco.map(pt => pt.x).filter(v => v !== undefined && !isNaN(v));
        const ys = ptsFoco.map(pt => pt.y).filter(v => v !== undefined && !isNaN(v)).concat([0]);

        if (xs.length > 0 && ys.length > 0) {
          const xMinF = Math.min(...xs);
          const xMaxF = Math.max(...xs);
          const yMinF = Math.min(...ys);
          const yMaxF = Math.max(...ys);

          const spanX = Math.max(xMaxF - xMinF, 0.12);
          const spanY = Math.max(yMaxF - yMinF, 0.12);

          layout.xaxis.range = [xMinF - spanX * 0.35, xMaxF + spanX * 0.35];
          layout.yaxis.range = [yMinF - spanY * 0.35, yMaxF + spanY * 0.35];
        }
      }

      Plotly.react('plotlyChart', traces, layout, { responsive: true, displayModeBar: true });
    }

    // Modal Comparativo
    async function abrirModalComparativo() {
      const modal = document.getElementById("modalComp");
      modal.classList.remove("hidden");
      lucide.createIcons();

      const payload = {
        f: document.getElementById("inpF").value,
        df: document.getElementById("inpDf").value,
        a: parseFloat(document.getElementById("inpA").value),
        b: parseFloat(document.getElementById("inpB").value),
        x0_n: parseFloat(document.getElementById("inpX0N").value),
        x0_s: parseFloat(document.getElementById("inpX0S").value),
        x1_s: parseFloat(document.getElementById("inpX1S").value),
        tol: parseFloat(document.getElementById("inpTol").value) || 1e-6,
        max_iter: parseInt(document.getElementById("inpMax").value) || 100,
        nome: nomeProblemaAtual
      };

      try {
        const resp = await fetch("/api/comparar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const dados = await resp.json();

        const tbody = document.getElementById("modalTbody");
        tbody.innerHTML = "";

        dados.dados.forEach(item => {
          const tr = document.createElement("tr");
          tr.className = "hover:bg-muted/40 transition-colors";
          const rStr = item.raiz !== null ? item.raiz.toFixed(8) : "Falha";
          const resStr = item.residuo !== null ? item.residuo.toExponential(2) : "-";
          const corSt = item.sucesso ? "text-emerald-500 font-semibold" : "text-rose-500 font-semibold";

          tr.innerHTML = `
            <td class="py-2.5 px-3 font-semibold text-foreground">${item.metodo}</td>
            <td class="py-2.5 px-3">${rStr}</td>
            <td class="py-2.5 px-3 text-center">${item.iteracoes}</td>
            <td class="py-2.5 px-3 text-right">${item.tempo_ms.toFixed(4)} ms</td>
            <td class="py-2.5 px-3 text-right">${resStr}</td>
            <td class="py-2.5 px-3 text-center ${corSt}">${item.status}</td>
          `;
          tbody.appendChild(tr);
        });

        // Gráficos de Barras com Plotly dentro do Modal
        const nomes = dados.dados.map(d => d.metodo);
        const iters = dados.dados.map(d => d.iteracoes);
        const tempos = dados.dados.map(d => d.tempo_ms);
        const cores = ['#0ea5e9', '#f59e0b', '#10b981', '#a855f7'];

        const isDark = document.documentElement.classList.contains("dark");
        const txtColor = isDark ? "#fafafa" : "#09090b";
        const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";

        const layoutIter = {
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { family: 'Inter, sans-serif', color: txtColor, size: 10 },
          margin: { l: 30, r: 10, t: 10, b: 25 },
          xaxis: { gridcolor: gridColor },
          yaxis: { gridcolor: gridColor, title: '' },
          showlegend: false
        };

        const traceIter = {
          x: nomes,
          y: iters,
          type: 'bar',
          text: iters.map(String),
          textposition: 'auto',
          marker: { color: cores }
        };

        Plotly.react('modalChartIter', [traceIter], layoutIter, { responsive: true, displayModeBar: false });

        const layoutTempo = {
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { family: 'Inter, sans-serif', color: txtColor, size: 10 },
          margin: { l: 45, r: 10, t: 10, b: 25 },
          xaxis: { gridcolor: gridColor },
          yaxis: { gridcolor: gridColor, title: 'ms' },
          showlegend: false
        };

        const traceTempo = {
          x: nomes,
          y: tempos,
          type: 'bar',
          text: tempos.map(t => t.toFixed(3) + ' ms'),
          textposition: 'auto',
          marker: { color: cores }
        };

        Plotly.react('modalChartTempo', [traceTempo], layoutTempo, { responsive: true, displayModeBar: false });

      } catch (err) {
        console.error("Erro ao comparar:", err);
      }
    }

    function fecharModal() {
      document.getElementById("modalComp").classList.add("hidden");
    }

    async function exportarExcel() {
      const resp = await fetch("/api/exportar_excel", { method: "POST" });
      const res = await resp.json();
      const fb = document.getElementById("modalExportFeedback");
      fb.classList.remove("hidden");
      fb.innerText = `✓ Planilha salva com sucesso em '${res.arquivo}'!`;
    }

    async function exportarGraficos() {
      const resp = await fetch("/api/gerar_graficos", { method: "POST" });
      const res = await resp.json();
      const fb = document.getElementById("modalExportFeedback");
      fb.classList.remove("hidden");
      fb.innerText = `✓ Figuras geradas na pasta '${res.pasta}'!`;
    }
  </script>
</body>
</html>
"""

class ServidorSimuladorHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Desativa logs no terminal para manter a saída limpa
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_SHADCN.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            req = json.loads(corpo)
        except Exception:
            req = {}

        if self.path == "/api/simular":
            try:
                f_str = req.get("f", "cos(x) - x")
                df_str = req.get("df", "-sin(x) - 1")
                a = float(req.get("a", 0.0))
                b = float(req.get("b", 1.0))
                x0_n = float(req.get("x0_n", 0.5))
                x0_s = float(req.get("x0_s", 0.0))
                x1_s = float(req.get("x1_s", 1.0))
                tol = float(req.get("tol", 1e-6))
                max_iter = int(req.get("max_iter", 100))
                metodo = req.get("metodo", "Newton-Raphson")

                f = compilar_funcao(f_str)
                df = compilar_funcao(df_str) if df_str.strip() else None

                if metodo == "Bissecção":
                    passos, status = gerar_passos_bisseccao(f, a, b, tol, max_iter)
                elif metodo == "Falsa Posição":
                    passos, status = gerar_passos_falsa_posicao(f, a, b, tol, max_iter)
                elif "Newton" in metodo:
                    passos, status = gerar_passos_newton(f, df, x0_n, tol, max_iter)
                else:
                    passos, status = gerar_passos_secante(f, x0_s, x1_s, tol, max_iter)

                # Gera curva f(x) englobando todos os pontos do método
                todos_x = [a, b, x0_n, x0_s, x1_s]
                for p_it in passos:
                    for k in ('x', 'x_prox', 'a', 'b', 'xe', 'xd'):
                        if k in p_it and p_it[k] is not None:
                            todos_x.append(float(p_it[k]))

                span = max(todos_x) - min(todos_x)
                margem = span * 0.25 if span > 0 else 1.5
                x_min = min(todos_x) - margem
                x_max = max(todos_x) + margem
                x_vals = np.linspace(x_min, x_max, 350).tolist()
                y_vals = []
                for xv in x_vals:
                    try:
                        val = float(f(xv))
                        y_vals.append(None if abs(val) > 1e6 else val)
                    except Exception:
                        y_vals.append(None)

                resposta = {
                    "passos": passos,
                    "curva_x": x_vals,
                    "curva_y": y_vals,
                    "status_final": status
                }
            except Exception as e:
                resposta = {
                    "erro": str(e),
                    "passos": [],
                    "curva_x": [],
                    "curva_y": [],
                    "status_final": f"Erro: {e}"
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resposta).encode("utf-8"))

        elif self.path == "/api/comparar":
            try:
                f_str = req.get("f", "cos(x) - x")
                df_str = req.get("df", "-sin(x) - 1")
                a = float(req.get("a", 0.0))
                b = float(req.get("b", 1.0))
                x0_n = float(req.get("x0_n", 0.5))
                x0_s = float(req.get("x0_s", 0.0))
                x1_s = float(req.get("x1_s", 1.0))
                tol = float(req.get("tol", 1e-6))
                max_iter = int(req.get("max_iter", 100))
                nome = req.get("nome", "Problema")

                f = compilar_funcao(f_str)
                df = compilar_funcao(df_str) if df_str.strip() else None

                comp = executar_comparativo(f, df, a, b, x0_n, x0_s, x1_s, tol, max_iter, nome=nome)
            except Exception as e:
                comp = {"nome": req.get("nome", "Problema"), "erro": str(e), "dados": []}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(comp).encode("utf-8"))

        elif self.path == "/api/exportar_excel":
            # Gera para os 3 problemas padrão
            from main import get_problemas_padrao
            probs = get_problemas_padrao()
            bateria = [
                executar_comparativo(p["f"], p["df"], p["a"], p["b"], p["x0_newton"], p["x0_sec"], p["x1_sec"], nome=p["nome"])
                for p in probs
            ]
            exportar_para_excel(bateria, "tabelas_comparativas.xlsx")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"sucesso": True, "arquivo": "tabelas_comparativas.xlsx"}).encode("utf-8"))

        elif self.path == "/api/gerar_graficos":
            from main import get_problemas_padrao
            probs = get_problemas_padrao()
            bateria = [
                executar_comparativo(p["f"], p["df"], p["a"], p["b"], p["x0_newton"], p["x0_sec"], p["x1_sec"], nome=p["nome"])
                for p in probs
            ]
            gerar_graficos(bateria, "graficos")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"sucesso": True, "pasta": "graficos/"}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()


def iniciar_servidor(porta=5050):
    # Procura porta livre se 5050 estiver ocupada
    for p in range(porta, porta + 20):
        try:
            servidor = http.server.ThreadingHTTPServer(("127.0.0.1", p), ServidorSimuladorHandler)
            url = f"http://localhost:{p}"
            print("\n" + "=" * 65)
            print("  ⚡ SIMULADOR DE EQUAÇÕES ALGÉBRICAS E TRANSCENDENTES")
            print("=" * 65)
            print(f"  Interface web aberta em: {url}")
            print("  Pressione Ctrl+C para encerrar o simulador.")
            print("=" * 65 + "\n")
            webbrowser.open(url)
            servidor.serve_forever()
            break
        except OSError:
            continue

if __name__ == "__main__":
    iniciar_servidor()
