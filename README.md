# Relógio de Terminal Minimalista
---

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/8a249583-28c5-4b5d-bedb-08e7f570a15c" />
modo padrão

modo minimax

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1d86872e-790c-49ad-aa22-4caed0cfbac8" />

`PyClock` é um relógio de terminal versátil e estilizável escrito em Python usando a biblioteca `curses`. Ele vai além de apenas mostrar as horas, oferecendo um cronômetro, temporizador, método Pomodoro, relógio mundial e alarmes, tudo em uma interface de texto limpa.

 <!-- Imagem de exemplo, substitua pelo seu próprio screenshot se desejar -->

## Funcionalidades

- **Relógio Digital Grande**: Exibição clara da hora em arte ASCII.
- **Múltiplos Modos**:
  - **Relógio**: Exibição padrão da hora com suporte a alarmes.
  - **Cronômetro**: Meça o tempo decorrido com suporte a voltas (laps).
  - **Temporizador**: Contagem regressiva a partir de uma duração definida.
  - **Pomodoro**: Gerenciador de tempo com ciclos de trabalho e descanso configuráveis.
  - **Relógio Mundial**: Exiba a hora atual em múltiplos fusos horários.
- **Customização**:
  - Alterne entre os formatos 12h/24h.
  - Mostre ou oculte os segundos, a data e citações inspiradoras.
  - Mude a cor do relógio.
  - Ative o "Modo Zen" para uma interface minimalista.
- **Persistência**: Suas configurações (cor, fusos horários, alarmes) são salvas e carregadas automaticamente.

## Instalação e Execução

1.  **Pré-requisitos**: Certifique-se de ter o Python 3 instalado.

2.  **Instale as dependências**: O programa requer a biblioteca `pytz`.

    ```bash
    pip install pytz
    ```

3.  **Execute o programa**:

    ```bash
    python3 /caminho/para/seu/clock.py
    ```
    ou, se o arquivo for executável (`chmod +x clock.py`):
    ```bash
    ./caminho/para/seu/clock.py
    ```

## Como Usar

O programa possui dois métodos de interação: atalhos de teclado para ações rápidas e um modo de comando para configurações mais complexas.

### Atalhos de Teclado

| Tecla | Ação                                           |
| :---- | :--------------------------------------------- |
| `q`   | Sair do programa.                              |
| `a`   | Mudar para o modo **Relógio** (Clock).         |
| `w`   | Mudar para o modo **Cronômetro** (Stopwatch).  |
| `t`   | Mudar para o modo **Temporizador** (Timer).    |
| `p`   | Mudar para o modo **Pomodoro**.                |
| `z`   | Mudar para o modo **Relógio Mundial** (World). |
| `o`   | Ativar/desativar o **Modo Zen** (interface limpa). |
| `c`   | Mudar a **cor** do relógio.                    |
| `s`   | Mostrar/ocultar os **segundos**.               |
| `h`   | Alternar entre formato **12h/24h**.            |
| `d`   | Mostrar/ocultar a **data**.                    |
| `b`   | Ativar/desativar o **piscar** dos dois pontos. |
| `?`   | Exibir ajuda rápida dos comandos.              |
| `[`   | Entrar no modo de comando.                     |

### Modo de Comando

Pressione `[` para começar a digitar um comando, termine com `]` e pressione `Enter`.

#### Comandos Gerais
- `[quit]` ou `[exit]`: Sai do programa.
- `[help]`: Mostra a lista de comandos disponíveis.
- `[date]`: Alterna a exibição da data.
- `[quote]`: Alterna a exibição de uma citação.
- `[blink]`: Alterna o piscar dos dois pontos.
- `[mode <nome>]`: Muda para um modo específico (`clock`, `stopwatch`, `timer`, `pomodoro`, `worldclock`).

#### Comandos de Cronômetro, Temporizador e Pomodoro
- `[start]`: Inicia o cronômetro, temporizador ou ciclo Pomodoro.
- `[pause]`: Pausa o cronômetro ou temporizador.
- `[reset]`: Reinicia o cronômetro, temporizador ou Pomodoro para o estado inicial.
- `[lap]`: (Apenas Cronômetro) Grava uma volta.
- `[laps]`: (Apenas Cronômetro) Exibe as voltas gravadas.

#### Comandos de Configuração
- `[set timer <duração>]`: Define a duração do temporizador. Ex: `[set timer 10m]`, `[set timer 1h30m]`, `[set timer 45s]`.
- `[set alarm <HH:MM>]`: Define um alarme. Ex: `[set alarm 07:30]`.
- `[clear alarm]`: Remove o alarme configurado.
- `[set pomodoro work <duração>]`: Define a duração do ciclo de trabalho do Pomodoro. Ex: `[set pomodoro work 25m]`.
- `[set pomodoro break <duração>]`: Define a duração do ciclo de descanso do Pomodoro. Ex: `[set pomodoro break 5m]`.

#### Comandos do Relógio Mundial
- `[add tz <Fuso/Horário>]`: Adiciona um fuso horário à lista. Ex: `[add tz America/New_York]`, `[add tz Europe/London]`.
- `[remove tz <Fuso/Horário>]`: Remove um fuso horário da lista.
- `[list tz]`: Lista todos os fusos horários configurados.

## Arquivo de Configuração

Suas preferências, como cor, modo 12h/24h, alarmes e fusos horários, são salvas automaticamente no arquivo `~/.py_clock_config.json`. Você pode editar este arquivo diretamente ou simplesmente usar os comandos no programa para atualizá-lo.

