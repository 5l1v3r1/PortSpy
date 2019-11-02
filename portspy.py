#!/usr/bin/python3
# -*- coding: utf-8 -*-
########################################################
# PortSpy: Multi Threaded Port Scan Tool With Simple GUI
########################################################
# Version: {2.0}
################
# CodedBy: Oseid Aldary
########################
# Follow Me: github.com/Oseid
#############################
import queue,threading,socket
from PyQt5 import QtCore, QtGui, QtWidgets
from time import sleep as se
qu = queue.Queue()
fltr = lambda lst: list(filter(lambda elem:elem if elem.strip() else None,lst))
stop,pause = False,False
THREADS = []
open_ports = 0
headers = ["Target", "Protocol", "Port", "Service"]
noemit = 0
def isFloat(var):
    try:
        test = float(var)
        return True
    except ValueError: return False
def getPorts(ports):
    PORTS = []
    ports = ports.strip()
    if "," in ports:
        ports = fltr(ports.split(","))
        for port in ports:
            if "-" not in port:
                if port.isdigit():PORTS.append(int(port))
            else:
                if port.count("-")==1:
                    s,e= port.split("-")
                    if s.isdigit() and e.isdigit():
                        s,e=int(s),int(e)
                        if s<e:
                            if s >=0 and e <= 65535: PORTS+=range(s, e+1)
    elif "-" in ports:
        if ports.count("-")==1:
            s,e = ports.split("-")
            if s.isdigit() and e.isdigit():
                s,e=int(s),int(e)
                if s<e:
                    if s >= 0 and e <= 65535:PORTS=range(s, e+1)
    else:
        if ports.isdigit() and 0 <= int(ports) <= 65535 :PORTS = [int(ports)]
    return PORTS
def service(port):
    try:return socket.getservbyport(int(port))
    except socket.error:return "??"
class anymation(QtCore.QThread):
    setTitle = QtCore.pyqtSignal(str)
    def __init__(self):
        QtCore.QThread.__init__(self)
    def run(self):
        global pause
        self.done = False
        self.pause = False
        anim = ('[=      ]', '[ =     ]', '[  =    ]', '[   =   ]',
         '[    =  ]', '[     = ]', '[      =]', '[      =]',
         '[     = ]', '[    =  ]', '[   =   ]', '[  =    ]',
      '[ =     ]', '[=      ]')
        i = 0
        dot = "."
        while not self.done:
                if not self.done and self.pause:
                    self.setTitle.emit("[Paused]")
                    while self.pause and not self.done:continue
                    if self.done:break
                    else:
                        self.setTitle.emit("[Resuming]...")
                        se(1)
                        pause = False
                if self.done:break
                if len(dot) ==4:dot = "."
                self.setTitle.emit(anim[i % len(anim)]+" Scanning"+dot)
                se(1.0/5)
                i+=1
                dot+="."
        self.setTitle.emit("PortSpy{2.0}")
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self,rows):
        QtCore.QAbstractTableModel.__init__(self)
        self.rows = rows
    def rowCount(self, parent):return len(self.rows)
    def columnCount(self, parent):return len(headers)
    def data(self, index, role):
        if role != QtCore.Qt.DisplayRole:return QtCore.QVariant()
        return self.rows[index.row()][index.column()]
    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Horizontal:return QtCore.QVariant()
        return headers[section]
def scan(setTobox,signal,server,proto,timeout):
    global open_ports
    global noemit
    while not stop:
        if not stop and pause:
            while pause and not stop:se(1)
        if qu.empty():break
        try:port = qu.get()
        except Exception:break
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) if proto == "tcp" else socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        try:
          s.connect((server,port))
          s.close()
          setTobox.emit([(server,proto,str(port),service(port))])
          open_ports+=1
        except socket.error:pass
        except Exception:qu.put(port)
        qu.task_done()
    if not noemit:signal.emit("")
class Scan(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)
    setTobox = QtCore.pyqtSignal(list)
    def __init__(self,ip,proto,timeout,threads):
        QtCore.QThread.__init__(self)
        self.ip,self.proto,self.timeout,self.threads = ip,proto,timeout,threads
    def run(self):
        global THREADS
        for i in range(self.threads):
            thread = threading.Thread(target=scan,args=(self.setTobox,self.signal,self.ip,self.proto,self.timeout))
            thread.setDaemon = True
            thread.start()
            THREADS.append(thread)
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowIcon(QtGui.QIcon(self.iconFromBase64(b'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')))
        MainWindow.setFixedSize(503, 325)
        MainWindow.setStyleSheet("""
            QMainWindow{background-color:#e9ebee;}
            QPushButton {
              background-color:#e1e1e1;
              border:1px solid #adadad;
              outline:none;
              border-radius:3px;
              font: "MS Shell Dlg 2";
              }
            QPushButton:hover {
              background-color:#e5f1fb;
              border:1px solid #3190dc;
              font:bold;
              }
            QPushButton:pressed {
              background-color:#cce4f7;
              border:1px solid #1e68a4;
              }
            QMessageBox QPushButton{
              background-color:#e1e1e1;
              border:1px solid #adadad;
              width:45px;
            }""")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(9, 2, 483, 95))
        self.groupBox.setStyleSheet("""
            QLineEdit{
              border: 1px solid silver;
              border-radius: 3px;
              background-color:rgb(245,245,245);
              }
            QLineEdit:focus{border:1px solid #3190dc;}
            QGroupBox {
              border: 1px solid #CCC;
              border-radius: 3px;
              margin-top: 0.5em;
              background-color:white;
              }
            QGroupBox::title {
              subcontrol-origin: margin;
              left: 10px;
              padding: 0 2px 0 2px;
              color:gray;
              }
            """)
        self.groupBox.setObjectName("groupBox")
        self.label_1 = QtWidgets.QLabel(self.groupBox)
        self.label_1.setGeometry(QtCore.QRect(28, 13, 48, 21))
        self.label_1.setObjectName("label_1")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(34, 43, 41, 13))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 68, 61, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(187, 15, 52, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(186, 40, 47, 20))
        self.label_5.setObjectName("label_5")
        self.target = QtWidgets.QLineEdit(self.groupBox)
        self.target.setGeometry(QtCore.QRect(70, 13, 91, 20))
        self.target.setObjectName("target")
        self.PORTS = QtWidgets.QLineEdit(self.groupBox)
        self.PORTS.setGeometry(QtCore.QRect(70, 39, 91, 20))
        self.PORTS.setObjectName("PORTS")
        self.PROTOCOL = QtWidgets.QLineEdit(self.groupBox)
        self.PROTOCOL.setGeometry(QtCore.QRect(70, 65, 51, 20))
        self.PROTOCOL.setObjectName("PROTOCOL")
        self.TIMEOUT = QtWidgets.QLineEdit(self.groupBox)
        self.TIMEOUT.setGeometry(QtCore.QRect(235, 13, 51, 20))
        self.TIMEOUT.setObjectName("TIMEOUT")
        self.threads = QtWidgets.QLineEdit(self.groupBox)
        self.threads.setGeometry(QtCore.QRect(235, 39, 51, 20))
        self.threads.setObjectName("threads")
        self.ScanBtnIcon = self.iconFromBase64(b'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')
        self.PauseBtnIcon = self.iconFromBase64(b'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')
        self.StopBtnIcon = self.iconFromBase64(b'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')
        self.ResumeBtnIcon = self.iconFromBase64(b'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')
        self.ScanBtn = QtWidgets.QPushButton(self.centralwidget)
        self.ScanBtn.setGeometry(QtCore.QRect(8, 111, 74, 23))
        self.ScanBtn.setObjectName("ScanBtn")
        self.ScanBtn.setIcon(self.ScanBtnIcon)
        self.PauseBtn = QtWidgets.QPushButton(self.centralwidget)
        self.PauseBtn.setGeometry(QtCore.QRect(8, 141, 75, 23))
        self.PauseBtn.setObjectName("PauseBtn")
        self.PauseBtn.setIcon(self.PauseBtnIcon)
        self.PauseBtn.setStyleSheet("padding-left:4px;")
        self.StopBtn = QtWidgets.QPushButton(self.centralwidget)
        self.StopBtn.setGeometry(QtCore.QRect(8, 171, 75, 23))
        self.StopBtn.setObjectName("StopBtn")
        self.StopBtn.setIcon(self.StopBtnIcon)
        self.StopBtn.setStyleSheet("padding-right:4px;")
        self.ClearBtn = QtWidgets.QPushButton(self.centralwidget)
        self.ClearBtn.setGeometry(QtCore.QRect(8, 201, 75, 23))
        self.ClearBtn.setObjectName("ClearBtn")
        self.ClearAllBtn = QtWidgets.QPushButton(self.centralwidget)
        self.ClearAllBtn.setGeometry(QtCore.QRect(8, 231, 75, 23))
        self.ClearAllBtn.setObjectName("ClearAllBtn")
        self.ShowBox = QtWidgets.QTableView(self.centralwidget)
        self.ShowBox.setGeometry(QtCore.QRect(90, 110, 402, 192))
        self.ShowBox.setObjectName("ShowBox")
        self.ShowBox.setStyleSheet("""
            QTableView {
              background-color:white;
              border: 1px solid #CCC;
              border-radius: 3px;
              outline:none;
              show-decoration-selected: 1;
              }
            QTableView::item {
              outline:none;
              background-color:rgb(245,245,245);
              border:0px;
              padding:5px;
              border-top-color: transparent;
              border-bottom-color: transparent;
              }
            QTableView::item:hover {
              background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
              border: 1px solid #bfcde4;
              }
            QTableView::item:selected {border: 1px solid #567dbc;}
            QTableView::item:selected:active{background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);}
            QTableView::item:selected:!active {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);}
            QHeaderView{color:gray;
            }""")
        self.ShowBox.setModel(self.headersMod())
        self.ShowBox.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.ShowBox.verticalHeader().setVisible(False)
        self.Scan = Scan("","", "","")
        self.anym = anymation()
        self.rows = []
        self.paused = False
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PortSpy{2.0}"))
        self.groupBox.setTitle(_translate("MainWindow", "Config"))
        self.label_1.setText(_translate("MainWindow", "Target :"))
        self.label_2.setText(_translate("MainWindow", "Ports :"))
        self.label_3.setText(_translate("MainWindow", "Protocol :"))
        self.label_4.setText(_translate("MainWindow", "Timeout :"))
        self.label_5.setText(_translate("MainWindow", "Threads :"))
        self.ScanBtn.setText(_translate("MainWindow", "Scan"))
        self.PauseBtn.setText(_translate("MainWindow", "Pause"))
        self.StopBtn.setText(_translate("MainWindow", "Stop"))
        self.ClearBtn.setText(_translate("MainWindow", "Clear Table"))
        self.ClearAllBtn.setText(_translate("MainWindow", "Reset"))
        self.target.setPlaceholderText(_translate("MainWindow", "x.x.x.x"))
        self.PORTS.setToolTip(_translate("MainWindow", "Set A Ports To Scan:\n 1 - Single port E.g[80]\n 2 - Many ports E.g[21,22,80]\n 3 - Range Of Ports E.g[1-1025]"))
        self.PORTS.setPlaceholderText(_translate("MainWindow", "21,22,30-90,443"))
        self.PROTOCOL.setToolTip(_translate("MainWindow", "Set connection protocol <br> Default : TCP"))
        self.PROTOCOL.setPlaceholderText(_translate("MainWindow", "TCP,UDP"))
        self.TIMEOUT.setToolTip(_translate("MainWindow", "set connection Timeout in seconds<br>Default: 2s"))
        self.TIMEOUT.setPlaceholderText(_translate("MainWindow", "2"))
        self.threads.setToolTip(_translate("MainWindow", "set the number of threads <br> Default: 5 threads"))
        self.threads.setPlaceholderText(_translate("MainWindow", "5"))
        self.ensc(False)
        self.enpu(False)
        self.enst(False)
        self.encl(False)
        self.encla(False)
        self.target.textChanged.connect(self.check)
        self.PORTS.textChanged.connect(self.check)
        self.Scan.signal.connect(self.FIN)
        self.Scan.setTobox.connect(self.updatebox)
        self.anym.setTitle.connect(lambda text: MainWindow.setWindowTitle(text))
        self.ScanBtn.clicked.connect(self.START)
        self.PauseBtn.clicked.connect(self.PAUSE)
        self.StopBtn.clicked.connect(self.STOP)
        self.ClearBtn.clicked.connect(self.CLEAR)
        self.ClearAllBtn.clicked.connect(self.CLEARALL)
    def check(self):
        tartext = self.target.text().strip()
        portext = self.PORTS.text().strip()
        if not tartext or not portext:self.ensc(False)
        elif not set(portext).issubset("01234567890-,") or "-," in portext or ",-" in portext:self.ensc(False)
        else:self.ensc(True)
    def START(self):
        global THREADS
        global stop
        global pause
        global open_ports
        global noemit
        del THREADS[:]
        del self.rows[:]
        stop = False
        pause = False
        noemit = 0
        open_ports=0
        self.statusbar.showMessage("")
        self.CLEAR()
        self.ensc(False)
        self.encl(False)
        self.encla(False)
        self.deinput(False)
        ip,ports,proto,timeout,threads = self.target.text(),self.PORTS.text(),self.PROTOCOL.text(),self.TIMEOUT.text(),self.threads.text()
        ports = getPorts(ports)
        if not ports:
            self.ShowMsg("PortSpy ~ ERROR","Ports Must be in range 0-65535 !")
            self.PORTS.clear()
            self.ensc(False)
            self.deinput(True)
            return
        ports = list(dict.fromkeys(ports))
        if proto.strip():
            if  proto.lower() not in ("tcp","udp"):
                self.ShowMsg("PortSpy ~ ERROR","Invalid Connection Protocol!")
                self.PROTOCOL.clear()
                self.ensc(True)
                self.deinput(True)
                return
            else:proto = proto.lower()
        else: proto = "tcp"
        if timeout.strip():
            if timeout.isdigit(): timeout = int(timeout)
            elif isFloat(timeout): timeout = float(timeout)
            else:
                self.ShowMsg("PortSpy ~ ERROR","Invalid Connection timeout!")
                self.TIMEOUT.clear()
                self.ensc(True)
                self.deinput(True)
                return
        else: timeout = 2
        if threads.strip():
            if not threads.isdigit():
                self.ShowMsg("PortSpy ~ ERROR","Invalid Threads Number!")
                self.threads.clear()
                self.ensc(True)
                self.deinput(True)
                return
            else:threads = int(threads)
        else:threads=5
        if len(ports) < threads:threads = len(ports)
        if not qu.empty():
            with qu.mutex: qu.queue.clear()
        for port in ports:qu.put(port)
        self.Scan.ip,self.Scan.proto,self.Scan.timeout,self.Scan.threads = ip,proto,timeout,threads
        self.Scan.start()
        self.anym.start()
        self.enpu(True)
        self.enst(True)
    def deinput(self,val):
        self.target.setEnabled(val)
        self.PORTS.setEnabled(val)
        self.TIMEOUT.setEnabled(val)
        self.PROTOCOL.setEnabled(val)
        self.threads.setEnabled(val)
    def headersMod(self):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        return model
    def updatebox(self,rows):
        self.rows+=rows
        model = TableModel(self.rows)
        self.ShowBox.setModel(model)
    def PAUSE(self):
        global pause
        if not self.paused:
            pause = True
            self.anym.pause = True
            self.PauseBtn.setText("Resume")
            self.PauseBtn.setIcon(self.ResumeBtnIcon)
            self.paused = True
        else:
            self.anym.pause = False
            self.PauseBtn.setText("Pause")
            self.PauseBtn.setIcon(self.PauseBtnIcon)
            self.paused = False
    def STOP(self):
        global THREADS
        global stop
        global open_ports
        global noemit
        noemit = 1
        stop = True
        self.anym.done = True
        self.statusbar.showMessage("[!] Scan [Aborted]{}".format("(No Open Ports)" if not open_ports else "({} Ports is Open)".format(open_ports)))
        self.PauseBtn.setText("Pause")
        self.PauseBtn.setIcon(self.PauseBtnIcon)
        for thread in THREADS:thread.join()
        self.enpu(False)
        self.enst(False)
        self.ensc(True)
        self.encla(True)
        self.deinput(True)
        if self.rows:self.encl(True)
    def CLEAR(self):
        self.ShowBox.setModel(self.headersMod())
        self.encl(False)
    def CLEARALL(self):
        self.target.clear()
        self.PORTS.clear()
        self.PROTOCOL.clear()
        self.TIMEOUT.clear()
        self.threads.clear()
        self.statusbar.showMessage("")
        self.CLEAR()
        self.encl(False)
        self.encla(False)
    def FIN(self,text):
        global open_ports
        self.anym.done = True
        self.statusbar.showMessage("[*] Scan [Finished]{}".format("(No Open Ports)" if not open_ports else "({} Ports is Open)".format(open_ports)))
        self.enpu(False)
        self.enst(False)
        self.ensc(True)
        self.encla(True)
        self.deinput(True)
        if self.rows:self.encl(True)
    def iconFromBase64(self,base64):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray.fromBase64(base64))
        return QtGui.QIcon(pixmap)
    ShowMsg = lambda self, title,MSG: QtWidgets.QMessageBox.about(MainWindow, title,MSG)
    ensc = lambda self,val: self.ScanBtn.setEnabled(val)
    enpu = lambda self,val: self.PauseBtn.setEnabled(val) 
    enst = lambda self,val: self.StopBtn.setEnabled(val)
    encl = lambda self,val: self.ClearBtn.setEnabled(val) 
    encla = lambda self,val: self.ClearAllBtn.setEnabled(val)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
##############################################################
#####################                #########################
#####################   END OF TOOL  #########################
#####################                #########################
##############################################################
#This Tool by Oseid Aldary
#Have a nice day :)
#GoodBye
