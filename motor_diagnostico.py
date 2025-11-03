#!/usr/bin/env python
# -*- coding: utf-8 -*-

from experta import *

# --- 1. Definição dos Fatos ---
class Sintoma(Fact):
    pass
class Condicao(Fact):
    pass
class Diagnostico(Fact):
    pass
class Alerta(Fact):
    pass

# --- 2. Criação do Motor e da Base de Conhecimento (Regras) ---
class MotorDiagnosticoAgricola(KnowledgeEngine):
    
    @DefFacts()
    def _fatos_iniciais(self):
        yield Fact(acao="buscar_solucao")
        yield Fact(resultados=[]) # Lista para acumular nossos resultados

    def _adicionar_resultado(self, tipo, dados):
        """Helper para adicionar um resultado à nossa lista de fatos."""
        for f in self.facts.values(): 
            if 'resultados' in f: 
                lista_resultados_antiga = f['resultados']
                nova_lista = list(lista_resultados_antiga)
                nova_lista.append({'tipo': tipo, **dados})
                self.modify(f, resultados=nova_lista)
                break

    # --- GRUPO 1: GESTÃO HÍDRICA ---

    # 1
    @Rule(Condicao(sensor_umidade_solo=P(lambda x: x < 30)), 
          Condicao(tipo_solo='arenoso'))
    def regra_irrigacao_solo_arenoso(self):
        self._adicionar_resultado('Diagnostico', {'causa': 'baixa_umidade_em_solo_arenoso','recomendacao': 'irrigar_agora_ciclo_curto'})

    # 2
    @Rule(Condicao(sensor_umidade_solo=P(lambda x: x < 40)), 
          Condicao(tipo_solo='argiloso'))
    def regra_irrigacao_solo_argiloso(self):
        self._adicionar_resultado('Diagnostico', {'causa': 'baixa_umidade_em_solo_argiloso','recomendacao': 'irrigar_agora_ciclo_longo'})

    # 3
    @Rule(Sintoma(planta_aparencia='murcha_pela_manha'), 
          Condicao(solo_umido='seco'))
    def regra_estresse_hidrico_severo(self):
        self._adicionar_resultado('Diagnostico', {'causa': 'estresse_hidrico_severo', 'recomendacao': 'irrigar_imediatamente'})

    # 4
    @Rule(Sintoma(planta_aparencia='murcha_pela_tarde'), 
          Condicao(solo_umido='umido'), 
          Condicao(temperatura_ar=P(lambda x: x > 30)))
    def regra_estresse_termico(self):
        self._adicionar_resultado('Diagnostico', {'causa': 'estresse_termico', 'recomendacao': 'nao_irrigar_agora_verificar_sombreamento'})

    # 5
    @Rule(Condicao(solo_umido='encharcado'), 
          Sintoma(planta_folhas_baixas='amareladas'))
    def regra_excesso_agua(self):
        self._adicionar_resultado('Diagnostico', {'causa': 'excesso_de_agua_asfixia_radicular', 'recomendacao': 'suspender_irrigacao_e_checar_drenagem'})

    # 6
    @Rule(Condicao(ph_solo=P(lambda x: x > 7.5)))
    def regra_solo_alcalino(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'solo_alcalino_(pH_alto)',
            'recomendacao': 'pH alto detectado. Isso pode travar a absorcao de micronutrientes (como Ferro). Aplicar enxofre elementar ou sulfato de amonio para reduzir o pH.'
        })

   # 7
    @Rule(OR(Diagnostico(causa='deficiencia_de_calcio_(Ca)'),
             Diagnostico(causa='deficiencia_de_magnesio_(Mg)')),
          Condicao(ph_solo=P(lambda x: x < 5.5)))
    def regra_corrigir_ph_para_Ca_Mg(self):
        self._adicionar_resultado('Diagnostico', {
            'recomendacao_corretiva': 'pH baixo detectado. Aplicar calcário dolomítico (corrige pH e fornece Ca/Mg).'
        })

    # --- GRUPO 2: DIAGNÓSTICO NUTRICIONAL ---
    
    # 8
    @Rule(Sintoma(local='folhas_velhas', 
                  cor='amarelada_uniforme'))
    def regra_deficiencia_nitrogenio(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'deficiencia_de_nitrogenio_(N)',
            'recomendacao': 'Aplicar fertilizante nitrogenado (ex: ureia, nitrato de amônio).' 
        })

    # 9
    @Rule(Sintoma(local='folhas_velhas', 
                  cor='verde_escura_com_tons_arroxeados'))
    def regra_deficiencia_fosforo(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'deficiencia_de_fosforo_(P)',
            'recomendacao': 'Aplicar fertilizante fosfatado (ex: superfosfato simples/triplo).'
        })

    # 10
    @Rule(Sintoma(local='folhas_velhas', 
                  aspecto='bordas_queimadas_e_secas'))
    def regra_deficiencia_potassio(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'deficiencia_de_potassio_(K)',
            'recomendacao': 'Aplicar fertilizante potássico (ex: cloreto de potássio).'
        })

    # 11
    @Rule(Sintoma(local='folhas_velhas', 
                  cor='amarelada_entre_nervuras'))
    def regra_deficiencia_magnesio(self):
        # Esta regra declara um Fato, pois ela pode ser usada
        # pela regra de correção de pH (encadeamento)
        self.declare(Diagnostico(
            causa='deficiencia_de_magnesio_(Mg)',
            recomendacao='Aplicar sulfato de magnésio ou calcário dolomítico (se pH baixo).'
        ))

    # 12
    @Rule(Sintoma(local='folhas_novas', 
                  cor='amarelada_entre_nervuras'))
    def regra_deficiencia_ferro(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'deficiencia_de_ferro_(Fe)',
            'recomendacao': 'Aplicar quelato de ferro (Fe-EDTA) no solo ou via foliar.' 
        })

    # 13
    @Rule(Sintoma(local='folhas_novas', 
                  aspecto='deformadas_ou_retorcidas', 
                  ponto_crescimento='morto'))
    def regra_deficiencia_calcio(self):
        self.declare(Diagnostico(
            causa='deficiencia_de_calcio_(Ca)',
            recomendacao='Aplicar gesso agrícola ou nitrato de cálcio.' 
        ))

    # 14
    @Rule(Sintoma(local='folhas_novas', 
                  cor='amarelada_uniforme_completa'))
    def regra_deficiencia_enxofre(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'deficiencia_de_enxofre_(S)',
            'recomendacao': 'Aplicar sulfato de amônio ou gesso agrícola (fontes de enxofre).' 
        })

 

    # --- GRUPO 3: DIAGNÓSTICO DE DOENÇAS E PRAGAS ---

    # 15
    @Rule(Sintoma(observacao='po_branco_nas_folhas'))
    def regra_oidio(self):
        self.declare(Diagnostico(
            causa='infeccao_fungica_oidio',
            recomendacao='Aplicar fungicida à base de enxofre ou bicarbonato de potássio.'
        ))

    # 16
    @Rule(Sintoma(observacao='po_branco_nas_folhas'),
          Sintoma(observacao_inseto='pequenos_insetos_verdes_ou_pretos_agrupados'),
          salience=5)
    def regra_co_infeccao_oidio_pulgoes(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'co_infeccao_severa_(oidio_e_pulgoes)',
            'recomendacao': 'ATAQUE COMBINADO: A planta está sendo atacada por fungos (Oídio) e pragas (Pulgões). Trate os Pulgões (sabão inseticida) PRIMEIRO, pois eles sugam a seiva e enfraquecem a planta. Em seguida, trate o Oídio (fungicida).'
        })

    # 17
    @Rule(Sintoma(observacao_inseto='pequenos_insetos_verdes_ou_pretos_agrupados'),
          Condicao(previsao_tempo='geada_iminente'),
          salience=5)
    def alerta_geada_em_planta_enfraquecida(self):
        self._adicionar_resultado('Alerta', {
            'risco': 'Risco Critico: Geada em planta enfraquecida por pragas',
            'recomendacao': 'A infestação de pulgões/afídeos já enfraqueceu a planta. A geada iminente tem alta probabilidade de ser letal. A prioridade máxima é proteger a planta fisicamente (com manta térmica) ANTES de controlar a praga.'
        })

    # 18
    @Rule(Sintoma(observacao='substancia_pegajosa_escura_nas_folhas', 
                  observacao_inseto='pequenos_insetos_verdes_ou_pretos_agrupados'))
    def regra_pulgoes(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'infestacao_de_pulgoes_(afideos)',
            'recomendacao_controle': 'aplicar_oleo_de_neem_ou_sabao_inseticida'
        })

    # 19
    @Rule(Sintoma(observacao='furos_irregulares_nas_folhas', 
                  detalhe='presenca_de_lagartas_ou_fezes_escuras'))
    def regra_lagartas(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'ataque_de_lagartas',
            'recomendacao_controle': 'aplicar_bacillus_thuringiensis_(BT)'
        })

    # 20
    @Rule(Sintoma(observacao='folhas_com_pontilhados_prateados_ou_amarelados', 
                  detalhe='teias_finas_sob_as_folhas'), 
          Condicao(clima='seco_e_quente'))
    def regra_acaro_rajado(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'infestacao_de_acaro_rajado',
            'recomendacao_controle': 'aumentar_umidade_relativa_e_aplicar_acaricida'
        })

    # 21
    @Rule(Sintoma(observacao='furos_irregulares_nas_folhas'),
          Condicao(solo_umido='encharcado'),
          salience=5)
    def alerta_risco_infeccao_dupla(self):
        self._adicionar_resultado('Alerta', {
            'risco': 'Risco Alto de Infecção Secundária (Raiz e Folha)',
            'recomendacao': 'A planta está sofrendo estresse duplo: as raízes estão asfixiadas (solo encharcado) e as folhas estão danificadas (lagartas). A prioridade é suspender a irrigação e checar a drenagem. Os furos das lagartas são uma porta de entrada para fungos/bactérias.'
        })

    # --- GRUPO 4: ALERTAS AMBIENTAIS E PREVENTIVOS ---

    # 22
    @Rule(Condicao(temperatura_ar=P(lambda x: x > 35)), 
          Condicao(previsao_tempo='calor_iminente'))
    def alerta_escaldadura(self):
        self._adicionar_resultado('Alerta', {'risco': 'Risco alto de escaldadura (queima solar)', 'recomendacao': 'Ativar sombrite ou nebulização'})

    # 23
    @Rule(Condicao(previsao_tempo='geada_iminente'), 
          Condicao(temperatura_ar=P(lambda x: x < 3)))
    def alerta_geada(self):
        self._adicionar_resultado('Alerta', {'risco': 'Risco iminente de geada', 'recomendacao': 'Cobrir plantas com manta térmica ou irrigar por aspersão na madrugada'})

    # 24
    @Rule(Condicao(velocidade_vento=P(lambda x: x > 60)))
    def alerta_acamamento(self):
        self._adicionar_resultado('Alerta', {'risco': 'Risco de acamamento (tombamento) pelo vento', 'recomendacao': 'Reforçar estacas ou quebra-ventos'})

    # 25
    @Rule(Condicao(umidade_ar=P(lambda x: x > 85)), 
          Condicao(periodo_chuvoso=True), 
          Condicao(historico_area='alta_incidencia_fungica'))
    def recomendacao_preventiva_fungo(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'condicoes_favoraveis_a_fungos_(alta_umidade_e_chuva)',
            'recomendacao': '[PREVENTIVO] Aplicar fungicida a base de cobre devido à alta umidade.'
        })
    # 26
    @Rule(Condicao(estacao_ano='inicio_primavera'), 
          Condicao(temperatura_solo=P(lambda x: x > 18)))
    def recomendacao_monitoramento_pragas_solo(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'risco_de_eclosao_de_pragas_de_solo_(primavera_e_solo_quente)',
            'recomendacao': '[MONITORAMENTO] Iniciar monitoramento de pragas de solo (ex: larvas).'
        })
    # 27
    @Rule(Condicao(cultura_estagio='floracao'), 
          Condicao(previsao_tempo='chuva_forte_ou_granizo'))
    def alerta_perda_floracao(self):
        self._adicionar_resultado('Alerta', {'risco': 'Risco de perda de flores e falha na polinização', 'recomendacao': 'Se possível, proteger estruturas (ex: estufas)'})

    # 28
    @Rule(Condicao(umidade_ar=P(lambda x: x > 80)),
          Condicao(temperatura_ar=P(lambda x: 15 < x < 25)))
    def alerta_risco_mildio(self):
        self._adicionar_resultado('Alerta', {
            'risco': 'Risco alto de Míldio (Downy Mildew)',
            'recomendacao': 'Condições (alta umidade e temperatura amena) são ideais para Míldio. Aumente a ventilação/espaçamento e prepare fungicida protetor (ex: cúprico).'
        })

    # 29
    @Rule(Condicao(cultura_estagio='floracao'),
          Condicao(temperatura_ar=P(lambda x: x > 38)))
    def alerta_abortamento_calor(self):
        self._adicionar_resultado('Alerta', {
            'risco': 'Risco de abortamento floral por calor extremo',
            'recomendacao': 'Temperaturas acima de 38°C podem esterilizar o pólen e causar a queda de flores. Aumente a frequência de irrigação para resfriar a planta e, se possível, ative o sombreamento.'
        })

    # 30
    @Rule(Condicao(temperatura_ar=P(lambda x: 5 < x < 12)),
          Condicao(temperatura_solo=P(lambda x: x < 15)))
    def diagnostico_estresse_frio(self):
        self._adicionar_resultado('Diagnostico', {
            'causa': 'estresse_por_frio_e_solo_frio_(crescimento_lento)',
            'recomendacao': 'O frio no ar e no solo reduz o metabolismo da planta e a absorção de nutrientes (especialmente Fósforo). Considere usar cobertura de solo (mulching) para aquecer o solo ou aplicar fertilizante foliar.'
        })
    # --- REGRA FINAL: COLETA DE RESULTADOS ---
    
    @Rule(AS.f_acao << Fact(acao='buscar_solucao'),
          Fact(resultados=MATCH.r), 
          salience=-100) 
    def coletar_resultados(self, f_acao, r):
        self.retract(f_acao) 
        
        print("\n--- RELATÓRIO DO SISTEMA ESPECIALISTA ---")
        
        diagnosticos_encontrados = [item for item in r if item['tipo'] == 'Diagnostico']
        alertas_encontrados = [item for item in r if item['tipo'] == 'Alerta']
        
        for f in self.facts.values():
            if isinstance(f, Diagnostico):
                if not any(d.get('causa') == f.get('causa') for d in diagnosticos_encontrados if d.get('causa')):
                    diagnosticos_encontrados.append(f)

        if not diagnosticos_encontrados and not alertas_encontrados:
            print("Nenhuma conclusão pôde ser determinada com os fatos fornecidos.")
            return

        if alertas_encontrados:
            print("\n[ALERTAS PREVENTIVOS]:")
            for i, alerta in enumerate(alertas_encontrados):
                print(f"  Alerta {i+1}: {alerta.get('risco')}")
                print(f"  Ação: {alerta.get('recomendacao')}")

        if diagnosticos_encontrados:
            print("\n[DIAGNÓSTICOS E RECOMENDAÇÕES]:")
            for i, d in enumerate(diagnosticos_encontrados):
                print(f"  Diagnóstico {i+1}:")
                if d.get('causa'):
                    print(f"    Causa Provável: {d.get('causa')}")
                if d.get('recomendacao'):
                    print(f"    Recomendação Imediata: {d.get('recomendacao')}")
                if d.get('recomendacao_controle'):
                    print(f"    Controle Específico: {d.get('recomendacao_controle')}")
                if d.get('recomendacao_corretiva'):
                    print(f"    Correção Específica: {d.get('recomendacao_corretiva')}")

        print("\n--- Fim do Relatório ---")