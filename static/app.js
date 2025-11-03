document.addEventListener("DOMContentLoaded", () => {
  let fatosAcumulados = [];

  const btnFolha = document.getElementById("btn-add-folha");
  const btnPraga = document.getElementById("btn-add-praga");
  const btnSolo = document.getElementById("btn-add-solo");
  const btnClima = document.getElementById("btn-add-clima");
  const btnDiagnosticar = document.getElementById("btn-diagnosticar");
  const btnLimpar = document.getElementById("btn-limpar");
  const listaFatosUI = document.getElementById("fatos-acumulados");
  const resultadosUI = document.getElementById("resultados");

  const modalOverlay = document.getElementById("modal-overlay");
  const modalTitle = document.getElementById("modal-title");
  const modalOptions = document.getElementById("modal-options");

  function adicionarFato(tipo, dados, descricao) {
    fatosAcumulados.push({ tipo: tipo, dados: dados });
    const li = document.createElement("li");
    li.textContent = `[${tipo}] ${descricao}`;
    listaFatosUI.appendChild(li);
  }

  function limparSessao() {
    fatosAcumulados = [];
    listaFatosUI.innerHTML = "";
    resultadosUI.innerHTML = "";
  }

  /**
   * @param {string} title - O título da pergunta.
   * @param {Object} options - Um objeto onde {chave: 'valor_exibido'}
   * @returns {Promise<string|null>} - A CHAVE da opção clicada (ex: '1') ou null.
   */
  function askQuestion(title, options) {
    // Retorna uma Promessa que será resolvida quando o usuário clicar
    return new Promise((resolve) => {
      modalTitle.textContent = title;
      modalOptions.innerHTML = "";

      for (const [key, value] of Object.entries(options)) {
        const btn = document.createElement("button");
        btn.textContent = value;
        btn.onclick = () => {
          modalOverlay.classList.add("hidden");
          resolve(key); // Resolve a promessa com a CHAVE (ex: '1', 'v')
        };
        modalOptions.appendChild(btn);
      }

      modalOverlay.classList.remove("hidden");
    });
  }

  /**
   * @param {string} title - O título da pergunta.
   * @param {string} placeholder - Placeholder para o input.
   * @param {string} inputType - O tipo do input (ex: 'number', 'text').
   * @returns {Promise<string|null>} - O valor digitado ou null se cancelado.
   */
  function askForInput(title, placeholder = "", inputType = "text") {
    return new Promise((resolve) => {
      modalTitle.textContent = title;
      modalOptions.innerHTML = "";

      const input = document.createElement("input");
      input.type = inputType;
      input.placeholder = placeholder;
      input.className = "modal-input";
      if (inputType === "number") {
        input.step = "0.1";
      }

      const actionsDiv = document.createElement("div");
      actionsDiv.className = "modal-actions";

      const btnConfirm = document.createElement("button");
      btnConfirm.textContent = "Confirmar";
      btnConfirm.className = "modal-btn-confirm";
      btnConfirm.onclick = () => {
        modalOverlay.classList.add("hidden");
        resolve(input.value);
      };

      const btnCancel = document.createElement("button");
      btnCancel.textContent = "Cancelar";
      btnCancel.className = "modal-btn-cancel";
      btnCancel.onclick = () => {
        modalOverlay.classList.add("hidden");
        resolve(null);
      };

      actionsDiv.appendChild(btnCancel);
      actionsDiv.appendChild(btnConfirm);
      modalOptions.appendChild(input);
      modalOptions.appendChild(actionsDiv);

      modalOverlay.classList.remove("hidden");

      input.focus();
    });
  }

  /**
   * Exibe um modal de alerta simples com uma mensagem e um botão "OK".
   * @param {string} title - O título do modal.
   * @param {string} message - A mensagem a ser exibida.
   * @returns {Promise<void>} - Resolve quando o modal é fechado.
   */
  function showAlert(title, message) {
    return new Promise((resolve) => {
      modalTitle.textContent = title;
      modalOptions.innerHTML = "";

      // Adiciona a mensagem
      const messageEl = document.createElement("p");
      messageEl.textContent = message;
      messageEl.style.marginBottom = "20px";
      messageEl.style.fontSize = "16px";

      // Adiciona o container de ações
      const actionsDiv = document.createElement("div");
      actionsDiv.className = "modal-actions";
      actionsDiv.style.gridTemplateColumns = "1fr";

      // Botão OK
      const btnOK = document.createElement("button");
      btnOK.textContent = "OK";
      btnOK.className = "modal-btn-confirm";

      const closeModal = () => {
        modalOverlay.classList.add("hidden");
        resolve();
      };

      btnOK.onclick = closeModal;

      // Monta e exibe o modal
      actionsDiv.appendChild(btnOK);
      modalOptions.appendChild(messageEl);
      modalOptions.appendChild(actionsDiv);

      modalOverlay.classList.remove("hidden");
      btnOK.focus();
    });
  }

  async function menuFolha() {
    const local = await askQuestion("Onde é o sintoma?", {
      1: "Folhas Velhas (na base)",
      2: "Folhas Novas (no topo)",
      v: "Voltar",
    });
    if (local === "v") return;

    let dados = {};
    let descricao = "";

    if (local === "1") {
      dados.local = "folhas_velhas";
      descricao = "Local: Folhas Velhas, ";
      const aspecto = await askQuestion("Qual a aparência?", {
        1: "Amarelada uniforme",
        2: "Bordas queimadas",
        3: "Amarelada entre nervuras",
        4: "Cor verde-escura/arroxeada",
        v: "Voltar",
      });
      if (aspecto === "v") return;

      if (aspecto === "1") {
        dados.cor = "amarelada_uniforme";
        descricao += "Cor: Amarelada uniforme";
      } else if (aspecto === "2") {
        dados.aspecto = "bordas_queimadas_e_secas";
        descricao += "Aspecto: Bordas queimadas";
      } else if (aspecto === "3") {
        dados.cor = "amarelada_entre_nervuras";
        descricao += "Cor: Amarelada entre nervuras";
      } else if (aspecto === "4") {
        dados.cor = "verde_escura_com_tons_arroxeados";
        descricao += "Cor: Verde-escura/arroxeada";
      }
    } else if (local === "2") {
      dados.local = "folhas_novas";
      descricao = "Local: Folhas Novas, ";
      const aspecto = await askQuestion("Qual a aparência?", {
        1: "Amarelada entre nervuras",
        2: "Amarelada uniforme completa",
        3: "Folhas deformadas e ponto morto",
        v: "Voltar",
      });
      if (aspecto === "v") return;

      if (aspecto === "1") {
        dados.cor = "amarelada_entre_nervuras";
        descricao += "Cor: Amarelada entre nervuras";
      } else if (aspecto === "2") {
        dados.cor = "amarelada_uniforme_completa";
        descricao += "Cor: Amarelada uniforme";
      } else if (aspecto === "3") {
        dados.aspecto = "deformadas_ou_retorcidas";
        dados.ponto_crescimento = "morto";
        descricao += "Aspecto: Deformadas/Ponto morto";
      }
    }

    // Só adiciona se um fato foi criado
    if (Object.keys(dados).length > 0) {
      adicionarFato("Sintoma", dados, descricao);
    }
  }

  async function menuSolo() {
    const opcao = await askQuestion("Qual a condição do Solo/Água?", {
      1: "Solo seco, planta murcha",
      2: "Solo encharcado",
      3: "Inserir pH (Manual)",
      4: "Inserir Umidade",
      5: "Solo úmido, planta murcha (só à tarde)",
      v: "Voltar",
    });
    if (opcao === "v") return;

    if (opcao === "1") {
      adicionarFato("Condicao", { solo_umido: "seco" }, "Solo: Seco");
      adicionarFato(
        "Sintoma",
        { planta_aparencia: "murcha_pela_manha" },
        "Planta: Murcha pela manhã"
      );
    } else if (opcao === "2") {
      adicionarFato(
        "Condicao",
        { solo_umido: "encharcado" },
        "Solo: Encharcado"
      );
      adicionarFato(
        "Sintoma",
        { planta_folhas_baixas: "amareladas" },
        "Planta: Folhas baixas amareladas"
      );
    } else if (opcao === "3") {
      const phValue = await askForInput(
        "Digite o valor do pH",
        "ex: 5.5",
        "number"
      );
      if (phValue) {
        const ph = parseFloat(phValue);
        if (!isNaN(ph)) {
          adicionarFato("Condicao", { ph_solo: ph }, `Solo: pH ${ph}`);
        } else {
          alert("Valor de pH inválido. Por favor, insira um número.");
        }
      }
    }
    else if (opcao === "4") {
      // 1. PRIMEIRO, pergunta o tipo de solo
      const tipoSolo = await askQuestion("Qual o tipo do solo?", {
        arenoso: "Arenoso",
        argiloso: "Argiloso",
        v: "Voltar",
      });

      if (tipoSolo === "v") return; // Sai se o usuário clicar em Voltar

      // 2. SEGUNDO, pergunta o valor do sensor
      const umidadeValue = await askForInput(
        "Digite o valor do sensor de umidade",
        "ex: 30",
        "number"
      );

      // 3. TERCEIRO, adiciona AMBOS os fatos
      if (umidadeValue) {
        const umidade = parseFloat(umidadeValue);
        if (!isNaN(umidade)) {
          // Adiciona o fato do tipo de solo (ex: 'arenoso' ou 'argiloso')
          adicionarFato(
            "Condicao",
            { tipo_solo: tipoSolo },
            `Solo: ${tipoSolo}`
          );

          // Adiciona o fato da umidade (ex: 30)
          adicionarFato(
            "Condicao",
            { sensor_umidade_solo: umidade },
            `Sensor Umidade: ${umidade}`
          );
        } else {
          alert("Valor de umidade inválido. Por favor, insira um número.");
        }
      }
    }

    else if (opcao === "5") {
      // Adiciona os dois fatos que a regra precisa
      adicionarFato(
        "Condicao",
        { solo_umido: "umido" },
        "Solo: Úmido"
      );
      adicionarFato(
        "Sintoma",
        { planta_aparencia: "murcha_pela_tarde" },
        "Planta: Murcha pela tarde"
      );
    }
    
  }

  async function menuPraga() {
    const opcao = await askQuestion("O que você vê na planta?", {
      1: "Pó branco (talco) nas folhas",
      2: "Insetos pequenos e folhas grudentas",
      3: "Furos de lagartas",
      4: "Pontos prateados e teias finas",
      v: "Voltar",
    });
    if (opcao === "v") return;

    let dadosSintoma = {};
    let descricao = "";

    if (opcao === "1") {
      dadosSintoma.observacao = "po_branco_nas_folhas";
      descricao = "Sintoma: Pó branco nas folhas";
      adicionarFato("Sintoma", dadosSintoma, descricao);
    } else if (opcao === "2") {
      dadosSintoma.observacao = "substancia_pegajosa_escura_nas_folhas";
      dadosSintoma.observacao_inseto =
        "pequenos_insetos_verdes_ou_pretos_agrupados";
      descricao = "Sintoma: Insetos pequenos e folhas grudentas";
      adicionarFato("Sintoma", dadosSintoma, descricao);
    } else if (opcao === "3") {
      dadosSintoma.observacao = "furos_irregulares_nas_folhas";
      dadosSintoma.detalhe = "presenca_de_lagartas_ou_fezes_escuras";
      descricao = "Sintoma: Furos de lagartas";
      adicionarFato("Sintoma", dadosSintoma, descricao);
    } else if (opcao === "4") {
      dadosSintoma.observacao =
        "folhas_com_pontilhados_prateados_ou_amarelados";
      dadosSintoma.detalhe = "teias_finas_sob_as_folhas";
      descricao = "Sintoma: Pontos prateados e teias";
      adicionarFato("Sintoma", dadosSintoma, descricao);
      adicionarFato(
        "Condicao",
        { clima: "seco_e_quente" },
        "Condição: Clima seco e quente"
      );
    }
  }

  async function menuClima() {
    const opcao = await askQuestion("Qual a condição climática?", {
      1: "Risco de Geada (temp < 3°C)",
      2: "Onda de Calor (temp > 35°C e ar seco)",
      3: "Vento Forte (risco de tombar)",
      4: "Inserir Fatos Manuais (Avançado)",
      v: "Voltar",
    });
    if (opcao === "v") return;

    let dadosCondicao = {};
    let descricao = "";

    if (opcao === "1") {
      dadosCondicao.previsao_tempo = "geada_iminente";
      dadosCondicao.temperatura_ar = 2;
      descricao = "Clima: Risco de Geada";
    } else if (opcao === "2") {
      dadosCondicao.previsao_tempo = "calor_iminente";
      dadosCondicao.temperatura_ar = 36;
      descricao = "Clima: Onda de Calor";
    } else if (opcao === "3") {
      dadosCondicao.velocidade_vento = 70;
      descricao = "Clima: Vento Forte";
    }
    else if (opcao === "4") {
      // --- Esta opção permite a entrada granular ---

      // FATO: Temperatura do Ar (para geada, escaldadura)
      const tempValue = await askForInput(
        "Temperatura do Ar (em °C)? (Deixe em branco se não souber)",
        "ex: 25",
        "number"
      );
      if (tempValue) {
        const temp = parseFloat(tempValue);
        if (!isNaN(temp)) {
          adicionarFato("Condicao", { temperatura_ar: temp }, `Temp. Ar: ${temp}°C`);
        }
      }

      // FATO: Umidade do Ar (para escaldadura, fungos)
      const umidadeValue = await askForInput(
        "Umidade Relativa do Ar (em %)? (Deixe em branco se não souber)",
        "ex: 60",
        "number"
      );
      if (umidadeValue) {
        const umidade = parseFloat(umidadeValue);
        if (!isNaN(umidade)) {
          adicionarFato("Condicao", { umidade_ar: umidade }, `Umidade Ar: ${umidade}%`);
        }
      }

      // FATO: Temperatura do Solo (para pragas de solo)
      const soloTempValue = await askForInput(
        "Temperatura do Solo (em °C)? (Deixe em branco se não souber)",
        "ex: 20",
        "number"
      );
      if (soloTempValue) {
        const soloTemp = parseFloat(soloTempValue);
        if (!isNaN(soloTemp)) {
          adicionarFato("Condicao", { temperatura_solo: soloTemp }, `Temp. Solo: ${soloTemp}°C`);
        }
      }

      // --- FATOS DE CONTEXTO (SIM/NÃO) ---

      const estacao = await askQuestion("Estamos no Início da Primavera?", { 'inicio_primavera': "Sim", 'nao': "Não" });
      if (estacao === 'inicio_primavera') {
        adicionarFato("Condicao", { estacao_ano: 'inicio_primavera' }, "Estação: Início da Primavera");
      }

      const chuva = await askQuestion("Está em um período chuvoso?", { 'true': "Sim", 'nao': "Não" });
      if (chuva === 'true') {
        adicionarFato("Condicao", { periodo_chuvoso: true }, "Contexto: Período Chuvoso");
      }
      
      const floracao = await askQuestion("A cultura principal está em floração?", { 'floracao': "Sim", 'nao': "Não" });
      if (floracao === 'floracao') {
        adicionarFato("Condicao", { cultura_estagio: 'floracao' }, "Estágio: Floração");
      }
      
      const previsao = await askQuestion("Há previsão de Chuva Forte ou Granizo?", { 'chuva_forte_ou_granizo': "Sim", 'nao': "Não" });
      if (previsao === 'chuva_forte_ou_granizo') {
        adicionarFato("Condicao", { previsao_tempo: 'chuva_forte_ou_granizo' }, "Previsão: Chuva Forte/Granizo");
      }

      const historico = await askQuestion("A área tem histórico de fungos?", { 'alta_incidencia_fungica': "Sim", 'nao': "Não" });
      if (historico === 'alta_incidencia_fungica') {
        adicionarFato("Condicao", { historico_area: 'alta_incidencia_fungica' }, "Histórico: Área com fungos");
      }

      // FATO: Tipo de Cultura (para regras existentes)
      const tipoCultura = await askQuestion("Qual o tipo de cultura principal?", {
        'hortalica_folhosa': "Hortaliça Folhosa (ex: Alface)",
        'sensivel_ao_frio': "Sensível ao Frio (ex: Tomate)",
        'porte_alto_ex_milho_ou_banana': "Porte Alto (ex: Milho)",
        'outra': "Outra / Não sei"
      });
      if (tipoCultura !== 'v' && tipoCultura !== 'outra') {
         adicionarFato("Condicao", { tipo_cultura: tipoCultura }, `Cultura: ${tipoCultura.replace(/_/g, ' ')}`);
      }
      
      // Não definimos 'descricao', pois esta opção adiciona múltiplos fatos.
      // O 'if (descricao)' no final será pulado, o que está correto.
    }
    if (descricao) {
      adicionarFato("Condicao", dadosCondicao, descricao);
    }
  }

  async function executarDiagnostico() {
    if (fatosAcumulados.length === 0) {
      showAlert(
        "Atenção",
        "Por favor, adicione pelo menos um fato antes de diagnosticar."
      );
      return;
    }
    resultadosUI.innerHTML = "Processando...";

    try {
      const resposta = await fetch("/diagnosticar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(fatosAcumulados),
      });

      if (!resposta.ok) {
        const erro = await resposta.json();
        throw new Error(`Erro na API: ${erro.erro || resposta.statusText}`);
      }

      const resultados = await resposta.json();

      resultadosUI.innerHTML = "";
      if (resultados.length === 0) {
        resultadosUI.innerHTML =
          "<div>Nenhuma conclusão pôde ser determinada.</div>";
        return;
      }

      resultados.forEach((res) => {
        const div = document.createElement("div");
        if (res.tipo === "Alerta") {
          div.className = "alerta";
          div.innerHTML = `<strong>ALERTA:</strong> ${res.risco}<br><strong>Ação:</strong> ${res.recomendacao}`;
        } else if (res.tipo === "Diagnostico") {
          div.className = "diagnostico";
          let html = "<strong>DIAGNÓSTICO:</strong><br>";
          if (res.causa) html += `<strong>Causa:</strong> ${res.causa}<br>`;
          if (res.recomendacao)
            html += `<strong>Recomendação:</strong> ${res.recomendacao}<br>`;
          if (res.recomendacao_controle)
            html += `<strong>Controle:</strong> ${res.recomendacao_controle}<br>`;
          if (res.recomendacao_corretiva)
            html += `<strong>Correção:</strong> ${res.recomendacao_corretiva}<br>`;
          div.innerHTML = html;
        }
        resultadosUI.appendChild(div);
      });
    } catch (erro) {
      resultadosUI.innerHTML = `<div class="alerta">Erro ao processar: ${erro.message}</div>`;
    }
  }

  btnFolha.addEventListener("click", menuFolha);
  btnSolo.addEventListener("click", menuSolo);
  btnPraga.addEventListener("click", menuPraga);
  btnClima.addEventListener("click", menuClima);

  btnDiagnosticar.addEventListener("click", executarDiagnostico);
  btnLimpar.addEventListener("click", limparSessao);
});
