from dataclasses import dataclass, field
from flask import Flask, render_template, request
from typing import List

# detalhes do evento
@dataclass
class Evento:
    nome: str
    inicio: int  # tempo em minutos
    fim: int
    capacidade_necessaria: int = 0
    projetor_necessario: bool = False

# descricao da sala de eventos
@dataclass
class Sala:
    nome: str
    capacidade: int = 0
    tem_projetor: bool = False

# agenda da sala com eventos, incluindo cálculo do último horário de fim
@dataclass
class AgendaSala:
    sala_info: Sala
    eventos: List[Evento] = field(default_factory=list)

    @property
    def ultimo_horario_fim(self) -> int:
        if not self.eventos:
            return 0
        return self.eventos[-1].fim
    
# Algoritmo de interval partitioning para alocação de eventos em salas   
def alocar_eventos(eventos: List[Evento]) -> List[List[Evento]]:
    eventos_ordenados = sorted(eventos, key=lambda e: e.inicio)
    salas_alocadas = []
    for evento in eventos_ordenados:
        alocado = False
        for sala in salas_alocadas:
            ultimo_evento_fim = sala[-1].fim if sala else 0
            if evento.inicio >= ultimo_evento_fim:
                sala.append(evento)
                alocado = True
                break
        if not alocado:
            salas_alocadas.append([evento])
    return salas_alocadas

# Aplicação flask 
app = Flask(__name__)

def parse_time(time_str):
    """Converte 'HH:MM' para minutos totais."""
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado_alocacao = None
    if request.method == 'POST':
        eventos_raw = request.form.get('eventos_input')
        
        lista_eventos = []
        if eventos_raw:
            for linha in eventos_raw.strip().split('\n'):
                try:
                    nome, inicio_str, fim_str = linha.strip().split(',')
                    lista_eventos.append(
                        Evento(
                            nome=nome.strip(),
                            inicio=parse_time(inicio_str.strip()),
                            fim=parse_time(fim_str.strip())
                        )
                    )
                except ValueError:
                    pass
        
        if lista_eventos:
            resultado_alocacao = alocar_eventos(lista_eventos)

    return render_template('index.html', alocacao=resultado_alocacao)

if __name__ == '__main__':
    app.run(debug=True)