from dataclasses import dataclass, field
from flask import Flask, render_template, request
from typing import List, Dict

CAPACIDADE_BANDA = 500       # Mochila 1 
CAPACIDADE_ELETRONICOS = 3   # Mochila 2 
LIMITE_SALAS = 5             # Limite máximo de salas

DB_SERVICOS = {
    "Streaming de vídeo e áudio": 175,
    "Videoconferência e reuniões online": 225,
    "Monitoramento remoto": 125,
    "Controle de automação via IoT": 75,
    "Serviço de compartilhamento de tela e mídia": 125,
    "Serviço de jogos em nuvem": 325,
    "Serviços de backup automático de dados locais": 175,
    "Assistentes virtuais": 75,
    "Painel de informações ao vivo": 100,
    "Rede Wi-Fi para visitantes": 225,
    "Monitoramento de uso de equipamentos": 75
}

DB_EQUIPAMENTOS = {
    "Smart TV": 1,
    "Monitor de alta resolução e Computador": 2,
    "Projetor com conexão Wi-Fi": 1,
    "Caixas de som Bluetooth": 1,
    "Assistente de voz Alexa": 1,
    "Tablet para controle de sistema ou uso dos visitantes": 1,
    "Painel digital interativo": 1,
    "Impressora": 2,
    "Dispositivo de videoconferência completo": 2,
    "Console de jogos": 1,
    "Totem interativo com informações ou cadastro": 2
}

DB_PRIORIDADES = {
    "Crítica": 100,
    "Alta": 75,
    "Média": 50,
    "Baixa": 25
}

HORARIOS = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30)]

DB_AGENDAMENTOS: Dict[str, List['Agendamento']] = {}

# detalhes do evento
@dataclass
class Evento:
    nome: str
    inicio: int  # tempo em minutos
    fim: int

@dataclass
class Agendamento:
    evento: Evento
    recursos_alocados: List['ResultadoAlocacao']
    valor_total: float
    peso_banda_total: float
    peso_eletronicos_total: float

@dataclass
class ItemMochila:
    nome: str
    peso: int
    valor: int
    custo_beneficio: float = field(init=False) 

    def __post_init__(self):
        # Calcula o custo-benefício (Valor / Peso)
        self.custo_beneficio = self.valor / self.peso if self.peso > 0 else 0

@dataclass
class ResultadoAlocacao:
    nome_item: str
    fracao_alocada: float  # Ex: 1.0 para 100%, 0.33 para 33%
    peso_alocado: float
    valor_ganho: float

def verificar_conflito_horario(nome_sala: str, novo_evento: Evento) -> bool:
    """ Checa conflito de intervalo (Interval Partitioning) para uma sala """
    if nome_sala not in DB_AGENDAMENTOS:
        DB_AGENDAMENTOS[nome_sala] = [] # Cria a sala no DB se for nova
        return False # Sala nova, sem conflitos
    
    for agendamento_existente in DB_AGENDAMENTOS[nome_sala]:
        evento_existente = agendamento_existente.evento
        
        # Lógica de conflito de intervalo
        if (novo_evento.inicio < evento_existente.fim) and \
           (novo_evento.fim > evento_existente.inicio):
            return True # Conflito encontrado
    return False # Sem conflitos
    
def calcular_mochila_banda(capacidade_total: int, itens_solicitados: List[ItemMochila]) -> tuple:

    # ordenar pelo maior custo-benefício
    itens_ordenados = sorted(itens_solicitados, key=lambda x: x.custo_beneficio, reverse=True)
    
    resultados_alocacao = []
    capacidade_restante = capacidade_total
    valor_total_final = 0.0
    peso_total_final = 0.0

    for item in itens_ordenados:
        if capacidade_restante <= 0:
            # Mochila cheia, rejeita o item
            resultados_alocacao.append(ResultadoAlocacao(item.nome, 0.0, 0.0, 0.0))
            continue
        
        if item.peso <= capacidade_restante:
            # Item cabe 100%
            fracao = 1.0
            capacidade_restante -= item.peso
            valor_ganho = item.valor
            peso_alocado = item.peso
        else:
            # Item cabe parcialmente
            fracao = capacidade_restante / item.peso
            peso_alocado = capacidade_restante
            valor_ganho = item.valor * fracao
            capacidade_restante = 0 

        valor_total_final += valor_ganho
        peso_total_final += peso_alocado
        resultados_alocacao.append(ResultadoAlocacao(item.nome, fracao, peso_alocado, valor_ganho))

    return resultados_alocacao, valor_total_final, peso_total_final

def calcular_mochila_eletronicos(capacidade_total: int, itens_solicitados: List[ItemMochila]) -> tuple:

    # ordenar pelo maior custo-benefício
    itens_ordenados = sorted(itens_solicitados, key=lambda x: x.custo_beneficio, reverse=True)
    
    resultados_alocacao = []
    capacidade_restante = capacidade_total
    valor_total_final = 0.0
    peso_total_final = 0.0
    
    itens_alocados = []
    itens_rejeitados = []

    for item in itens_ordenados:
        if item.peso <= capacidade_restante:
            capacidade_restante -= item.peso
            valor_total_final += item.valor
            peso_total_final += item.peso
            itens_alocados.append(ResultadoAlocacao(item.nome, 1.0, item.peso, item.valor))
        else:
            # Item não cabe
            itens_rejeitados.append(ResultadoAlocacao(item.nome, 0.0, 0.0, 0.0))
            
    # Retorna os alocados e os rejeitados
    return (itens_alocados + itens_rejeitados), valor_total_final, peso_total_final

# Aplicação flask 
app = Flask(__name__)

def parse_time(time_str):
    """Converte 'HH:MM' para minutos totais."""
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado_final = None
    erro_validacao = None

    if request.method == 'POST':
        nome_evento_str = request.form.get('nome_evento')
        inicio_str = request.form.get('inicio_str')
        fim_str = request.form.get('fim_str')

        if inicio_str == fim_str:
            erro_validacao = "ERRO: O horário de início não pode ser igual ao horário de fim."
        else:
            novo_evento = Evento(
                nome=nome_evento_str,
                inicio=parse_time(inicio_str),
                fim=parse_time(fim_str)
            )

            # Prepara os itens para as Mochilas 
            itens_banda_solicitados = []
            itens_eletronicos_solicitados = []

            servicos_selecionados = request.form.getlist('servicos')
            for servico in servicos_selecionados:
                prioridade_str = request.form.get(f"prioridade_servico_{servico}")
                valor = DB_PRIORIDADES.get(prioridade_str, 25)
                peso = DB_SERVICOS.get(servico)
                itens_banda_solicitados.append(ItemMochila(servico, peso, valor))

            equipamentos_selecionados = request.form.getlist('equipamentos')
            for equip in equipamentos_selecionados:
                prioridade_str = request.form.get(f"prioridade_equipamento_{equip}")
                valor = DB_PRIORIDADES.get(prioridade_str, 25)
                peso = DB_EQUIPAMENTOS.get(equip)
                itens_eletronicos_solicitados.append(ItemMochila(equip, peso, valor))


            # INTERVAL PARTITIONING
            sala_alocada_nome = None
            
            for i in range(1, LIMITE_SALAS + 1): 
                sala_nome_atual = f"Sala {i}"
                if not verificar_conflito_horario(sala_nome_atual, novo_evento):
                    sala_alocada_nome = sala_nome_atual
                    break # Encontrou uma sala livre
            
            # Verificacao limite de salas
            if sala_alocada_nome is None:
                # Se o loop terminou e não encontrou sala
                erro_validacao = f"ERRO: Todas as {LIMITE_SALAS} salas estão ocupadas neste horário. Não é possível agendar."
            else:

                # Mochila 1
                (alocacao_banda, valor_banda, peso_banda) = calcular_mochila_banda(
                    CAPACIDADE_BANDA, itens_banda_solicitados
                )
                
                # Mochila 2:
                (alocacao_eletronicos, valor_eletronicos, peso_eletronicos) = calcular_mochila_eletronicos(
                    CAPACIDADE_ELETRONICOS, itens_eletronicos_solicitados
                )
                
                # Salvar e preparar resultado
                alocacao_final_combinada = alocacao_banda + alocacao_eletronicos
                valor_total_combinado = valor_banda + valor_eletronicos
                
                agendamento_salvo = Agendamento(
                    evento=novo_evento,
                    recursos_alocados=alocacao_final_combinada,
                    valor_total=valor_total_combinado,
                    peso_banda_total=peso_banda,
                    peso_eletronicos_total=peso_eletronicos
                )
                DB_AGENDAMENTOS[sala_alocada_nome].append(agendamento_salvo)
                
                resultado_final = {
                    "alocacoes": alocacao_final_combinada,
                    "valor_total": valor_total_combinado,
                    "evento": novo_evento,
                    "sala": sala_alocada_nome,
                    "capacidade_banda": CAPACIDADE_BANDA,
                    "peso_banda": peso_banda,
                    "capacidade_eletronicos": CAPACIDADE_ELETRONICOS,
                    "peso_eletronicos": peso_eletronicos
                }

    return render_template('index.html',
                           resultado=resultado_final, 
                           erro=erro_validacao,
                           horarios=HORARIOS,
                           servicos_db=DB_SERVICOS,
                           equipamentos_db=DB_EQUIPAMENTOS,
                           prioridades_db=DB_PRIORIDADES,
                           agendamentos_atuais=DB_AGENDAMENTOS
                           )

if __name__ == '__main__':
    app.run(debug=True)