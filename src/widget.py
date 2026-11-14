"""Bangla Net Speed Meter v1.3.0
Developed by Iqbal Mahmud: https://iqbalmahmud.com
"""
import ctypes, json, math, os, re, sys, threading, time, webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser
import psutil
from PIL import Image, ImageDraw
import pystray

APP='BanglaNetSpeed'
APP_VERSION='1.3.0'
WEBSITE='https://iqbalmahmud.com'
CFG_DIR=Path(os.getenv('APPDATA',Path.home()))/APP
CFG_FILE=CFG_DIR/'settings.json'
DEFAULT={
 'x':None,'y':None,'width':310,'height':42,'opacity':0.96,
 'unit':'auto_bytes','interface':'All','interval_ms':500,
 'font_color':'#F8FAFC','font_weight':'semibold','font_size':9,
 'background':'#172033','border':'#334155','autostart':True,'first_run_complete':False,
 'topmost_refresh_ms':1500,'stats_mode':'both','speed_layout':'horizontal','language':'en'
}
STATS_W=90  # extra widget width used by the CPU/RAM column
SPEED_LAYOUT_W=110  # width difference between horizontal and stacked speed layouts
STATS_MODES=('both','ram','cpu','off')
SPEED_LAYOUTS=('horizontal','stacked_up_down','stacked_down_up')
LANGUAGES=('en','bn')
UNITS=('auto_bytes','auto_bits','MBps','Mbps','KBps','Kbps')
WEIGHTS=('normal','semibold','bold')
HEX_COLOR=re.compile(r'#[0-9A-Fa-f]{6}')
MAX_CFG_BYTES=64*1024
ERROR_ALREADY_EXISTS=183
_MUTEX=None

def to_bn_digits(s):
    return str(s).translate(str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯'))

I18N = {
    'en': {
        'speed_unit': 'Speed unit',
        'speed_layout': 'Speed layout',
        'language': 'Language / ভাষা',
        'network_interface': 'Network interface',
        'all_interfaces': 'All interfaces',
        'font_color': 'Font color',
        'font_weight': 'Font weight',
        'font_size': 'Font size',
        'cpu_ram_usage': 'CPU / RAM usage',
        'widget_size': 'Widget size',
        'background_color': 'Background color…',
        'reset_position': 'Reset position to taskbar',
        'autostart': 'Start with Windows',
        'open_website': 'Open iqbalmahmud.com',
        'exit': 'Exit',
        'bring_to_front': 'Bring to front',
        'auto_bytes': 'Auto bytes',
        'auto_bits': 'Auto bits',
        'layout_horizontal': 'Horizontal (side by side)',
        'layout_up_down': 'Stacked: Upload top (↑ / ↓)',
        'layout_down_up': 'Stacked: Download top (↓ / ↑)',
        'stats_both': 'CPU + RAM',
        'stats_ram': 'RAM only',
        'stats_cpu': 'CPU only',
        'stats_off': 'Hidden',
        'color_white': 'White',
        'color_black': 'Black',
        'color_blue': 'Blue',
        'color_green': 'Green',
        'color_purple': 'Purple',
        'color_orange': 'Orange',
        'color_custom': 'Custom…',
        'weight_normal': 'Normal',
        'weight_semibold': 'Semi-bold',
        'weight_bold': 'Bold',
        'size_wider': 'Wider',
        'size_narrower': 'Narrower',
        'size_taller': 'Taller',
        'size_shorter': 'Shorter',
        'size_reset': 'Reset size',
        'tip_upload': 'Your upload speed is {val}',
        'tip_download': 'Your download speed is {val}',
        'tip_ram': 'RAM usage is {val}',
        'tip_cpu': 'CPU usage is {val}',
        'dlg_font_color': 'Speed font color',
        'dlg_bg': 'Widget background',
        'dlg_startup': 'Startup setting',
    },
    'bn': {
        'speed_unit': 'গতির একক',
        'speed_layout': 'গতির বিন্যাস',
        'language': 'ভাষা (Language)',
        'network_interface': 'নেটওয়ার্ক ইন্টারফেস',
        'all_interfaces': 'সকল ইন্টারফেস',
        'font_color': 'ফন্টের রঙ',
        'font_weight': 'ফন্ট পুরুত্ব',
        'font_size': 'ফন্টের আকার',
        'cpu_ram_usage': 'সিপিইউ / র‍্যাম ব্যবহার',
        'widget_size': 'উইজেটের আকার',
        'background_color': 'ব্যাকগ্রাউন্ড রঙ…',
        'reset_position': 'টাস্কবারে অবস্থান রিসেট',
        'autostart': 'উইন্ডোজের সাথে চালু করুন',
        'open_website': 'ইকবাল মাহমুদের ওয়েবসাইট',
        'exit': 'প্রস্থান',
        'bring_to_front': 'সামনে আনুন',
        'auto_bytes': 'স্বয়ংক্রিয় বাইট (Auto bytes)',
        'auto_bits': 'স্বয়ংক্রিয় বিট (Auto bits)',
        'layout_horizontal': 'অনুভূমিক (পাশাপাশি)',
        'layout_up_down': 'স্তূপীকৃত: আপলোড উপরে (↑ / ↓)',
        'layout_down_up': 'স্তূপীকৃত: ডাউনলোড উপরে (↓ / ↑)',
        'stats_both': 'সিপিইউ + র‍্যাম',
        'stats_ram': 'কেবল র‍্যাম',
        'stats_cpu': 'কেবল সিপিইউ',
        'stats_off': 'লুকানো',
        'color_white': 'সাদা',
        'color_black': 'কালো',
        'color_blue': 'নীল',
        'color_green': 'সবুজ',
        'color_purple': 'বেগুনি',
        'color_orange': 'কমলা',
        'color_custom': 'কাস্টম…',
        'weight_normal': 'সাধারণ (Normal)',
        'weight_semibold': 'সেমি-বোল্ড (Semi-bold)',
        'weight_bold': 'বোল্ড (Bold)',
        'size_wider': 'প্রস্থ বাড়ান',
        'size_narrower': 'প্রস্থ কমান',
        'size_taller': 'উচ্চতা বাড়ান',
        'size_shorter': 'উচ্চতা কমান',
        'size_reset': 'আকার রিসেট',
        'tip_upload': 'আপনার আপলোড গতি হলো {val}',
        'tip_download': 'আপনার ডাউনলোড গতি হলো {val}',
        'tip_ram': 'র‍্যাম ব্যবহার হলো {val}',
        'tip_cpu': 'সিপিইউ ব্যবহার হলো {val}',
        'dlg_font_color': 'গতি ফন্টের রঙ',
        'dlg_bg': 'উইজেট ব্যাকগ্রাউন্ড',
        'dlg_startup': 'স্টার্টআপ সেটিংস',
    }
}

def tr(key, lang='en', **kwargs):
    text = I18N.get(lang, I18N['en']).get(key, I18N['en'].get(key, key))
    if kwargs:
        if lang == 'bn' and 'val' in kwargs:
            kwargs['val'] = to_bn_digits(kwargs['val'])
        text = text.format(**kwargs)
    return text

class WidgetToolTip:
    def __init__(self, widgets, text_fn, get_theme_fn):
        self.widgets = widgets if isinstance(widgets, (list, tuple)) else [widgets]
        self.text_fn = text_fn
        self.get_theme_fn = get_theme_fn
        self.tw = None
        self.lbl = None
        self.after_id = None
        for w in self.widgets:
            w.bind('<Enter>', self.on_enter, add='+')
            w.bind('<Leave>', self.on_leave, add='+')
            w.bind('<Motion>', self.on_motion, add='+')
            w.bind('<ButtonPress>', self.on_leave, add='+')
    def on_enter(self, e):
        self.cancel()
        self.after_id = self.widgets[0].after(200, lambda: self.show(e.x_root, e.y_root))
    def on_motion(self, e):
        if not self.tw and self.after_id:
            self.cancel()
            self.after_id = self.widgets[0].after(200, lambda: self.show(e.x_root, e.y_root))
    def on_leave(self, e=None):
        self.cancel()
        self.hide()
    def cancel(self):
        if self.after_id:
            try: self.widgets[0].after_cancel(self.after_id)
            except Exception: pass
            self.after_id = None
    def raise_up(self):
        if self.tw:
            self.tw.lift()
            if os.name=='nt':
                try:
                    HWND_TOPMOST=wintypes.HWND(-1);flags=0x0001|0x0002|0x0010|0x0040
                    _U32.SetWindowPos(self.tw.winfo_id(),HWND_TOPMOST,0,0,0,0,flags)
                except Exception:pass
    def show(self,x,y):
        self.cancel()
        if self.tw:return
        text=self.text_fn()
        if not text:return
        w0=self.widgets[0];root_win=w0.winfo_toplevel()
        self.tw=tw=tk.Toplevel(root_win)
        tw.wm_overrideredirect(True)
        tw.wm_attributes('-topmost',True)
        theme=self.get_theme_fn()
        bg=theme.get('bg','#172033');fg=theme.get('fg','#F8FAFC');bd=theme.get('border','#334155')
        f=tk.Frame(tw,bg=bg,highlightthickness=1,highlightbackground=bd)
        f.pack(fill='both',expand=True)
        self.lbl=tk.Label(f,text=text,font=('Segoe UI',9),bg=bg,fg=fg,padx=8,pady=4)
        self.lbl.pack()
        tw.update_idletasks()
        tip_w=tw.winfo_reqwidth();tip_h=tw.winfo_reqheight()
        sw=root_win.winfo_screenwidth();sh=root_win.winfo_screenheight()
        rw_y=root_win.winfo_rooty();rw_h=root_win.winfo_height()
        if rw_y+rw_h+35>=sh or y+45>=sh:ty=max(10,rw_y-tip_h-6)
        else:ty=min(sh-tip_h-10,rw_y+rw_h+6)
        tx=max(6,min(sw-tip_w-6,x-20))
        tw.wm_geometry(f"+{tx}+{ty}")
        self.raise_up()
    def update_text(self):
        if self.tw and self.lbl:
            try: self.lbl.configure(text=self.text_fn())
            except Exception: pass
    def hide(self):
        tw, self.tw, self.lbl = self.tw, None, None
        if tw:
            try: tw.destroy()
            except Exception: pass

if os.name=='nt':
    from ctypes import wintypes
    # Explicit prototypes: without them ctypes truncates 64-bit handles and
    # GetLastError() can be clobbered by the interpreter between calls.
    _K32=ctypes.WinDLL('kernel32',use_last_error=True)
    _K32.CreateMutexW.restype=wintypes.HANDLE;_K32.CreateMutexW.argtypes=(wintypes.LPVOID,wintypes.BOOL,wintypes.LPCWSTR)
    _U32=ctypes.WinDLL('user32',use_last_error=True)
    _U32.FindWindowW.restype=wintypes.HWND;_U32.FindWindowW.argtypes=(wintypes.LPCWSTR,wintypes.LPCWSTR)
    _U32.GetWindowRect.restype=wintypes.BOOL;_U32.GetWindowRect.argtypes=(wintypes.HWND,ctypes.POINTER(wintypes.RECT))
    _U32.SetWindowPos.restype=wintypes.BOOL;_U32.SetWindowPos.argtypes=(wintypes.HWND,wintypes.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.UINT)

def single_instance():
    global _MUTEX
    if os.name!='nt': return True
    _MUTEX=_K32.CreateMutexW(None,False,'Local\\IqbalMahmud.BanglaNetSpeed.v1')
    return bool(_MUTEX) and ctypes.get_last_error()!=ERROR_ALREADY_EXISTS

def _clamp_int(v,default,lo,hi):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):return default
    return min(hi,max(lo,int(v)))
def sanitize_cfg(raw):
    """Treat settings.json as untrusted: keep only known keys with valid types and ranges."""
    c=DEFAULT.copy()
    if not isinstance(raw,dict):return c
    for k in ('x','y'):c[k]=_clamp_int(raw.get(k),None,-32768,32767)
    c['width']=_clamp_int(raw.get('width'),DEFAULT['width'],100,2000)
    c['height']=_clamp_int(raw.get('height'),DEFAULT['height'],30,400)
    c['interval_ms']=_clamp_int(raw.get('interval_ms'),DEFAULT['interval_ms'],200,10000)
    c['topmost_refresh_ms']=_clamp_int(raw.get('topmost_refresh_ms'),DEFAULT['topmost_refresh_ms'],500,60000)
    c['font_size']=_clamp_int(raw.get('font_size'),DEFAULT['font_size'],6,32)
    op=raw.get('opacity')
    # Opacity is floored at 0.2 so a bad value can never make the widget invisible.
    if not isinstance(op,bool) and isinstance(op,(int,float)) and math.isfinite(op):c['opacity']=min(1.0,max(0.2,float(op)))
    if raw.get('unit') in UNITS:c['unit']=raw['unit']
    if raw.get('speed_layout') in SPEED_LAYOUTS:c['speed_layout']=raw['speed_layout']
    if raw.get('language') in LANGUAGES:c['language']=raw['language']
    if raw.get('font_weight') in WEIGHTS:c['font_weight']=raw['font_weight']
    for k in ('font_color','background','border'):
        if isinstance(raw.get(k),str) and HEX_COLOR.fullmatch(raw[k]):c[k]=raw[k]
    if isinstance(raw.get('interface'),str) and 0<len(raw['interface'])<=256:c['interface']=raw['interface']
    if raw.get('stats_mode') in STATS_MODES:c['stats_mode']=raw['stats_mode']
    elif isinstance(raw.get('show_stats'),bool):c['stats_mode']='both' if raw['show_stats'] else 'off'  # v1.1.0-1.1.2 setting
    for k in ('autostart','first_run_complete'):
        if isinstance(raw.get(k),bool):c[k]=raw[k]
    return c

def load_cfg():
    try:
        if CFG_FILE.stat().st_size>MAX_CFG_BYTES:return DEFAULT.copy()
        raw=json.loads(CFG_FILE.read_text(encoding='utf-8'));c=sanitize_cfg(raw)
        # Settings saved before the CPU/RAM column existed: make room for it.
        if isinstance(raw,dict) and 'stats_mode' not in raw and 'show_stats' not in raw and c['stats_mode']!='off':c['width']=min(2000,c['width']+STATS_W)
        # v1.1.0-1.1.2 saved a narrower default (290) that is too tight now that speeds are centred.
        elif isinstance(raw,dict) and raw.get('show_stats') is True and 'stats_mode' not in raw:c['width']=max(c['width'],DEFAULT['width'])
        return c
    except (OSError,ValueError,RecursionError):return DEFAULT.copy()
def save_cfg(c):
    """Write atomically so a crash or power loss never leaves a truncated settings file."""
    try:
        CFG_DIR.mkdir(parents=True,exist_ok=True);tmp=CFG_FILE.with_name(CFG_FILE.name+'.tmp')
        tmp.write_text(json.dumps(c,indent=2),encoding='utf-8');os.replace(tmp,CFG_FILE)
        return True
    except OSError:return False
def counter(interface):
    if interface=='All':return psutil.net_io_counters()
    return psutil.net_io_counters(pernic=True).get(interface,psutil.net_io_counters())
def fmt_speed(n,mode):
    if mode=='MBps':return f'{n/1e6:.2f} MB/s'
    if mode=='Mbps':return f'{n*8/1e6:.2f} Mbps'
    if mode=='KBps':return f'{n/1e3:.1f} KB/s'
    if mode=='Kbps':return f'{n*8/1e3:.1f} Kbps'
    if mode=='auto_bits':
        n*=8
        for f,u in ((1e9,'Gbps'),(1e6,'Mbps'),(1e3,'Kbps')):
            if n>=f:return f'{n/f:.2f} {u}'
        return f'{n:.0f} bps'
    for f,u in ((1e9,'GB/s'),(1e6,'MB/s'),(1e3,'KB/s')):
        if n>=f:return f'{n/f:.2f} {u}'
    return f'{n:.0f} B/s'
def startup_command():
    """Build a quoted per-user startup command for source or frozen EXE mode."""
    if getattr(sys,'frozen',False):return f'"{Path(sys.executable).resolve()}"'
    executable=Path(sys.executable).resolve()
    # Prefer pythonw.exe to avoid a console at sign-in when launched from python.exe.
    if executable.name.lower()=='python.exe':
        candidate=executable.with_name('pythonw.exe')
        if candidate.exists():executable=candidate
    return f'"{executable}" "{Path(__file__).resolve()}"'

def set_autostart(enabled):
    """Set current-user startup only. Returns (success, message)."""
    if os.name!='nt':return False,'Auto-start is supported on Windows only.'
    try:
        import winreg
        path=r'Software\Microsoft\Windows\CurrentVersion\Run'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,path,0,winreg.KEY_SET_VALUE) as key:
            if enabled:winreg.SetValueEx(key,APP,0,winreg.REG_SZ,startup_command())
            else:
                try:winreg.DeleteValue(key,APP)
                except FileNotFoundError:pass
        return True,'enabled' if enabled else 'disabled'
    except OSError as exc:return False,f'Windows could not update startup: {exc}'

def remove_legacy_startup():
    """Remove only startup values created by earlier builds of this project."""
    if os.name!='nt':return
    try:
        import winreg
        path=r'Software\Microsoft\Windows\CurrentVersion\Run'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,path,0,winreg.KEY_SET_VALUE) as key:
            for legacy in ('Win11NetSpeedWidgetPro','Win11NetSpeedCompact'):
                try:winreg.DeleteValue(key,legacy)
                except FileNotFoundError:pass
    except OSError:pass

def taskbar_default(width,height):
    if os.name=='nt':
        try:
            hwnd=_U32.FindWindowW('Shell_TrayWnd',None);r=wintypes.RECT()
            if hwnd and _U32.GetWindowRect(hwnd,ctypes.byref(r)):
                return max(r.left,r.right-width-90),r.top+max(0,(r.bottom-r.top-height)//2)
        except Exception:pass
    return 100,100

class CompactWidget:
    def __init__(self,root):
        self.root=root;self.cfg=load_cfg();self.closed=False;self.drag=None;self.gdrag=None;self.guard_job=None
        self.cur_down_str='0 B/s';self.cur_up_str='0 B/s';self.cur_ram_str='0%';self.cur_cpu_str='0%';self.tooltips=[]
        remove_legacy_startup()
        if not self.cfg.get('first_run_complete',False):
            ok,_=set_autostart(True);self.cfg['autostart']=bool(ok);self.cfg['first_run_complete']=True;save_cfg(self.cfg)
        elif self.cfg.get('autostart',False):
            # Refresh the path in case the folder or EXE was moved after first run.
            ok,_=set_autostart(True);self.cfg['autostart']=bool(ok);save_cfg(self.cfg)
        psutil.cpu_percent(None)  # prime: the first call always returns 0.0
        self.last=counter(self.cfg['interface']);self.last_t=time.perf_counter()
        root.title('Bangla Net Speed Meter · বাংলা নেট স্পিড মিটার');root.overrideredirect(True);root.minsize(100,30)
        x,y=self.cfg['x'],self.cfg['y']
        if x is None or y is None:x,y=taskbar_default(self.cfg['width'],self.cfg['height'])
        root.geometry(f"{self.cfg['width']}x{self.cfg['height']}+{x}+{y}")
        root.attributes('-alpha',self.cfg['opacity']);root.attributes('-topmost',True)
        self.build();self.make_menu();self.bind();self.make_tray();self.apply_style();self.guard();self.tick()
    def build(self):
        self.card=tk.Frame(self.root,highlightthickness=1);self.card.pack(fill='both',expand=True)
        self.speeds=tk.Frame(self.card);self.speed_items={}
        for key in ('down','up'):
            item=tk.Frame(self.speeds);icon=tk.Canvas(item,width=14,height=14,highlightthickness=0,bd=0)
            lab=tk.Label(item,text='0 B/s',anchor='w',width=9)
            icon.pack(side='left',padx=(0,2));lab.pack(side='left')
            self.speed_items[key]=(item,icon,lab)
        self.down=self.speed_items['down'][2];self.up=self.speed_items['up'][2]
        self.stats=tk.Frame(self.card);self.stat_rows={}
        for key in ('ram','cpu'):
            row=tk.Frame(self.stats);icon=tk.Canvas(row,width=14,height=14,highlightthickness=0,bd=0)
            lab=tk.Label(row,text='0%',anchor='w',width=4)
            icon.pack(side='left',padx=(0,2));lab.pack(side='left')
            self.stat_rows[key]=(row,icon,lab)
        self.grip=tk.Label(self.card,text='◢',cursor='size_nw_se',bd=0,padx=0,pady=0)
        self.grip.place(relx=1.0,rely=1.0,anchor='se',x=-1,y=-1)
        self.layout_speeds();self.layout_stats()
        theme_fn=lambda:{'bg':self.cfg['background'],'fg':self.cfg['font_color'],'border':self.cfg['border']}
        self.tooltips=[
            WidgetToolTip([self.speed_items['up'][0],self.speed_items['up'][1],self.speed_items['up'][2]],lambda:tr('tip_upload',self.cfg.get('language','en'),val=self.cur_up_str),theme_fn),
            WidgetToolTip([self.speed_items['down'][0],self.speed_items['down'][1],self.speed_items['down'][2]],lambda:tr('tip_download',self.cfg.get('language','en'),val=self.cur_down_str),theme_fn),
            WidgetToolTip([self.stat_rows['ram'][0],self.stat_rows['ram'][1],self.stat_rows['ram'][2]],lambda:tr('tip_ram',self.cfg.get('language','en'),val=self.cur_ram_str),theme_fn),
            WidgetToolTip([self.stat_rows['cpu'][0],self.stat_rows['cpu'][1],self.stat_rows['cpu'][2]],lambda:tr('tip_cpu',self.cfg.get('language','en'),val=self.cur_cpu_str),theme_fn)
        ]
    def layout_speeds(self):
        layout=self.cfg.get('speed_layout','horizontal')
        for item,_,_ in self.speed_items.values():item.pack_forget()
        if layout=='stacked_up_down':
            for key in ('up','down'):self.speed_items[key][0].pack(side='top',anchor='w')
        elif layout=='stacked_down_up':
            for key in ('down','up'):self.speed_items[key][0].pack(side='top',anchor='w')
        else:
            for key in ('down','up'):self.speed_items[key][0].pack(side='left',padx=3)
        self.position_frames()
    def layout_stats(self):
        mode=self.cfg['stats_mode']
        for row,_,_ in self.stat_rows.values():row.pack_forget()
        if mode=='off':self.stats.place_forget()
        else:
            for key in ('ram','cpu'):
                if mode in ('both',key):self.stat_rows[key][0].pack(side='top',anchor='w')
            self.stats.place(relx=1.0,rely=.5,anchor='e',x=-8)
        self.position_frames()
    def position_frames(self):
        layout=self.cfg.get('speed_layout','horizontal')
        mode=self.cfg.get('stats_mode','both')
        if layout=='horizontal':
            self.speeds.place(relx=.5,rely=.5,anchor='center',x=0)
        else:
            if mode=='off':self.speeds.place(relx=.5,rely=.5,anchor='center',x=0)
            else:self.speeds.place(relx=0.0,rely=.5,anchor='w',x=10)
    def drag_widgets(self):
        ws=[self.root,self.card,self.speeds,self.stats]
        for row,icon,lab in list(self.speed_items.values())+list(self.stat_rows.values()):ws+=[row,icon,lab]
        return ws
    def bind(self):
        for w in self.drag_widgets():
            w.bind('<ButtonPress-1>',self.start_move);w.bind('<B1-Motion>',self.move);w.bind('<ButtonRelease-1>',self.end_move);w.bind('<Button-3>',self.popup)
        self.root.bind_all('<Control-MouseWheel>',self.resize_wheel)
        self.grip.bind('<ButtonPress-1>',self.grip_start);self.grip.bind('<B1-Motion>',self.grip_move);self.grip.bind('<ButtonRelease-1>',self.grip_end);self.grip.bind('<Button-3>',self.popup)
    def make_menu(self):
        lang=self.cfg.get('language','en')
        self.menu=tk.Menu(self.root,tearoff=0)
        units=tk.Menu(self.menu,tearoff=0);self.unit_var=tk.StringVar(value=self.cfg['unit'])
        for label_key,val in [('auto_bytes','auto_bytes'),('auto_bits','auto_bits'),('MB/s','MBps'),('Mbps','Mbps'),('KB/s','KBps'),('Kbps','Kbps')]:
            lbl=tr(label_key,lang) if label_key in ('auto_bytes','auto_bits') else label_key
            units.add_radiobutton(label=lbl,value=val,variable=self.unit_var,command=self.set_unit)
        self.menu.add_cascade(label=tr('speed_unit',lang),menu=units)
        layouts=tk.Menu(self.menu,tearoff=0);self.layout_var=tk.StringVar(value=self.cfg.get('speed_layout','horizontal'))
        for key,val in [('layout_horizontal','horizontal'),('layout_up_down','stacked_up_down'),('layout_down_up','stacked_down_up')]:
            layouts.add_radiobutton(label=tr(key,lang),value=val,variable=self.layout_var,command=self.set_speed_layout)
        self.menu.add_cascade(label=tr('speed_layout',lang),menu=layouts)
        langs=tk.Menu(self.menu,tearoff=0);self.lang_var=tk.StringVar(value=self.cfg.get('language','en'))
        for label,val in [('English','en'),('বাংলা (Bengali)','bn')]:
            langs.add_radiobutton(label=label,value=val,variable=self.lang_var,command=self.on_change_language)
        self.menu.add_cascade(label=tr('language',lang),menu=langs)
        adapters=tk.Menu(self.menu,tearoff=0);self.if_var=tk.StringVar(value=self.cfg['interface']);adapters.add_radiobutton(label=tr('all_interfaces',lang),value='All',variable=self.if_var,command=self.set_interface)
        for name,st in psutil.net_if_stats().items():
            if st.isup:adapters.add_radiobutton(label=name,value=name,variable=self.if_var,command=self.set_interface)
        self.menu.add_cascade(label=tr('network_interface',lang),menu=adapters)
        colors=tk.Menu(self.menu,tearoff=0)
        for key,value in [('color_white','#F8FAFC'),('color_black','#0F172A'),('color_blue','#38BDF8'),('color_green','#34D399'),('color_purple','#A78BFA'),('color_orange','#FB923C')]:
            colors.add_command(label=tr(key,lang),command=lambda c=value:self.set_color(c))
        colors.add_separator();colors.add_command(label=tr('color_custom',lang),command=self.custom_color);self.menu.add_cascade(label=tr('font_color',lang),menu=colors)
        weights=tk.Menu(self.menu,tearoff=0);self.weight_var=tk.StringVar(value=self.cfg['font_weight'])
        for key,value in [('weight_normal','normal'),('weight_semibold','semibold'),('weight_bold','bold')]:
            weights.add_radiobutton(label=tr(key,lang),value=value,variable=self.weight_var,command=self.set_weight)
        self.menu.add_cascade(label=tr('font_weight',lang),menu=weights)
        sizes=tk.Menu(self.menu,tearoff=0);self.size_var=tk.IntVar(value=self.cfg['font_size'])
        for n in (8,9,10,11,12):
            lbl=to_bn_digits(n) if lang=='bn' else str(n)
            sizes.add_radiobutton(label=lbl,value=n,variable=self.size_var,command=self.set_size)
        self.menu.add_cascade(label=tr('font_size',lang),menu=sizes)
        modes=tk.Menu(self.menu,tearoff=0);self.stats_var=tk.StringVar(value=self.cfg['stats_mode'])
        for key,val in [('stats_both','both'),('stats_ram','ram'),('stats_cpu','cpu'),('stats_off','off')]:
            modes.add_radiobutton(label=tr(key,lang),value=val,variable=self.stats_var,command=self.set_stats_mode)
        self.menu.add_cascade(label=tr('cpu_ram_usage',lang),menu=modes)
        sz=tk.Menu(self.menu,tearoff=0)
        for key,dw,dh in [('size_wider',10,0),('size_narrower',-10,0),('size_taller',0,2),('size_shorter',0,-2)]:
            sz.add_command(label=tr(key,lang),command=lambda a=dw,b=dh:self.resize_by(a,b))
        sz.add_separator();sz.add_command(label=tr('size_reset',lang),command=self.reset_size)
        self.menu.add_cascade(label=tr('widget_size',lang),menu=sz)
        self.menu.add_command(label=tr('background_color',lang),command=self.custom_background)
        self.menu.add_command(label=tr('reset_position',lang),command=self.reset_position)
        self.autostart_var=tk.BooleanVar(value=bool(self.cfg.get('autostart',True)));self.menu.add_checkbutton(label=tr('autostart',lang),variable=self.autostart_var,command=self.toggle_autostart)
        self.menu.add_command(label=tr('open_website',lang),command=lambda:webbrowser.open(WEBSITE))
        self.menu.add_separator();self.menu.add_command(label=tr('exit',lang),command=self.quit)
    def on_change_language(self):
        new_lang=self.lang_var.get()
        if new_lang in LANGUAGES:
            self.cfg['language']=new_lang;save_cfg(self.cfg);self.make_menu();self.update_tray()
    def font(self):
        fam='Segoe UI Semibold' if self.cfg['font_weight'] in ('semibold','bold') else 'Segoe UI'
        weight='bold' if self.cfg['font_weight']=='bold' else 'normal'
        return (fam,int(self.cfg['font_size']),weight)
    def apply_style(self):
        bg=self.cfg['background'];fg=self.cfg['font_color'];self.root.configure(bg=bg);self.card.configure(bg=bg,highlightbackground=self.cfg['border'])
        self.speeds.configure(bg=bg);self.stats.configure(bg=bg);self.grip.configure(bg=bg,fg=self.cfg['border'],font=('Segoe UI',6))
        for row,icon,lab in list(self.speed_items.values())+list(self.stat_rows.values()):row.configure(bg=bg);icon.configure(bg=bg);lab.configure(bg=bg,fg=fg,font=self.font())
        self.draw_icons()
    def draw_icons(self):
        c=self.cfg['font_color']
        dn=self.speed_items['down'][1];dn.delete('all');dn.create_polygon(7,13,1,6,5,6,5,1,9,1,9,6,13,6,fill=c,outline=c)
        up=self.speed_items['up'][1];up.delete('all');up.create_polygon(7,1,1,8,5,8,5,13,9,13,9,8,13,8,fill=c,outline=c)
        ram=self.stat_rows['ram'][1];ram.delete('all')
        ram.create_rectangle(1,3,13,9,outline=c,width=1)  # memory stick body
        for x in (3,6,9):ram.create_line(x,9,x,12,fill=c)  # contacts
        ram.create_line(3,5,11,5,fill=c)
        cpu=self.stat_rows['cpu'][1];cpu.delete('all')
        cpu.create_rectangle(3,3,11,11,outline=c,width=1);cpu.create_rectangle(5,5,9,9,fill=c,outline=c)
        for p in (5,9):
            cpu.create_line(p,0,p,3,fill=c);cpu.create_line(p,11,p,14,fill=c)
            cpu.create_line(0,p,3,p,fill=c);cpu.create_line(11,p,14,p,fill=c)
    def set_stats_mode(self):
        old=self.cfg['stats_mode']!='off';self.cfg['stats_mode']=self.stats_var.get();new=self.cfg['stats_mode']!='off'
        self.layout_stats()
        if old!=new:self.resize_by(STATS_W if new else -STATS_W,0)
        else:save_cfg(self.cfg)
    def set_speed_layout(self):
        old=self.cfg.get('speed_layout','horizontal')!='horizontal'
        self.cfg['speed_layout']=self.layout_var.get()
        new=self.cfg['speed_layout']!='horizontal'
        self.layout_speeds()
        if old!=new:self.resize_by(-SPEED_LAYOUT_W if new else SPEED_LAYOUT_W,0)
        else:save_cfg(self.cfg)
    def hide_tooltips(self):
        for tt in getattr(self,'tooltips',[]):tt.hide()
    def popup(self,e):self.hide_tooltips();self.menu.tk_popup(e.x_root,e.y_root)
    def start_move(self,e):self.hide_tooltips();self.drag=(e.x_root-self.root.winfo_x(),e.y_root-self.root.winfo_y());self.root.lift()
    def move(self,e):
        if self.drag:self.root.geometry(f'+{e.x_root-self.drag[0]}+{e.y_root-self.drag[1]}')
    def end_move(self,e):
        self.drag=None;self.cfg['x']=self.root.winfo_x();self.cfg['y']=self.root.winfo_y();save_cfg(self.cfg)
    def apply_size(self,w,h):
        w=min(2000,max(100,int(w)));h=min(400,max(30,int(h)));self.cfg['width']=w;self.cfg['height']=h
        self.root.geometry(f'{w}x{h}');save_cfg(self.cfg)
    def resize_by(self,dw,dh):self.apply_size(self.root.winfo_width()+dw,self.root.winfo_height()+dh)
    def resize_wheel(self,e):self.resize_by(10,2) if e.delta>0 else self.resize_by(-10,-2)
    def reset_size(self):
        w=DEFAULT['width']
        if self.cfg.get('speed_layout','horizontal')!='horizontal':w-=SPEED_LAYOUT_W
        if self.cfg['stats_mode']=='off':w-=STATS_W
        self.apply_size(w,DEFAULT['height'])
    def grip_start(self,e):self.gdrag=(e.x_root,e.y_root,self.root.winfo_width(),self.root.winfo_height())
    def grip_move(self,e):
        g=getattr(self,'gdrag',None)
        if g:self.root.geometry(f'{min(2000,max(100,g[2]+e.x_root-g[0]))}x{min(400,max(30,g[3]+e.y_root-g[1]))}')
    def grip_end(self,e):
        if getattr(self,'gdrag',None):self.gdrag=None;self.apply_size(self.root.winfo_width(),self.root.winfo_height())
    def set_unit(self):self.cfg['unit']=self.unit_var.get();save_cfg(self.cfg)
    def set_interface(self):self.cfg['interface']=self.if_var.get();self.last=counter(self.cfg['interface']);self.last_t=time.perf_counter();save_cfg(self.cfg)
    def set_color(self,c):self.cfg['font_color']=c;self.apply_style();save_cfg(self.cfg)
    def custom_color(self):
        lang=self.cfg.get('language','en')
        c=colorchooser.askcolor(color=self.cfg['font_color'],title=tr('dlg_font_color',lang))[1]
        if c:self.set_color(c)
    def custom_background(self):
        lang=self.cfg.get('language','en')
        c=colorchooser.askcolor(color=self.cfg['background'],title=tr('dlg_bg',lang))[1]
        if c:self.cfg['background']=c;self.apply_style();save_cfg(self.cfg)
    def set_weight(self):self.cfg['font_weight']=self.weight_var.get();self.apply_style();save_cfg(self.cfg)
    def set_size(self):self.cfg['font_size']=self.size_var.get();self.apply_style();save_cfg(self.cfg)
    def reset_position(self):
        x,y=taskbar_default(self.root.winfo_width(),self.root.winfo_height());self.root.geometry(f'+{x}+{y}');self.cfg.update(x=x,y=y);save_cfg(self.cfg)
    def toggle_autostart(self):
        requested=bool(self.autostart_var.get());ok,message=set_autostart(requested)
        self.cfg['autostart']=requested if ok else not requested
        self.autostart_var.set(self.cfg['autostart']);save_cfg(self.cfg)
        if not ok:
            from tkinter import messagebox
            lang=self.cfg.get('language','en')
            messagebox.showerror(tr('dlg_startup',lang),message,parent=self.root)

    def bring_to_front(self):
        if self.closed:return
        self.root.deiconify();self.root.attributes('-topmost',True);self.root.lift()
        if os.name=='nt':
            try:
                HWND_TOPMOST=wintypes.HWND(-1);flags=0x0001|0x0002|0x0010|0x0040
                _U32.SetWindowPos(self.root.winfo_id(),HWND_TOPMOST,0,0,0,0,flags)
            except Exception:pass
        for tt in getattr(self,'tooltips',[]):tt.raise_up()
    def guard(self):
        if self.closed:return
        # Keep exactly one guard timer alive; never move or hide the widget.
        self.bring_to_front()
        self.guard_job=self.root.after(max(500,int(self.cfg['topmost_refresh_ms'])),self.guard)
    def tick(self):
        if self.closed:return
        now=time.perf_counter();cur=counter(self.cfg['interface']);dt=max(.05,now-self.last_t)
        down=max(0,(cur.bytes_recv-self.last.bytes_recv)/dt);up=max(0,(cur.bytes_sent-self.last.bytes_sent)/dt)
        self.cur_down_str=fmt_speed(down,self.cfg['unit']);self.cur_up_str=fmt_speed(up,self.cfg['unit'])
        self.down.configure(text=self.cur_down_str);self.up.configure(text=self.cur_up_str)
        mode=self.cfg['stats_mode']
        if mode in ('both','ram'):
            self.cur_ram_str=f'{psutil.virtual_memory().percent:.0f}%'
            self.stat_rows['ram'][2].configure(text=self.cur_ram_str)
        if mode in ('both','cpu'):
            self.cur_cpu_str=f'{psutil.cpu_percent(None):.0f}%'
            self.stat_rows['cpu'][2].configure(text=self.cur_cpu_str)
        for tt in getattr(self,'tooltips',[]):tt.update_text()
        self.last,self.last_t=cur,now;self.root.after(max(200,int(self.cfg['interval_ms'])),self.tick)
    def update_tray(self):
        if getattr(self,'tray',None):
            lang=self.cfg.get('language','en')
            menu=pystray.Menu(pystray.MenuItem(tr('bring_to_front',lang),lambda:self.root.after(0,self.bring_to_front),default=True),pystray.MenuItem(tr('exit',lang),lambda:self.root.after(0,self.quit)))
            self.tray.menu=menu
    def make_tray(self):
        im=Image.new('RGBA',(64,64),(23,32,51,255));d=ImageDraw.Draw(im);d.line((8,48,23,31,35,39,56,14),fill=(56,189,248),width=6)
        lang=self.cfg.get('language','en')
        menu=pystray.Menu(pystray.MenuItem(tr('bring_to_front',lang),lambda:self.root.after(0,self.bring_to_front),default=True),pystray.MenuItem(tr('exit',lang),lambda:self.root.after(0,self.quit)))
        self.tray=pystray.Icon(APP,im,'Bangla Net Speed Meter · Iqbal Mahmud',menu);threading.Thread(target=self.tray.run,daemon=True).start()
    def quit(self):
        self.closed=True
        self.hide_tooltips()
        if self.guard_job:
            try:self.root.after_cancel(self.guard_job)
            except Exception:pass
        try:self.tray.stop()
        except Exception:pass
        self.root.destroy()

if __name__=='__main__':
    if not single_instance():sys.exit(0)
    root=tk.Tk();CompactWidget(root);root.mainloop()
