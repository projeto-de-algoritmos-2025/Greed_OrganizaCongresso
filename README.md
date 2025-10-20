# Agemdador de Salas Inteligente com Alocador de Recursos

**Número da Lista**: 28<br>
**Conteúdo da Disciplina**: Greed<br>

## Alunos
| Matrícula | Nome |  
|:----------:|:---------------------------:|  
| 20/2046229 | Kallyne Macêdo Passos |  
| 20/0022199 | Leonardo Sobrinho de Aguiar | 

## Sobre 

O "Agendador de Salas Inteligente" é uma aplicação web desenvolvida para otimizar a alocação de recursos e o agendamento de eventos em salas de um congresso ou centro de convenções. O sistema gerencia a reserva de salas evitando conflitos de horário através do algoritmo de *Interval Partitioning*. Além disso, otimiza a alocação de dois tipos de recursos limitados: banda de internet e equipamentos eletrônicos.

Para a alocação de banda de internet, foi utilizado o algoritmo da **Mochila Fracionária**, que permite a alocação parcial de recursos para maximizar o valor (prioridade) total. Já para os equipamentos eletrônicos, foi implementado o algoritmo da **Mochila Booleana**, onde um item só pode ser inteiramente alocado ou não. O objetivo é maximizar a soma das prioridades dos serviços e equipamentos alocados, respeitando as capacidades máximas de cada sala.


## Screenshots

<div align="center">
 
Página Inicial
![Imagem do WhatsApp de 2025-10-20 à(s) 15 47 14_30257b68](https://github.com/user-attachments/assets/3f448901-f672-4cc5-bb59-d5ab2951a41c)</div>
<br>
<div align="center">
 
Agendamento Concluído com Sucesso
![Imagem do WhatsApp de 2025-10-20 à(s) 15 47 14_e8877513](https://github.com/user-attachments/assets/280f05ac-2678-44aa-ac26-d5a84d05ef69)</div>
<br>
<div align="center">
 
Alocação de Pesos
![Imagem do WhatsApp de 2025-10-20 à(s) 15 47 14_279336b0](https://github.com/user-attachments/assets/01066b55-af55-4b58-9662-84fe64799832)</div>
<br>

<div align="center">

Agendamentos Atuais
![Imagem do WhatsApp de 2025-10-20 à(s) 15 47 15_d0b0ed7b](https://github.com/user-attachments/assets/55fe5bc7-5c2d-409c-b82c-21be931800a0)</div>



## Guia de Instalação 

**Linguagem**: Python<br>
**Framework**: Flask<br>
**Pré-requisitos**: Navegador instalado, Python e Flask presentes no computador; clonar o repositório localmente.

### Passo a Passo

### 1. Clonar repositório:
```bash
git clone https://github.com/projeto-de-algoritmos-2025/Greed_OrganizaCongresso
```
### 2. Instale as Dependências:
Abra um terminal ou prompt de comando na pasta do projeto e execute:
```bash
pip install Flask
```
### 3. Inicie o Servidor:
Digite no mesmo terminal:
```bash
python app.py
```
### 4. Acesse a Aplicação:
Abra seu navegador web e acesse o seguinte endereço: http://127.0.0.1:5000

## Uso
Após iniciar a aplicação, a interface web será exibida:

1.  **Preencha os dados do evento**: Insira o nome do evento, o horário de início e o horário de fim.
2.  **Selecione os Serviços de Internet**: Marque os serviços de internet necessários e defina a prioridade de cada um (Crítica, Alta, Média, Baixa).
3.  **Selecione os Equipamentos Eletrônicos**: Marque os equipamentos desejados e, da mesma forma, defina suas prioridades.
4.  **Clique em "Agendar e Otimizar Recursos"**: O sistema irá procurar uma sala disponível no horário solicitado e realizará a alocação otimizada dos recursos.
5.  **Veja o Resultado**: O resultado será exibido na tela, informando a sala agendada, os recursos que foram total ou parcialmente alocados e os que foram recusados, junto com um resumo do consumo de banda e espaços de equipamentos.
