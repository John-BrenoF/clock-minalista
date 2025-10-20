#!/usr/bin/env python3
import curses
import time
import json
import os
import random
from datetime import datetime, timedelta

try:
    import pytz
except ImportError:
    print("Erro: A biblioteca 'pytz' é necessária. Por favor, instale-a com 'pip install pytz'")
    exit(1)

# --- ASCII DIGITS (refined for better symmetry and style) ---
BLOCK = "█"
SPACE = " "
# --- ASCII DIGITS (Classic digital clock style) ---
DIGITS = {
    "0": ["█████", "█   █", "█   █", "█   █", "█   █", "█   █", "█████"],
    "1": ["  █  ", "  █  ", "  █  ", "  █  ", "  █  ", "  █  ", "  █  "],
    "2": ["█████", "    █", "    █", "█████", "█    ", "█    ", "█████"],
    "3": ["█████", "    █", "    █", "█████", "    █", "    █", "█████"],
    "4": ["█   █", "█   █", "█   █", "█████", "    █", "    █", "    █"],
    "5": ["█████", "█    ", "█    ", "█████", "    █", "    █", "█████"],
    "6": ["█████", "█    ", "█    ", "█████", "█   █", "█   █", "█████"],
    "7": ["█████", "    █", "    █", "    █", "    █", "    █", "    █"],
    "8": ["█████", "█   █", "█   █", "█████", "█   █", "█   █", "█████"],
    "9": ["█████", "█   █", "█   █", "█████", "    █", "    █", "█████"],
    ":": ["     ", "  █  ", "  █  ", "     ", "  █  ", "  █  ", "     "],
    "A": [" ███ ", "█   █", "█   █", "█████", "█   █", "█   █", "█   █"],
    "M": ["█   █", "██ ██", "█ █ █", "█   █", "█   █", "█   █", "█   █"],
    "P": ["█████", "█   █", "█   █", "█████", "█    ", "█    ", "█    "],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "]
}
COLORS = ["cyan", "green", "yellow", "magenta", "blue", "red", "white", "random"]
COLOR_MAP = {
    "black": curses.COLOR_BLACK, "red": curses.COLOR_RED, "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW, "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA, "cyan": curses.COLOR_CYAN, "white": curses.COLOR_WHITE
}
QUOTES = [
    "Keep it simple.", "Focus on progress.", "Done is better than perfect.",
    "Stay curious.", "Time waits for no one.", "The best time is now.",
    "Persistence pays off.", "Learn from yesterday.", "Dream big.", "Act small."
]
CONFIG_FILE = os.path.expanduser("~/.py_clock_config.json")

def render_time_string(timestr, color_pair, random_mode=False):
    rows = [""] * 7
    for char in timestr:
        glyph = DIGITS.get(char, DIGITS[" "])
        for i, line in enumerate(glyph):
            rows[i] += line + "  "
    if random_mode:
        return [(random.choice(list(pair_map.values())), line) for line in rows]
    else:
        return [(color_pair, line) for line in rows]

def parse_time_str(s):
    if s.endswith("h"): return int(s[:-1]) * 3600
    if s.endswith("m"): return int(s[:-1]) * 60
    if s.endswith("s"): return int(s[:-1])
    return int(s)

def parse_alarm_time(s):
    try:
        h, m = map(int, s.split(':'))
        now = datetime.now()
        alarm = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if alarm < now:
            alarm += timedelta(days=1)
        return alarm
    except:
        return None

def load_config():
    """Carrega a configuração do arquivo JSON."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Converte strings de alarme e fusos horários de volta para os tipos corretos
            if config.get("alarm_time"):
                config["alarm_time"] = datetime.fromisoformat(config["alarm_time"])
            return config
    except (json.JSONDecodeError, IOError):
        return {}

def save_config(state):
    """Salva as configurações persistentes em um arquivo JSON."""
    config_to_save = {
        key: state[key] for key in [
            "show_seconds", "h12", "color", "show_date", "show_quote", "blink_colon", "minimal_mode",
            "pomodoro_work", "pomodoro_break", "world_clocks"
        ] if key in state
    }
    if state.get("alarm_time"):
        config_to_save["alarm_time"] = state["alarm_time"].isoformat()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_to_save, f, indent=2)

def main(stdscr):
    curses.curs_set(0)  # Hide cursor for better style
    curses.start_color()
    curses.use_default_colors()
    global pair_map
    pair_map = {}
    for idx, name in enumerate(COLOR_MAP.keys(), start=1):
        curses.init_pair(idx, COLOR_MAP[name], -1)
        pair_map[name] = curses.color_pair(idx)

    saved_config = load_config()
    state = {
        "mode": "clock", "show_seconds": True, "h12": False, "color": "cyan", "show_date": False,
        "stopwatch_start": None, "stopwatch_elapsed": 0, "laps": [],
        "timer_end": None, "timer_duration": 0, "timer_paused": False, "timer_remaining": 0,
        "alarm_time": None, "alarm_triggered": False,
        "pomodoro_phase": "work", "pomodoro_end": None, "pomodoro_cycles": 0, "pomodoro_work": 25 * 60, "pomodoro_break": 5 * 60,
        "show_quote": False, "blink_colon": True,
        "world_clocks": [], "minimal_mode": False
    }
    state.update(saved_config)

    input_buffer = ""
    msg = ""
    blink = False
    last_beep = None
    quote_index = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        now = datetime.now()

        # --- Handle blinking and beeping ---
        blink = (now.second % 2 == 0)
        finished_blink = False
        if state["mode"] == "timer" and state["timer_end"] and (state["timer_end"] - now).total_seconds() <= 0:
            if not last_beep or (now - last_beep).total_seconds() > 1:
                curses.beep()
                last_beep = now
            finished_blink = True
        if state["alarm_time"] and now >= state["alarm_time"] and not state["alarm_triggered"]:
            curses.beep()
            msg = "Alarm triggered!"
            state["alarm_triggered"] = True

        # --- Build numeric time string ---
        colon = ":" if (state["blink_colon"] or not blink) else " "
        numeric_timestr = ""
        extra_text = ""
        if state["mode"] == "clock":
            hour = now.hour
            if state["h12"]:
                ampm = "AM" if hour < 12 else "PM"
                hour = hour % 12 or 12
                extra_text = ampm
            numeric_timestr = f"{hour:02d}{colon}{now.minute:02d}"
            if state["show_seconds"]:
                numeric_timestr += f"{colon}{now.second:02d}"
        elif state["mode"] == "stopwatch":
            elapsed = state["stopwatch_elapsed"]
            if state["stopwatch_start"]:
                elapsed += (now - state["stopwatch_start"]).total_seconds()
            m, s = divmod(int(elapsed), 60)
            h2, m = divmod(m, 60)
            numeric_timestr = f"{h2:02d}{colon}{m:02d}{colon}{s:02d}"
        elif state["mode"] == "timer":
            if state["timer_end"] and not state["timer_paused"]:
                remaining = int((state["timer_end"] - now).total_seconds())
                if remaining <= 0:
                    remaining = 0
                    finished_blink = True
            elif state["timer_paused"]:
                remaining = state["timer_remaining"]
            else:
                remaining = state["timer_duration"]
            m, s = divmod(remaining, 60)
            h2, m = divmod(m, 60)
            numeric_timestr = f"{h2:02d}{colon}{m:02d}{colon}{s:02d}"
        elif state["mode"] == "pomodoro":
            if state["pomodoro_end"]:
                remaining = int((state["pomodoro_end"] - now).total_seconds())
                if remaining <= 0:
                    remaining = 0
                    if state["pomodoro_phase"] == "work":
                        state["pomodoro_phase"] = "break"
                        state["pomodoro_end"] = now + timedelta(seconds=state["pomodoro_break"])
                        state["pomodoro_cycles"] += 1
                        msg = "Break time!"
                    else:
                        state["pomodoro_phase"] = "work"
                        state["pomodoro_end"] = now + timedelta(seconds=state["pomodoro_work"])
                        msg = "Work time!"
                    curses.beep()
                    # Recalculate for immediate update
                    remaining = int((state["pomodoro_end"] - now).total_seconds())
            else:
                remaining = state["pomodoro_work"] if state["pomodoro_phase"] == "work" else state["pomodoro_break"]
            m, s = divmod(remaining, 60)
            h2, m = divmod(m, 60)
            numeric_timestr = f"{h2:02d}{colon}{m:02d}{colon}{s:02d}"
            extra_text = f"({state['pomodoro_phase'].title()}, cycle {state['pomodoro_cycles']})"

        # --- Render World Clock (se aplicável) ---
        if state["mode"] == "worldclock":
            stdscr.addstr(2, max((w - 20) // 2, 0), "--- World Clocks ---", curses.A_BOLD)
            if not state["world_clocks"]:
                stdscr.addstr(4, max((w - 40) // 2, 0), "Nenhum fuso horário adicionado. Use [add tz Zone/Name]")
            else:
                for i, tz_name in enumerate(state["world_clocks"]):
                    try:
                        tz = pytz.timezone(tz_name)
                        tz_time = now.astimezone(tz)
                        time_str = tz_time.strftime('%H:%M:%S')
                        date_str = tz_time.strftime('%Y-%m-%d')
                        display_str = f"{tz_name:<20} {time_str} ({date_str})"
                        stdscr.addstr(4 + i, max((w - len(display_str)) // 2, 0), display_str)
                    except pytz.UnknownTimeZoneError:
                        stdscr.addstr(4 + i, max((w - 30) // 2, 0), f"{tz_name}: Fuso horário inválido", curses.A_REVERSE)
            # Pula a renderização do relógio grande

        # --- Calculate layout ---
        num_extra = 0
        if extra_text: num_extra += 1
        if state["show_date"]: num_extra += 1
        if state["show_quote"]: num_extra += 1
        total_height = 7 + 2 * num_extra  # 7 for time + 1 line + 1 skip per extra
        top = max((h - total_height) // 2, 0)

        # --- Render big time (exceto para worldclock) ---
        if state["mode"] != "worldclock":
            random_mode = state["color"] == "random"
            lines = render_time_string(numeric_timestr, pair_map.get(state["color"], pair_map["white"]), random_mode)
            time_width = len(numeric_timestr) * 7
            x = max((w - time_width) // 2, 0)
            for i, (c, line) in enumerate(lines):
                attr = c
                if (finished_blink or (state["mode"] in ["timer", "pomodoro"] and remaining <= 0)) and (int(now.timestamp() * 10) % 2 == 0):
                    attr |= curses.A_REVERSE
                stdscr.addstr(top + i, x, line, attr)

        # --- Render extra elements dynamically ---
        y = top + 7
        if extra_text:
            stdscr.addstr(y + 1, max((w - len(extra_text)) // 2, 0), extra_text, curses.A_DIM)
            y += 2
        if state["show_date"]:
            date_str = now.strftime("%A, %d %B %Y")
            stdscr.addstr(y + 1, max((w - len(date_str)) // 2, 0), date_str)
            y += 2
        if state["show_quote"]:
            quote_index = now.second % len(QUOTES)
            quote = QUOTES[quote_index]
            stdscr.addstr(y + 1, max((w - len(quote)) // 2, 0), quote, curses.A_DIM)
            y += 2

        # --- Display laps if any (left-aligned below display) ---
        if state["mode"] == "stopwatch" and state["laps"]:
            lap_str = "Laps: " + ", ".join(f"{i+1}: {int(t)//60:02d}:{int(t)%60:02d}" for i, t in enumerate(state["laps"]))
            display_laps = lap_str[:w - 2]
            stdscr.addstr(y + 1, 1, display_laps, curses.A_DIM)

        # --- Status and input at bottom (unless in minimal mode) ---
        if not state["minimal_mode"]:
            help_str = "[c]color [s]secs [h]12h [d]date [b]blink [q]quote [o]zen [w]stopwatch [t]timer [p]pomodoro [a]clock [z]world [?]help [q]quit"
            stdscr.addstr(h - 5, 1, help_str[:w - 2], curses.A_DIM)
            if msg:
                stdscr.addstr(h - 4, 1, msg[:w - 2], curses.A_BOLD)
            stdscr.addstr(h - 3, 1, f"Mode: {state['mode']} | Color: {state['color']}", curses.A_DIM)
            if state["alarm_time"]:
                stdscr.addstr(h - 2, 1, f"Alarm set for {state['alarm_time'].strftime('%H:%M')}", curses.A_DIM)
            stdscr.addstr(h - 1, 1, "> " + input_buffer)
            stdscr.clrtoeol()

        stdscr.refresh()

        # --- Non-blocking input ---
        stdscr.nodelay(True)
        try:
            ch = stdscr.getch()
        except:
            ch = -1
        stdscr.nodelay(False)  # Reset for next getch

        if ch == -1:
            time.sleep(0.1)
            continue

        # --- Input handling (cleaned up) ---
        if input_buffer.startswith("["):
            # Command mode: handle buffer
            if ch in (curses.KEY_BACKSPACE, 127, 8):
                input_buffer = input_buffer[:-1]
            elif ch in (10, 13):  # Enter
                if input_buffer.endswith("]"):
                    cmd = input_buffer[1:-1].strip()
                    msg = handle_cmd(cmd, state)
                    save_config(state) # Salva a configuração após um comando
                    if msg == "quit":
                        break
                else:
                    msg = "Invalid: use [cmd]"
                input_buffer = ""
            elif 32 <= ch < 127:
                input_buffer += chr(ch)
        else:
            # Shortcut mode
            if ch == ord('q'):
                break
            elif ch == ord('s'):
                state["show_seconds"] = not state["show_seconds"]
                msg = "Toggled seconds"
            elif ch == ord('h'):
                state["h12"] = not state["h12"]
                msg = "Toggled 12h"
            elif ch == ord('c'):
                idx = (COLORS.index(state["color"]) + 1) % len(COLORS)
                state["color"] = COLORS[idx]
                msg = f"Color: {state['color']}"
            elif ch == ord('d'):
                state["show_date"] = not state["show_date"]
                msg = "Toggled date"
            elif ch == ord('b'):
                state["blink_colon"] = not state["blink_colon"]
                msg = "Toggled blinking colon"
            elif ch == ord('w'):
                state["mode"] = "stopwatch"
                msg = "Stopwatch mode"
            elif ch == ord('t'):
                state["mode"] = "timer"
                msg = "Timer mode"
            elif ch == ord('p'):
                state["mode"] = "pomodoro"
                msg = "Pomodoro mode"
            elif ch == ord('a'):
                state["mode"] = "clock"
                msg = "Clock mode (with alarm support)"
            elif ch == ord('z'):
                state["mode"] = "worldclock"
                msg = "World Clock mode"
            elif ch == ord('o'):
                state["minimal_mode"] = not state["minimal_mode"]
                msg = "Toggled zen mode"
            elif ch == ord('?'):
                msg = "Commands: [mode ...], [start], [pause], [reset], [set timer 5m], [set alarm 14:30], [add tz Zone/Name], [remove tz Zone/Name], [list tz], [help], [quit]"
            elif ch in (curses.KEY_BACKSPACE, 127, 8) and input_buffer:
                input_buffer = input_buffer[:-1]
            elif ch in (10, 13):
                input_buffer = ""  # Clear on enter without [
            elif 32 <= ch < 127:
                input_buffer += chr(ch)
                if input_buffer == "[":
                    pass  # Start command mode
                else:
                    input_buffer = ""  # Discard non-command input

def handle_cmd(cmd, state):
    if not cmd:
        return ""
    parts = cmd.split()
    if parts[0] in ("quit", "exit"):
        return "quit"
    if parts[0] == "date":
        state["show_date"] = not state["show_date"]
        return "Toggled date"
    if parts[0] == "quote":
        state["show_quote"] = not state["show_quote"]
        return "Toggled quote"
    if parts[0] == "blink":
        state["blink_colon"] = not state["blink_colon"]
        return "Toggled blinking colon"
    if parts[0] == "mode" and len(parts) > 1:
        if parts[1] in ("clock", "stopwatch", "timer", "pomodoro", "worldclock"):
            state["mode"] = parts[1]
            return f"Mode: {parts[1]}"
    if parts[0] == "start":
        if state["mode"] == "stopwatch":
            state["stopwatch_start"] = datetime.now()
        elif state["mode"] == "timer" and state["timer_duration"] > 0:
            if state["timer_paused"]:
                state["timer_end"] = datetime.now() + timedelta(seconds=state["timer_remaining"])
                state["timer_paused"] = False
            else:
                state["timer_end"] = datetime.now() + timedelta(seconds=state["timer_duration"])
        elif state["mode"] == "pomodoro":
            duration = state["pomodoro_work"] if state["pomodoro_phase"] == "work" else state["pomodoro_break"]
            state["pomodoro_end"] = datetime.now() + timedelta(seconds=duration)
        return "Started"
    if parts[0] == "pause":
        if state["mode"] == "stopwatch" and state["stopwatch_start"]:
            state["stopwatch_elapsed"] += (datetime.now() - state["stopwatch_start"]).total_seconds()
            state["stopwatch_start"] = None
            return "Paused stopwatch"
        elif state["mode"] == "timer" and state["timer_end"]:
            state["timer_remaining"] = int((state["timer_end"] - datetime.now()).total_seconds())
            state["timer_end"] = None
            state["timer_paused"] = True
            return "Paused timer"
    if parts[0] == "reset":
        if state["mode"] == "stopwatch":
            state.update(stopwatch_start=None, stopwatch_elapsed=0, laps=[])
            return "Stopwatch reset"
        if state["mode"] == "timer":
            state.update(timer_end=None, timer_duration=0, timer_remaining=0, timer_paused=False)
            return "Timer reset"
        if state["mode"] == "pomodoro":
            state.update(pomodoro_end=None, pomodoro_phase="work", pomodoro_cycles=0)
            return "Pomodoro reset"
    if parts[0] == "lap" and state["mode"] == "stopwatch":
        elapsed = state["stopwatch_elapsed"]
        if state["stopwatch_start"]:
            elapsed += (datetime.now() - state["stopwatch_start"]).total_seconds()
        state["laps"].append(elapsed)
        return f"Lap {len(state['laps'])} saved"
    if parts[0] == "laps" and state["mode"] == "stopwatch":
        if not state["laps"]:
            return "No laps"
        return "Laps: " + ", ".join(f"{i+1}: {int(t)//60:02d}:{int(t)%60:02d}" for i, t in enumerate(state["laps"]))
    if parts[0] == "set" and len(parts) > 2:
        if parts[1] == "timer":
            try:
                secs = parse_time_str(parts[2])
                state["timer_duration"] = secs
                return f"Timer set to {secs}s"
            except:
                return "Invalid timer value"
        if parts[1] == "alarm":
            alarm = parse_alarm_time(parts[2])
            if alarm:
                state["alarm_time"] = alarm
                state["alarm_triggered"] = False
                return f"Alarm set for {parts[2]}"
            else:
                return "Invalid alarm time (HH:MM)"
        if parts[1] == "pomodoro" and len(parts) > 3:
            if parts[2] == "work":
                try:
                    secs = parse_time_str(parts[3])
                    state["pomodoro_work"] = secs
                    return f"Pomodoro work set to {secs}s"
                except:
                    return "Invalid value"
            if parts[2] == "break":
                try:
                    secs = parse_time_str(parts[3])
                    state["pomodoro_break"] = secs
                    return f"Pomodoro break set to {secs}s"
                except:
                    return "Invalid value"
    if parts[0] == "clear" and len(parts) > 1:
        if parts[1] == "alarm":
            state["alarm_time"] = None
            state["alarm_triggered"] = False
            return "Alarm cleared"
    if parts[0] == "add" and len(parts) > 2 and parts[1] == "tz":
        tz_name = parts[2]
        try:
            pytz.timezone(tz_name) # Valida o fuso horário
            if tz_name not in state["world_clocks"]:
                state["world_clocks"].append(tz_name)
                return f"Added timezone: {tz_name}"
            else:
                return f"{tz_name} já está na lista."
        except pytz.UnknownTimeZoneError:
            return f"Fuso horário desconhecido: {tz_name}"
    if parts[0] == "remove" and len(parts) > 2 and parts[1] == "tz":
        tz_name = parts[2]
        if tz_name in state["world_clocks"]:
            state["world_clocks"].remove(tz_name)
            return f"Removed timezone: {tz_name}"
        else:
            return f"Fuso horário não encontrado: {tz_name}"
    if parts[0] == "list" and len(parts) > 1 and parts[1] == "tz":
        return "Fusos horários: " + ", ".join(state["world_clocks"]) if state["world_clocks"] else "Nenhum fuso horário configurado."
    if parts[0] == "randomquote":
        return random.choice(QUOTES)
    if parts[0] == "help":
        return "Commands: [mode ...], [start], [pause], [reset], [set timer 5m], [set alarm 14:30], [add tz Zone/Name], [remove tz Zone/Name], [list tz], [help], [quit]"
    return f"Unknown command: {cmd}"

if __name__ == "__main__":
    curses.wrapper(main)
