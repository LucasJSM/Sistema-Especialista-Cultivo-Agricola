#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
from flask import Flask, request, jsonify, render_template
from motor_diagnostico import MotorDiagnosticoAgricola, Sintoma, Condicao, Diagnostico, Fact

# Inicializa o aplicativo Flask
app = Flask(__name__)

# --- Helper de Formatação ---
def formatar_texto(texto):
    """
    Formata o texto interno do motor para algo legível.
    Ex: 'deficiencia_de_magnesio_(Mg)' vira 'Deficiencia de magnesio (mg)'
    """
    if not texto:
        return None # Retorna None se o texto for vazio
    
    # Primeiro, substitui underscores
    texto_formatado = texto.replace('_', ' ')
    
    # Coloca em maiúscula apenas a primeira letra da string inteira
    return texto_formatado.capitalize()

# --- Rota 1: Servir a Página Web ---
@app.route('/')
def index():
    """Renderiza o nosso frontend (o index.html)"""
    return render_template('index.html')

# REGISTRA AUDITORIA EM TXT (LEITURA GERAL DA AUDITORIA)
def registro_auditoria_txt(resultado_diagnostico):
    nome_arquivo = "auditoria_diagnosticos_da_planta.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d (%d/%m) %H:%M:%S")

    if isinstance(resultado_diagnostico, list) or isinstance(resultado_diagnostico, dict):
        resultado_formatado_txt = json.dumps(resultado_diagnostico, 
                                          indent=4, 
                                          ensure_ascii=False) # Garante acentos
    else:
        # Fallback
        resultado_formatado_txt = str(resultado_diagnostico)
    
    conteudo = f"""
    AUDITORIA DE DIAGNÓSTICO
    =============================== 
    Data/Hora: {timestamp}
    Resultado do Diagnóstico:
    {resultado_formatado_txt}
    ==================================================
    """
   
   #Cria TXT com arquivo e se já foi criado faz apenas um append com o "a" 
    try:
        with open(nome_arquivo, "a", encoding="utf-8") as arquivo_auditoria:
            arquivo_auditoria.write(conteudo + "\n")
            print(f"Arquivo de Auditoria em TXT criado/atualizado!")
    except Exception as e:
        print(f"Erro ao escrever no arquivo de auditoria: {e}")

# ---------------------
# SEPARAÇÃO DAS FUNÇÕES DE REGISTRO PARA EVITAR CONFUSÃO VISUAL
# ---------------------

# --- REGISTRO DE AUDITORIA EM JSON (PARA ANÁLISE DE DADOS) ---
def registro_auditoria_json(resultado_diagnostico):
    nome_arquivo = "auditoria_sistema_especialista.jsonl"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Dicionario para a entrada de informações
    log_entry = {
        "timestamp": timestamp,
        "resultados": resultado_diagnostico 
    }

    try:
        linha_json = json.dumps(log_entry, ensure_ascii=False)

        #Abre arquivo como append
        with open(nome_arquivo, "a", encoding="utf-8") as arquivo_auditoria:
            arquivo_auditoria.write(linha_json + "\n")
            print(f"Arquivo de Auditoria JSON criado/atualizado!")
            
            
    except Exception as e:
        print(f"Erro ao escrever no arquivo de auditoria JSONL: {e}")


# --- Rota 2: A API de Diagnóstico (VERSÃO 100% FORMATADA) ---
@app.route('/diagnosticar', methods=['POST'])
def diagnosticar():
    """
    Recebe os fatos do frontend, executa o motor 
    e retorna os resultados como JSON.
    """
    fatos_json = request.json
    engine = MotorDiagnosticoAgricola()
    engine.reset()
    
    try:
        # 1. Declarar os fatos no motor
        for fato_info in fatos_json:
            tipo_fato = fato_info.get('tipo')
            dados_fato = fato_info.get('dados', {})
            
            if tipo_fato == 'Sintoma':
                engine.declare(Sintoma(**dados_fato))
            elif tipo_fato == 'Condicao':
                engine.declare(Condicao(**dados_fato))
        
        # 2. Executar o motor
        engine.run()
        
        # 3. Coletar os resultados (de AMBAS as fontes)
        causas_ja_adicionadas = set() 
        resultados_finais = []

        for f in engine.facts.values():
            
            # Fonte 1: Pega a lista principal de resultados (de _adicionar_resultado)
            if 'resultados' in f:
                for res in f['resultados']:
                    
                    # --- APLICA FORMATAÇÃO COMPLETA AQUI ---
                    res_formatado = {
                        'tipo': res.get('tipo'),
                        'causa': formatar_texto(res.get('causa')),
                        'risco': formatar_texto(res.get('risco')),
                        'recomendacao': formatar_texto(res.get('recomendacao')),
                        'recomendacao_controle': formatar_texto(res.get('recomendacao_controle')),
                        'recomendacao_corretiva': formatar_texto(res.get('recomendacao_corretiva'))
                    }
                    # Remove chaves que são None (limpa o JSON)
                    res_formatado = {k: v for k, v in res_formatado.items() if v is not None}
                    
                    resultados_finais.append(res_formatado)
                    
                    if res_formatado.get('causa'):
                        causas_ja_adicionadas.add(res_formatado.get('causa')) 
            
            # Fonte 2: Pega os diagnósticos de encadeamento (de self.declare)
            if isinstance(f, Diagnostico):
                causa_original = f.get('causa')
                causa_formatada = formatar_texto(causa_original)
                
                # Adiciona só se essa causa ainda não foi adicionada pela Fonte 1
                if causa_formatada and causa_formatada not in causas_ja_adicionadas:
                    
                    # --- APLICA FORMATAÇÃO COMPLETA AQUI TAMBÉM ---
                    diag_dict = {
                        'tipo': 'Diagnostico',
                        'causa': causa_formatada,
                        'recomendacao': formatar_texto(f.get('recomendacao')),
                        'recomendacao_controle': formatar_texto(f.get('recomendacao_controle')),
                        'recomendacao_corretiva': formatar_texto(f.get('recomendacao_corretiva'))
                    }
                    # Remove chaves que são None (limpa o JSON)
                    diag_dict = {k: v for k, v in diag_dict.items() if v is not None}

                    resultados_finais.append(diag_dict)
                    causas_ja_adicionadas.add(causa_formatada) # Marca como adicionada
        
        registro_auditoria_txt(resultado_diagnostico=resultados_finais) #Cria a auditoria com os resultados finais formatados no TXT
        registro_auditoria_json(resultado_diagnostico=resultados_finais) #Cria a auditoria com os resultados finais formatados em JSON
        # 5. Retornar a lista final e formatada
        return jsonify(resultados_finais)
    
    except Exception as e:
        # Captura erros e os envia como JSON para o frontend
        return jsonify({"erro": str(e)}), 400

# --- Comando para rodar o servidor ---
if __name__ == '__main__':
#     Roda o app em modo de debug
    app.run(debug=True, port=5000)

