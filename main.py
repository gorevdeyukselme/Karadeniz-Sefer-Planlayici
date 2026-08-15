import csv
from math import radians,sin,cos,sqrt,atan2
from pathlib import Path
from datetime import datetime,timedelta
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.mapview import MapView,MapMarker
from plyer import gps

KV='''
<Root>:
    orientation:'vertical'
    BoxLayout:
        size_hint_y:None;height:'46dp';spacing:'3dp';padding:'3dp'
        Button:text:'GPS';on_release:app.start_gps()
        Button:text:'Istasyon';on_release:app.toggle_stations()
        Button:text:'Liman';on_release:app.toggle_ports()
        Button:text:'Log';on_release:app.show_log()
    Label:
        size_hint_y:None;height:'42dp';text:app.gps_text;text_size:self.width-dp(8),None;halign:'left'
    Label:
        size_hint_y:None;height:'48dp';text:app.info_text;text_size:self.width-dp(8),None;halign:'left'
    BoxLayout:id:mapbox
    GridLayout:
        cols:3;size_hint_y:None;height:'100dp';spacing:'3dp';padding:'3dp'
        Button:text:'Sefer Baslat';on_release:app.log('cikis')
        Button:text:'Varis';on_release:app.log('varis')
        Button:text:'Hareket';on_release:app.log('hareket')
        Button:text:'CTD Baslat';on_release:app.log('CTD basladi')
        Button:text:'CTD Tamam';on_release:app.log('CTD tamamlandi')
        Button:text:'Su Orn. Tamam';on_release:app.log('Su orneklemesi tamamlandi')
'''
class Root(BoxLayout):pass
class TxtMarker(MapMarker):
    def __init__(self,text='',fs=8,color=(.02,.23,.62,1),**kw):
        kw.setdefault('anchor_x',.5);kw.setdefault('anchor_y',.25);super().__init__(**kw);self.source=''
        l=CoreLabel(text='• '+text,font_size=fs,color=color);l.refresh();self.texture=l.texture
        if self.texture:self.size_hint=(None,None);self.size=(max(dp(12),self.texture.width),max(dp(12),self.texture.height))
class SeferApp(App):
    gps_text=StringProperty('GPS bekleniyor...');info_text=StringProperty('GPS baslatin veya nokta secin.');AUTO=.15
    def build(self):
        self.rootui=Builder.load_string(KV);self.map=MapView(zoom=7,lat=41.2,lon=36.5);self.rootui.ids.mapbox.add_widget(self.map)
        self.base=Path(__file__).parent;self.st=self.read('stations.csv');self.po=self.read('ports.csv',True);self.sm=[];self.pm=[];self.sv=self.pv=False;self.ship=None;self.lat=self.lon=self.speed=None;self.near=self.sel=None;self.arr=set();self.logs=[];self.load_logs();Clock.schedule_once(lambda d:self.show_stations(),.4);return self.rootui
    def on_start(self):
        if platform=='android':
            try:
                from android.permissions import request_permissions,Permission
                request_permissions([Permission.ACCESS_FINE_LOCATION,Permission.ACCESS_COARSE_LOCATION])
            except:pass
    def read(self,fn,ports=False):
        p=self.base/fn;out=[]
        for enc in ('utf-8-sig','utf-8','cp1254','latin1'):
            try:
                with p.open(encoding=enc,newline='') as f:
                    sample=f.read(1000);f.seek(0);sep=';' if sample.count(';')>=sample.count(',') else ','
                    for r in csv.DictReader(f,delimiter=sep):
                        try:
                            if ports:out.append(dict(name=r['Name'].strip(),lat=float(r['Latitude']),lon=float(r['Longitude']),type=r.get('Type','')))
                            else:out.append(dict(name=r['Station'].strip(),project=r.get('Proje','').strip(),lat=float(r['Latitude']),lon=float(r['Longitude']),city=r.get('City',''),district=r.get('District','')))
                        except:pass
                return out
            except:continue
        return out
    def clear(self,a):
        for m in a:
            try:self.map.remove_marker(m)
            except:pass
        a[:]=[]
    def toggle_stations(self):
        if self.sv:self.clear(self.sm);self.sv=False
        else:self.show_stations()
    def toggle_ports(self):
        if self.pv:self.clear(self.pm);self.pv=False
        else:self.show_ports()
    def show_stations(self):
        self.clear(self.sm)
        for s in self.st:
            m=TxtMarker(lat=s['lat'],lon=s['lon'],text=f"{s['project']} | {s['name']}",fs=8);m.bind(on_release=lambda x,z=s:self.pick_station(z));self.map.add_marker(m);self.sm.append(m)
        self.sv=True;self.info_text=f'{len(self.st)} istasyon gosteriliyor.'
    def show_ports(self):
        self.clear(self.pm)
        for p in self.po:
            m=TxtMarker(lat=p['lat'],lon=p['lon'],text=p['name'],fs=7,color=(.55,.28,.02,1));m.bind(on_release=lambda x,z=p:self.pick_port(z));self.map.add_marker(m);self.pm.append(m)
        self.pv=True;self.info_text=f'{len(self.po)} liman/barinak gosteriliyor.'
    def pick_station(self,s):self.sel=f"{s['project']} | {s['name']}";self.near=s;self.info_text=self.sel
    def pick_port(self,p):self.sel=p['name'];self.info_text=p['name']
    def start_gps(self):
        try:gps.configure(on_location=self.on_loc,on_status=lambda a,b:setattr(self,'gps_text','GPS: '+str(b)));gps.start(minTime=1000,minDistance=1);self.gps_text='GPS baslatildi...'
        except Exception as e:self.gps_text='GPS hata: '+str(e)
    def nm(self,a,b,c,d):
        R=6371.0088;x=radians(c-a);y=radians(d-b);q=sin(x/2)**2+cos(radians(a))*cos(radians(c))*sin(y/2)**2;return R*2*atan2(sqrt(q),sqrt(1-q))/1.852
    def on_loc(self,**k):
        if k.get('lat') is None:return
        self.lat=float(k['lat']);self.lon=float(k['lon']);self.speed=float(k.get('speed') or 0)*1.943844;self.gps_text=f'GPS: {self.lat:.5f}, {self.lon:.5f} | {self.speed:.1f} kt';self.map.center_on(self.lat,self.lon)
        if self.ship:
            try:self.map.remove_marker(self.ship)
            except:pass
        self.ship=TxtMarker(lat=self.lat,lon=self.lon,text='GEMI',fs=9,color=(0,0,0,1));self.map.add_marker(self.ship)
        best=min(((self.nm(self.lat,self.lon,s['lat'],s['lon']),s) for s in self.st),default=None,key=lambda x:x[0])
        if best:
            d,s=best;self.near=s;eta=''
            if self.speed>.3:eta=' | ETA '+(datetime.now()+timedelta(hours=d/self.speed)).strftime('%H:%M')
            self.info_text=f"{s['project']} | {s['name']} | {d:.2f} NM{eta}";key=f"{s['project']}|{s['name']}"
            if d<=self.AUTO and key not in self.arr:self.arr.add(key);self.add_log('varis (GPS otomatik)',f"{s['project']} | {s['name']}")
    def path(self):return Path(self.user_data_dir)/f"sefer_log_{datetime.now():%Y%m%d}.csv"
    def log(self,event):self.add_log(event,self.sel or (f"{self.near['project']} | {self.near['name']}" if self.near else ''))
    def add_log(self,event,point=''):
        t=datetime.now();self.logs.append((t,event,point));p=self.path();exists=p.exists();p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('a',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f,delimiter=';');
            if not exists:w.writerow(['Tarih','Saat','Olay','Nokta','Latitude','Longitude'])
            w.writerow([t.strftime('%d.%m.%Y'),t.strftime('%H:%M:%S'),event,point,self.lat or '',self.lon or ''])
        self.info_text=f"{t:%H:%M} — {point} {event}"
    def load_logs(self):
        p=self.path()
        if not p.exists():return
        try:
            with p.open(encoding='utf-8-sig') as f:
                for r in csv.DictReader(f,delimiter=';'):
                    t=datetime.strptime(r['Tarih']+' '+r['Saat'],'%d.%m.%Y %H:%M:%S');self.logs.append((t,r['Olay'],r['Nokta']))
        except:pass
    def show_log(self):
        text='\n'.join(f'{t:%H:%M} — {p} {e}' for t,e,p in self.logs[-30:]) or 'Henuz kayit yok.';box=BoxLayout(orientation='vertical');lab=Label(text=text,halign='left',valign='top');lab.bind(size=lambda i,v:setattr(i,'text_size',v));box.add_widget(lab);b=Button(text='Kapat',size_hint_y=None,height='48dp');box.add_widget(b);pop=Popup(title='Sefer Kayit Defteri',content=box,size_hint=(.95,.85));b.bind(on_release=pop.dismiss);pop.open()
if __name__=='__main__':SeferApp().run()
