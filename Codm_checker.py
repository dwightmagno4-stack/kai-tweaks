import hashlib
import json
import logging
import threading
import random
import os
import re
import sys
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import colorama
import requests
from Crypto.Cipher import AES
from rich import print as rprint
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.box import Box, DOUBLE
from rich.columns import Columns
from rich.align import Align
from rich.layout import Layout
from rich.rule import Rule
import queue
import io
import signal
from collections import deque
colorama.init(autoreset=True)
console = Console()
try:
    import pyfiglet as _pyfiglet
    _HAS_FIG = True
except ImportError:
    _HAS_FIG = False
try:
    from tabulate import tabulate as _tabulate
    _HAS_TAB = True
except ImportError:
    _HAS_TAB = False
import shutil as _shutil_ui
from colorama import Fore as _F, Style as _S

# ─── Premium Dark-Navy Palette (truecolor ANSI) ────────────────────────────────
def _tc(r, g, b):  return f'\x1b[38;2;{r};{g};{b}m'

_RST    = '\x1b[0m'
_BRT    = '\x1b[1m'
_DIM    = '\x1b[2m'

_ACCENT  = _tc(56,  189, 248)   # #38BDF8  sky-blue accent
_BORDER  = _tc(37,  99,  235)   # #2563EB  blue border
_SUCCESS = _tc(16,  185, 129)   # #10B981  emerald
_WARN    = _tc(245, 158, 11)    # #F59E0B  amber
_DANGER  = _tc(239, 68,  68)    # #EF4444  red
_TEXT    = _tc(248, 250, 252)   # #F8FAFC  near-white
_MUTED   = _tc(148, 163, 184)   # #94A3B8  slate
_PURPLE  = _tc(192, 132, 252)   # soft violet

# Backend alias names — never changed below this line
_CY  = _ACCENT
_GN  = _SUCCESS
_RD  = _DANGER
_YL  = _WARN
_MG  = _PURPLE
_WH  = _TEXT
_BLU = _BORDER

# Rich style strings (Rich-based calls only)
P  = 'bold bright_cyan'
S  = 'bold bright_magenta'
OK = 'bold bright_green'
ER = 'bold bright_red'
WN = 'bold yellow'
MU = 'dim'
TX = 'bright_white'
BL = 'cyan'

# ─── Geometry ─────────────────────────────────────────────────────────────────
def _tw():
    return _shutil_ui.get_terminal_size((80, 24)).columns

def _w(n=72):
    return min(_tw() - 4, n)

def _strip_rich(text):
    return re.sub('\\[/?[^\\]]+\\]', '', str(text))

def _ts():
    return datetime.now().strftime('%H:%M:%S')

# ─── Premium panel primitives ─────────────────────────────────────────────────
_TL = '╭'; _TR = '╮'; _BLC = '╰'; _BRC = '╯'
_H  = '─'; _V  = '│'; _ML  = '├'; _MR  = '┤'

def _hr(char='─', color=None, w=None):
    c = color or _BORDER
    n = w or _w()
    print(f'  {c}{char * n}{_RST}')

def _section(title, color=None, icon='◈'):
    c = color or _ACCENT
    w = _w()
    print(f"\n  {_BORDER}{_H * w}{_RST}")
    print(f'  {c}{_BRT}{icon}  {title}{_RST}')
    print(f"  {_BORDER}{_H * w}{_RST}")

def _kv(key, val, kc=None, vc=None, kw=18):
    kc = kc or _MUTED
    vc = vc or _TEXT
    clean_val = _strip_rich(str(val))
    print(f'  {kc}{key:<{kw}}{_RST}  {vc}{clean_val}{_RST}')

def _panel_top(title, bw=None, bc=None):
    bc = bc or _BORDER
    bw = bw or _w(68)
    t  = _strip_rich(title)
    inner = bw - 4
    pad   = max(0, inner - len(t))
    print(f'  {bc}{_TL}{_H * (bw - 2)}{_TR}{_RST}')
    print(f'  {bc}{_V}{_RST} {_BRT}{_ACCENT}{t}{_RST}{_MUTED}{" " * pad}{_RST} {bc}{_V}{_RST}')
    print(f'  {bc}{_ML}{_H * (bw - 2)}{_MR}{_RST}')

def _panel_row(key, val, vc=None, bc=None, kw=20, bw=None):
    bc = bc or _BORDER
    vc = vc or _TEXT
    bw = bw or _w(68)
    k  = f'{_MUTED}{key:<{kw}}{_RST}'
    v  = f'{vc}{_strip_rich(str(val))}{_RST}'
    vis = kw + len(_strip_rich(str(val)))
    pad = max(0, bw - vis - 4)
    print(f'  {bc}{_V}{_RST} {k} {v}{" " * pad} {bc}{_V}{_RST}')

def _panel_sep(bc=None, bw=None):
    bc = bc or _BORDER
    bw = bw or _w(68)
    print(f'  {bc}{_ML}{_H * (bw - 2)}{_MR}{_RST}')

def _panel_bot(bc=None, bw=None):
    bc = bc or _BORDER
    bw = bw or _w(68)
    print(f'  {bc}{_BLC}{_H * (bw - 2)}{_BRC}{_RST}')

# Back-compat wrappers
def _abox_open(title, bc=None, tc=None, w=None):
    _panel_top(title, bw=w or _w(66), bc=bc or _BORDER)

def _abox_row(key, val, vc=None, bc=None, kw=18, w=None):
    _panel_row(key, val, vc=vc or _TEXT, bc=bc or _BORDER, kw=kw, bw=w or _w(66))

def _abox_sep(bc=None, w=None):
    _panel_sep(bc=bc or _BORDER, bw=w or _w(66))

def _abox_close(bc=None, w=None):
    _panel_bot(bc=bc or _BORDER, bw=w or _w(66))
_LOG_ICONS = {
    'INFO':     (_ACCENT,  '·'),
    'SUCCESS':  (_SUCCESS, '✔'),
    'WARNING':  (_WARN,    '⚠'),
    'ERROR':    (_DANGER,  '✖'),
    'DEBUG':    (_MUTED,   '·'),
    'REQUEST':  (_ACCENT,  '→'),
    'RESPONSE': (_ACCENT,  '←'),
    'RETRY':    (_WARN,    '↺'),
    'PROXY':    (_PURPLE,  '◆'),
    'THREAD':   (_PURPLE,  '⧫'),
    'SAVE':     (_SUCCESS, '⬇'),
}

def _log(level: str, msg: str, indent: str='  '):
    col, icon = _LOG_ICONS.get(level, (_MUTED, '·'))
    ts   = _ts()
    clean = _strip_rich(msg)
    ts_s  = f'{_MUTED}[{ts}]{_RST}'
    ic_s  = f'{col}{_BRT}{icon}{_RST}'
    print(f'{indent}{ts_s}  {ic_s}  {_TEXT}{clean}{_RST}')
THREAD_CONFIGS = {'1': {'threads': 1, 'label': '1  thread   — Safe, slower', 'icon': ''}, '2': {'threads': 3, 'label': '3  threads  — Balanced', 'icon': ''}, '3': {'threads': 5, 'label': '5  threads  — Fast', 'icon': ''}, '4': {'threads': 10, 'label': '10 threads  — Very fast (risk)', 'icon': ''}, '5': {'threads': 15, 'label': '15 threads  — Max speed (high risk)', 'icon': ''}}
from rich.box import Box, DOUBLE
CARD = Box('┏━━┓\n┃  ┃\n┣━━┫\n┃  ┃\n┣━━┫\n┣━━┫\n┃  ┃\n┗━━┛\n')
telegram_enabled = False
_telegram_config = None
CODM_REGIONS = {'PH': {'name': 'Philippines', 'code': '63', 'flag': '🇵🇭'}, 'ID': {'name': 'Indonesia', 'code': '62', 'flag': '🇮🇩'}, 'HK': {'name': 'Hong Kong', 'code': '852', 'flag': '🇭🇰'}, 'MY': {'name': 'Malaysia', 'code': '60', 'flag': '🇲🇾'}, 'TW': {'name': 'Taiwan', 'code': '886', 'flag': '🇹🇼'}, 'TH': {'name': 'Thailand', 'code': '66', 'flag': '🇹🇭'}, 'SG': {'name': 'Singapore', 'code': '65', 'flag': '🇸🇬'}, 'VN': {'name': 'Vietnam', 'code': '84', 'flag': '🇻🇳'}, 'MM': {'name': 'Myanmar', 'code': '95', 'flag': '🇲🇲'}, 'KH': {'name': 'Cambodia', 'code': '855', 'flag': '🇰🇭'}, 'LA': {'name': 'Laos', 'code': '856', 'flag': '🇱🇦'}, 'BN': {'name': 'Brunei', 'code': '673', 'flag': '🇧🇳'}}

def sanitize_string(text):
    if not text or text == 'N/A':
        return text
    try:
        return text.encode('ascii', errors='ignore').decode('ascii')
    except:
        return re.sub('[^\\x00-\\x7F]+', '', str(text))

def clean_account_line(line):
    if not line:
        return (None, None)
    line = line.strip().lstrip('\ufeff\ufffe')
    line = ''.join((char for char in line if char.isprintable() or char == ':'))
    if ':' not in line:
        return (None, None)
    try:
        parts = line.split(':', 1)
        if len(parts) != 2:
            return (None, None)
        account = parts[0].strip()
        password = parts[1].strip()
        account = sanitize_string(account)
        password = sanitize_string(password)
        if not account or not password:
            return (None, None)
        return (account, password)
    except:
        return (None, None)

def format_codm_region(region_code):
    if not region_code or region_code == 'N/A':
        return 'N/A'
    region_code = region_code.upper()
    region_info = CODM_REGIONS.get(region_code)
    if region_info:
        return f"{region_info['flag']} {region_info['name']} ({region_code})"
    else:
        return f'{region_code}'

def format_mobile_number(mobile_no, country_code=None):
    if not mobile_no or mobile_no == 'N/A' or (not str(mobile_no).strip()):
        return 'N/A'
    mobile_str = str(mobile_no).strip()
    mobile_str = mobile_str.replace('+', '').replace(' ', '').replace('-', '')
    if country_code:
        country_code = str(country_code).strip()
        if not mobile_str.startswith(country_code):
            if mobile_str.startswith('0'):
                mobile_str = country_code + mobile_str[1:]
            else:
                mobile_str = country_code + mobile_str
    detected_country_code = None
    for code_key, region_info in CODM_REGIONS.items():
        code = region_info['code']
        if mobile_str.startswith(code):
            detected_country_code = code
            break
    if detected_country_code:
        local_number = mobile_str[len(detected_country_code):]
        if len(local_number) >= 4:
            masked = '*' * (len(local_number) - 4) + local_number[-4:]
            return f'+{detected_country_code} {masked}'
        else:
            return f'+{detected_country_code} {local_number}'
    elif len(mobile_str) >= 4:
        masked = '*' * (len(mobile_str) - 4) + mobile_str[-4:]
        return f'+{masked}'
    else:
        return mobile_str

def _sigint_handler(sig, frame):
    print(f'\n  {_YL}⚠  Ctrl+C – exiting immediately…{_RST}')
    os._exit(0)
signal.signal(signal.SIGINT, _sigint_handler)

class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': colorama.Fore.CYAN, 'INFO': colorama.Fore.CYAN, 'WARNING': colorama.Fore.YELLOW, 'ERROR': colorama.Fore.RED, 'CRITICAL': colorama.Fore.RED + colorama.Back.BLACK + colorama.Style.BRIGHT}
    ICONS = {'DEBUG': '⊡', 'INFO': 'ℹ', 'WARNING': '⚠', 'ERROR': '✖', 'CRITICAL': '☠'}
    RESET = colorama.Style.RESET_ALL

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        icon = self.ICONS.get(levelname, '·')
        tag = f'{levelname:<8}'
        if color:
            record.msg = f'{color}{icon} {tag}{self.RESET} {record.msg}'
        return super().format(record)
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
DEFAULT_THREADS = 5
CHECK_OTHER_GAMES: bool = False
GAME_FILE_MAP = {'CODM': 'CODM.txt', 'FREEFIRE': 'FreeFire.txt', 'FREE FIRE': 'FreeFire.txt', 'ROV': 'ROV.txt', 'DELTA FORCE': 'DeltaForce.txt', 'AOV': 'AOV.txt', 'SPEED DRIFTERS': 'SpeedDrifters.txt', 'BLACK CLOVER M': 'BlackCloverM.txt', 'GARENA UNDAWN': 'Undawn.txt', 'FC ONLINE': 'FCOnline.txt', 'FC ONLINE M': 'FCOnlineM.txt', 'MOONLIGHT BLADE': 'MoonlightBlade.txt', 'FAST THRILL': 'FastThrill.txt', 'THE WORLD OF WAR': 'WorldOfWar.txt'}
GAME_DISPLAY_NAMES = [('CODM', 'CODM'), ('FREEFIRE', 'Free Fire'), ('ROV', 'ROV'), ('DELTA FORCE', 'Delta Force'), ('AOV', 'AOV'), ('SPEED DRIFTERS', 'Speed Drifters'), ('BLACK CLOVER M', 'Black Clover M'), ('GARENA UNDAWN', 'Undawn'), ('FC ONLINE', 'FC Online'), ('FC ONLINE M', 'FC Online M'), ('MOONLIGHT BLADE', 'Moonlight Blade'), ('FAST THRILL', 'Fast Thrill'), ('THE WORLD OF WAR', 'World of War')]
OAUTH_MAX_RETRIES = 2
OAUTH_RETRY_DELAY = 0

def _pg_get_stats():
    import psycopg2
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM checked_accounts')
    total = cur.fetchone()[0]
    cur.execute('SELECT MAX(checked_at) FROM checked_accounts')
    latest = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {'total': total or 0, 'latest': latest}

def _pg_save_combos(combos: list):
    import psycopg2
    import psycopg2.extras
    if not combos:
        return
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cur = conn.cursor()
    psycopg2.extras.execute_values(cur, 'INSERT INTO checked_accounts (combo) VALUES %s ON CONFLICT (combo) DO NOTHING', [(c,) for c in combos])
    conn.commit()
    cur.close()
    conn.close()

def _pg_filter_combos(local_combos: list):
    import psycopg2
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cur = conn.cursor()
    BATCH = 2000
    matched_set = set()
    for i in range(0, len(local_combos), BATCH):
        batch = local_combos[i:i + BATCH]
        cur.execute('SELECT combo FROM checked_accounts WHERE combo = ANY(%s)', (batch,))
        for row in cur.fetchall():
            matched_set.add(row[0])
    cur.close()
    conn.close()
    return matched_set

class DatabaseComparison:

    def __init__(self):
        self.stats = None

    def display_database_stats(self):
        indent = '    '
        _err = None
        print(f'\n{indent}{_CY}↺  Connecting to Railway database…{_RST}')
        try:
            self.stats = _pg_get_stats()
        except Exception as e:
            _err = str(e)
            self.stats = None
        if not self.stats:
            _log('WARNING', 'Unable to fetch database statistics', indent)
            if _err:
                _log('ERROR', _err[:70], indent)
            return
        total = self.stats['total']
        latest = self.stats['latest'].strftime('%Y-%m-%d %H:%M') if self.stats['latest'] else 'N/A'
        print()
        _abox_open('DATABASE STATISTICS', bc=_BORDER)
        _abox_row('Total Stored',  f'{total:,}',       vc=_ACCENT)
        _abox_row('Last Entry',    latest,              vc=_WARN)
        _abox_row('Host',          'Railway PostgreSQL',vc=_PURPLE)
        _abox_row('Maintained by', '@maisanyvokei',        vc=_SUCCESS)
        _abox_close(bc=_BORDER)
        print()

    def compare_and_filter_file(self, file_path):
        indent = '    '
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            local_combos = [l.strip() for l in file_content.splitlines() if l.strip() and ':' in l]
            total_local = len(local_combos)
            _abox_open('DATABASE COMPARISON', bc=_BORDER)
            _abox_row('File',             file_path.name,    vc=_ACCENT)
            _abox_row('Combos to compare',f'{total_local:,}',vc=_WARN)
            _abox_close(bc=_BORDER)
            print()
            matched_set = None
            _conn_err = None
            print(f'\n  {_CY}↺  Comparing with Railway database…{_RST}')
            if True:
                try:
                    matched_set = _pg_filter_combos(local_combos)
                except Exception as e:
                    _conn_err = str(e)
                    matched_set = None
            if matched_set is None:
                _abox_open('✖  CONNECTION ERROR', bc=_DANGER)
                _abox_row('Error',  (_conn_err or 'Could not reach Railway database')[:60], vc=_DANGER)
                _abox_row('Action', 'Skipping filter — using full file', vc=_WARN)
                _abox_close(bc=_DANGER)
                print()
                return 'SERVER_ERROR'
            non_matched_combos = [c for c in local_combos if c not in matched_set]
            matches = len(local_combos) - len(non_matched_combos)
            non_matches = len(non_matched_combos)
            skip_pct = round(matches / total_local * 100, 1) if total_local else 0
            _abox_open('✔  COMPARISON RESULTS', bc=_SUCCESS)
            _abox_row('Total Combos',  f'{total_local:,}',                 vc=_ACCENT)
            _abox_row('Already in DB', f'{matches:,}  ({skip_pct}% skip)', vc=_DANGER)
            _abox_row('Fresh / Queue', f'{non_matches:,}',                 vc=_SUCCESS)
            _abox_close(bc=_SUCCESS)
            print()
            if non_matches == 0:
                _log('WARNING', 'All combos already in database — nothing new to check.', indent)
                print()
                return None
            filtered_file_path = file_path.parent / f'{file_path.stem}_filtered{file_path.suffix}'
            with open(filtered_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(non_matched_combos))
            _log('SAVE', f'Filtered file saved: [bright_cyan]{filtered_file_path.name}[/bright_cyan]', indent)
            _log('INFO', f'[dim]{non_matches:,} fresh combos queued for checking.[/dim]', indent)
            print()
            return (filtered_file_path, non_matched_combos)
        except Exception:
            _log('ERROR', 'Error during comparison', indent)
            _log('WARNING', 'Skipping filter — using full file…', indent)
            return 'SERVER_ERROR'

class AccountFileManager:

    def __init__(self, combo_folder='Combo'):
        self.combo_folder = Path(combo_folder)
        self.combo_folder.mkdir(exist_ok=True)
        self._file_lock = threading.Lock()

    def scan_combo_folder(self):
        return list(self.combo_folder.glob('*.txt'))

    def get_file_info(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip() and ':' in line]
                account_count = len(lines)
            file_size = file_path.stat().st_size
            return {'name': file_path.name, 'path': str(file_path), 'size': file_size, 'size_str': self._format_size(file_size), 'account_count': account_count}
        except Exception as e:
            logger.error(f'Error reading file {file_path}')
            return None

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024.0
        return f'{size_bytes:.2f} TB'

    def clean_file_encoding(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            cleaned_lines = []
            invalid_count = 0
            for line in lines:
                account, password = clean_account_line(line)
                if account and password:
                    cleaned_lines.append(f'{account}:{password}\n')
                else:
                    invalid_count += 1
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            return (len(cleaned_lines), invalid_count)
        except Exception as e:
            logger.error(f'Error cleaning file encoding')
            return (0, 0)

    def clean_duplicates(self, file_path, overwrite=True):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip()]
            original_count = len(lines)
            unique_lines = list(dict.fromkeys(lines))
            duplicates_removed = original_count - len(unique_lines)
            if overwrite:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            else:
                new_path = file_path.parent / f'{file_path.stem}_cleaned.txt'
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            return duplicates_removed
        except Exception as e:
            logger.error(f'Error cleaning duplicates')
            return 0

    def remove_line_from_file(self, file_path, line_to_remove):
        try:
            file_path = Path(file_path)
            target = line_to_remove.strip()
            with self._file_lock:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != target:
                            f.write(line)
            return True
        except Exception as e:
            logger.error(f'Error removing line')
            return False
