# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 09:29:07 2021

@author: hcji
"""

import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TPCA")

import numpy as np
import pandas as pd

from scipy import stats
from sklearn import metrics

from PyQt5.QtCore import Qt, QVariant
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

from MainWindow import Ui_MainWindow
from ColumnSelectUI import ColumnSelectUI
from AnalROCUI import AnalROCUI
from AnalTSAUI import AnalTSAUI
from AnaliTSAUI import AnaliTSAUI
from PreprocessUI import PreprocessUI
from NPTSAUI import NPTSAUI
from Thread import CurveFitThread, ROCThread, PairThread, ComplexThread, NPTSAThread
from MakeFigure import MakeFigure
from Utils import TableModel, fit_curve
from iTSA import estimate_df

# proteinData1 = pd.read_csv('data/TPCA_TableS14_DMSO.csv')
# proteinData2 = pd.read_csv('data/TPCA_TableS14_MTX.csv')
# columns = ['T37', 'T40', 'T43', 'T46', 'T49', 'T52', 'T55', 'T58', 'T61', 'T64']
# proteinPair = pd.read_csv('data/TPCA_TableS2_Protein_Pairs.csv')
# proteinComplex = pd.read_csv('data/TPCA_TableS3_Protein_Complex.csv')


class TCPA_Main(QMainWindow, Ui_MainWindow):
    
    def __init__(self, parent=None):
        super(TCPA_Main, self).__init__(parent)
        self.setupUi(self)
        
        # main window
        self.resize(1300, 800)
        self.setMinimumWidth(1150)
        self.setMinimumHeight(650)
        self.move(75, 50)
        self.setWindowTitle("TSAnalyst")
        self.setWindowIcon(QtGui.QIcon("img/TPCA.ico"))
        
        # threads
        self.CurveFitThread = None
        self.ROCThread = None
        self.PairThread = None
        self.ComplexThread = None
        self.NPTSAThread = None
        
        # groupbox
        self.figureG1 = MakeFigure(5, 5)
        self.figureG1_ntb = NavigationToolbar(self.figureG1, self)
        self.gridlayoutG1 = QGridLayout(self.groupBox)
        self.gridlayoutG1.addWidget(self.figureG1)
        self.gridlayoutG1.addWidget(self.figureG1_ntb)
        
        self.figureG2 = MakeFigure(5, 5)
        self.figureG2_ntb = NavigationToolbar(self.figureG2, self)
        self.gridlayoutG2 = QGridLayout(self.groupBox_2)
        self.gridlayoutG2.addWidget(self.figureG2)
        self.gridlayoutG2.addWidget(self.figureG2_ntb)
        
        # widgets
        self.ColumnSelectUI = ColumnSelectUI()
        self.AnalROCUI = AnalROCUI()
        self.AnalTSAUI = AnalTSAUI()
        self.iTSAUI = AnaliTSAUI()
        self.PreprocessUI = PreprocessUI()
        self.NPTSAUI = NPTSAUI()
        
        # menu action
        self.actionProteomics.triggered.connect(self.LoadProteinFile)
        self.actionDatabase.triggered.connect(self.LoadProteinComplex)
        self.actionPreprocessing.triggered.connect(self.OpenPreprocessing)
        self.action_iTSA.triggered.connect(self.OpeniTSA)
        self.action_CETSA.triggered.connect(self.OpenAnalTSA)
        self.actionNPTSA.triggered.connect(self.OpenNPTSA)
        self.actionCalcROC.triggered.connect(self.OpenAnalROC)
        self.actionContact.triggered.connect(self.ContactMsg)
        self.actionSave.triggered.connect(self.SaveProject)
        self.actionOpen.triggered.connect(self.LoadProject)
        
        # button action
        self.ButtonGroup1.clicked.connect(self.SetProteinTable1)
        self.ButtonGroup2.clicked.connect(self.SetProteinTable2)
        self.ButtonClearFileList.clicked.connect(self.ClearProteinFile)
        self.ButtonDatabaseConfirm.clicked.connect(self.SetProteinComplex)
        self.ButtonDatabaseRemove.clicked.connect(self.RemoveProteinComplex)
        self.ButtonClearDatabase.clicked.connect(self.ClearProteinComplex)
        self.ButtonCalcComplex.clicked.connect(self.CalcProteinComplexChange)
        self.ButtonShowCurve.clicked.connect(self.PlotProteinComplex)
        self.ButtonSaveComp.clicked.connect(self.SaveProteinComplex)
        
        self.ColumnSelectUI.ButtonColumnSelect.clicked.connect(self.SetProteinColumn)
        self.ColumnSelectUI.ButtonColumnCancel.clicked.connect(self.ColumnSelectUI.close)
        
        self.AnalROCUI.pushButtonDatabase.clicked.connect(self.LoadProteinPair)
        self.AnalROCUI.pushButtonConfirm.clicked.connect(self.ShowAnalROC)
        self.AnalROCUI.pushButtonCancel.clicked.connect(self.AnalROCUI.close)
        self.AnalROCUI.pushButtonPval.clicked.connect(self.CalcProteinPairChange)
        self.AnalROCUI.pushButtonCurve.clicked.connect(self.PlotProteinPairCurve)
        
        self.NPTSAUI.ButtonConfirm.clicked.connect(self.ShowNPTSA)
        self.NPTSAUI.ButtonCancel.clicked.connect(self.NPTSAUI.close)
        self.NPTSAUI.ButtonShow.clicked.connect(self.ShowNPTSACurve)
        self.NPTSAUI.pushButtonSave.clicked.connect(self.SaveTSAData)
        
        self.AnalTSAUI.ButtonConfirm.clicked.connect(self.ShowAnalTSA)
        self.AnalTSAUI.ButtonCancel.clicked.connect(self.AnalTSAUI.close)
        self.AnalTSAUI.ButtonShow.clicked.connect(self.ShowTSACurve)
        self.AnalTSAUI.pushButtonSave.clicked.connect(self.SaveTSAData)
        
        # table sort
        self.tableProteinComplex.setSortingEnabled(True)
        
        # server data
        self.columns = None
        self.prots = None
        self.TSA_table = pd.DataFrame()
        self.resultDataComplex = []
        self.resultDataTSA = []
        self.resultDataROC = []
        self.resultProtPair = []
        self.ROCNegValues = []
    
    
    def SaveProject(self):
        pass
    
    
    def LoadProject(self):
        pass
    
    
    def ContactMsg(self):
        msg = QtWidgets.QMessageBox()
        msg.resize(550, 200)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('Author: \t Ji Hongchao- ji.hongchao@foxmail.com \t Tan Soon Heng- christan@sustech.edu.cn')
        msg.setWindowTitle("Contact")
        msg.exec_()        
    
    
    def WarnMsg(self, Text):
        msg = QtWidgets.QMessageBox()
        msg.resize(550, 200)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(Text)
        msg.setWindowTitle("Warning")
        msg.exec_()    
    
    
    def ErrorMsg(self, Text):
        msg = QtWidgets.QMessageBox()
        msg.resize(550, 200)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(Text)
        msg.setWindowTitle("Error")
        msg.exec_()
                
    
    def LoadProteinFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileNames, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Load", "","All Files (*);;CSV Files (*.csv)", options=options)
        
        if len(fileNames) == 0:
            pass
        
        else:
            for fileName in fileNames:
                if fileName:
                    if fileName.split('.')[1] in ['csv', 'xlsx']:
                        self.ListFile.addItem(fileName)
                    else:
                        pass


    def ClearProteinFile(self):
        self.ListFile.clear()
        
    
    def LoadProteinComplex(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Load", "","All Files (*);;CSV Files (*.csv)", options=options)
        if fileName:
            if fileName.split('.')[1] in ['csv', 'xlsx']:
                self.ListDatabase.addItem(fileName)
            else:
                self.ErrorMsg("Invalid format")
        else:
            pass
        
    
    def RemoveProteinComplex(self):
        self.ListDatabase.takeItem(self.ListDatabase.currentRow())
    
    
    def ClearProteinComplex(self):
        self.tableProteinComplex.setRowCount(0)
        self.ListDatabase.clear()
    
    
    def ReplaceNonNumeric(self, data):
        for col in data.columns[1:]:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        # data = data.astype(float)
        keep = np.logical_not(np.isnan(np.sum(np.array(data)[:,1:], axis = 1).astype(float)))
        data = data.iloc[keep,:]
        data = data.reset_index(drop = True)
        return data 
    
    
    def SelectProteinTable(self):
        selectItem = self.ListFile.currentItem()
        if not selectItem:
            self.ErrorMsg('No item is selected')
            return None
        try:
            if selectItem.text().split('.')[1] == 'csv':
                selectData = pd.read_csv(selectItem.text())
            elif selectItem.text().split('.')[1] == 'xlsx':
                selectData = pd.read_excel(selectItem.text())
            else:
                return None
        except:
            self.ErrorMsg('Cannot be load the selected file')
        
        if 'Accession' in selectData.columns:
            return selectData
        else:
            self.ErrorMsg('Accession is not given in the data')
            return None


    def SetProteinTable1(self):
        data = self.SelectProteinTable()
        if data is None:
            return None
        self.ColumnSelectUI.listWidget.clear()
        all_cols = data.columns
        for c in all_cols:
            self.ColumnSelectUI.listWidget.addItem(c)
        self.ColumnSelectUI.show()


    def SetProteinTable2(self):
        if self.columns == None:
            self.ErrorMsg('Please set Group 1')
        else:
            data = self.SelectProteinTable()
            if data is None:
                return None
            columns = ['Accession'] + self.columns
            try:
                data = data.loc[:, columns]
                data = self.ReplaceNonNumeric(data)
                if np.nanmax(data.loc[:, self.columns]) > 10:
                    self.WarnMsg('The data seems not normalized')
                self.tableProtein2.setModel(TableModel(data))
            except:
                self.ErrorMsg('No columns matched with Group 1')


    def SetProteinColumn(self):
        data = self.SelectProteinTable()
        self.columns = [i.text() for i in self.ColumnSelectUI.listWidget.selectedItems()]
        try:
            [float(t.replace('T', '')) for t in self.columns]
        except:
            self.columns = None
            self.ErrorMsg('Selected columns can only be Txx, where xx is a number representing temperature')
            return None
        columns = ['Accession'] + self.columns
        data = data.loc[:, columns]
        data = self.ReplaceNonNumeric(data)
        if np.nanmax(data.loc[:, self.columns] > 10):
            self.WarnMsg('The data seems not normalized')
        self.ColumnSelectUI.close()
        self.tableProtein1.setModel(TableModel(data))


    def FillProteinComplex(self, proteinComplex):
        self.tableProteinComplex.setRowCount(proteinComplex.shape[0])
        self.tableProteinComplex.setColumnCount(proteinComplex.shape[1])
        self.tableProteinComplex.setHorizontalHeaderLabels(proteinComplex.columns)
        self.tableProteinComplex.setVerticalHeaderLabels(proteinComplex.index.astype(str))
        for i in range(proteinComplex.shape[0]):
            for j in range(proteinComplex.shape[1]):
                if type(proteinComplex.iloc[i,j]) == np.float64:
                    item = QtWidgets.QTableWidgetItem()
                    item.setData(Qt.EditRole, QVariant(float(proteinComplex.iloc[i,j])))
                else:
                    item = QtWidgets.QTableWidgetItem(str(proteinComplex.iloc[i,j]))
                self.tableProteinComplex.setItem(i, j, item)        
     
     
    def TakeProteinComplex(self):
        ncol = self.tableProteinComplex.columnCount()
        nrow = self.tableProteinComplex.rowCount()
        header = [self.tableProteinComplex.horizontalHeaderItem(i).text() for i in range(ncol)]
        output = pd.DataFrame(np.zeros((nrow, ncol)))
        output.columns = header
        for i in range(nrow):
            for j in range(ncol):        
                v = self.tableProteinComplex.item(i, j).text()
                try:
                    v = float(v)
                except:
                    pass
                output.iloc[i,j] = v
        return output
     

    def SetProteinComplex(self):
        selectItem = self.ListDatabase.currentItem()
        try:
            if selectItem.text().split('.')[1] == 'csv':
                selectData = pd.read_csv(selectItem.text())
            elif selectItem.text().split('.')[1] == 'xlsx':
                selectData = pd.read_excel(selectItem.text())
            else:
                pass
        
            if 'Subunits_UniProt_IDs' not in selectData.columns:
                self.ErrorMsg("Subunits_UniProt_IDs' not in columns")
            else:
                self.FillProteinComplex(selectData)
        except:
            self.ErrorMsg("Cannot load the selected file")
        
    
    def CalcProteinComplexChange(self):
        self.resultDataComplex = []
        self.progressBar.setValue(0)
        self.ButtonCalcComplex.setEnabled(False)
        
        columns = self.columns
        proteinComplex = self.TakeProteinComplex()
        if len(proteinComplex) == 0:
            self.ErrorMsg('Not set protein complex')
        elif (self.tableProtein1.model() is None) or (self.tableProtein2.model() is None):
            self.ErrorMsg('Not set proteomics data')
        else:       
            proteinData1 = self.tableProtein1.model()._data
            proteinData2 = self.tableProtein2.model()._data

            data1 = proteinData1.loc[:, columns]
            data2 = proteinData2.loc[:, columns]
            dist1 = metrics.pairwise_distances(data1, metric = 'cityblock')
            dist2 = metrics.pairwise_distances(data2, metric = 'cityblock')
            prot1 = proteinData1.loc[:, 'Accession']
            prot2 = proteinData2.loc[:, 'Accession']

            self.ComplexThread = ComplexThread(prot1, dist1, prot2, dist2, proteinComplex)
            self.ComplexThread._ind.connect(self.ProcessBarComplex)
            self.ComplexThread._res.connect(self.ResultDataComplex)
            self.ComplexThread.start()
            self.ComplexThread.finished.connect(self.VisualizeComplex)


    def ResultDataComplex(self, msg):
        self.resultDataComplex.append(msg)
        

    def ProcessBarComplex(self, msg):
        self.progressBar.setValue(int(msg))
    
    
    def VisualizeComplex(self):
        proteinComplex = self.TakeProteinComplex()
        keep = [c for c in proteinComplex.columns 
                    if c not in ['Num subunit found', 'p-value (change)', 'Avg distance (change)', 'TPCA Sig 1', 'Avg distance 1', 'TPCA Sig 2', 'Avg distance 2']]
        proteinComplex = proteinComplex.loc[:,keep]
        
        resultDataComplex = pd.DataFrame(self.resultDataComplex)
        resultDataComplex.columns = ['Num subunit found', 'p-value (change)', 'Avg distance (change)', 'TPCA Sig 1', 'Avg distance 1', 'TPCA Sig 2', 'Avg distance 2']
        proteinComplex = pd.concat([proteinComplex, resultDataComplex], axis=1)
        proteinComplex = proteinComplex.sort_values(by = 'p-value (change)')
        proteinComplex = proteinComplex.reset_index(drop = True)
        self.FillProteinComplex(proteinComplex)
        self.ButtonCalcComplex.setEnabled(True)
        
    
    def PlotProteinComplex(self):
        colNames = self.columns
        header = [self.tableProteinComplex.horizontalHeaderItem(i).text() for i in range(self.tableProteinComplex.columnCount())]
        # print(header)
        try:
            i = self.tableProteinComplex.selectedIndexes()[0].row()
            j = list(header).index('Subunits_UniProt_IDs')
            proteinSubunit = self.tableProteinComplex.item(i, j).text()
        except:
            self.ErrorMsg('Can not plot protein curves')
            return None
        # print(proteinSubunit)
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data
        # print(proteinData)

        self.figureG1.ProteinComplexFigure(proteinSubunit, proteinData1, colNames)
        self.figureG2.ProteinComplexFigure(proteinSubunit, proteinData2, colNames)
    

    def SaveProteinComplex(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save", "","CSV Files (*.csv)", options=options)
        if fileName:
            data = self.TakeProteinComplex()
            data.to_csv(fileName)


    def LoadProteinPair(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Load", "","All Files (*);;CSV Files (*.csv)", options=options)
        if fileName:
            if fileName.split('.')[1] == 'csv':
                proteinPair = pd.read_csv(fileName)
                header = [c for c in proteinPair.columns if c in ['Protein A', 'Protein B', 'Publications']]
                proteinPair = proteinPair.loc[:, header]
                self.AnalROCUI.tableView.setModel(TableModel(proteinPair))
            elif fileName.split('.')[1] == 'xlsx':
                proteinPair = pd.read_excel(fileName)
                header = [c for c in proteinPair.columns if c in ['Protein A', 'Protein B', 'Publications']]
                proteinPair = proteinPair.loc[:, header]
                self.AnalROCUI.tableView.setModel(TableModel(proteinPair))
            else:
                self.ErrorMsg("Invalid format")
            self.AnalROCUI.spinBoxRandom.setProperty("value", len(proteinPair))
        
    
    def OpenAnalROC(self):
        self.AnalROCUI.show()
        self.AnalROCUI.progressBar.setValue(0)
        self.AnalROCUI.comboBoxDataset.clear()
        self.AnalROCUI.comboBoxDataset.addItems(['Group1', 'Group2'])
        self.AnalROCUI.comboBoxDistance.clear()
        self.AnalROCUI.comboBoxDistance.addItems(['manhattan', 'cityblock', 'cosine', 'euclidean', 'l1', 'l2'])

        if self.tableProtein1.model() is None or (self.tableProtein2.model() is None):
            self.ErrorMsg('Please set proteomics data')
            self.AnalROCUI.close()
        else:
            pass
        
    
    def ShowAnalROC(self):
        pub_thres = self.AnalROCUI.spinBoxPub.value()
        columns = self.columns
        
        self.resultDataROC = []
        if self.tableProtein1.model() is None or (self.tableProtein2.model() is None):
            self.ErrorMsg("Protein matrix is not available")
            self.AnalROCUI.close()
        else:
            proteinData1 = self.tableProtein1.model()._data
            proteinData2 = self.tableProtein2.model()._data
                
        if self.AnalROCUI.tableView.model() is None:
            self.ErrorMsg("Protein pairs is not available")
            self.AnalROCUI.close()
        
        else:
            if self.AnalROCUI.comboBoxDataset.currentText() == 'Group1':
                proteinData = proteinData1
            else:
                proteinData = proteinData2
            
            proteinPair = self.AnalROCUI.tableView.model()._data
            header = [c for c in proteinPair.columns if c in ['Protein A', 'Protein B', 'Publications']]
            proteinPair = proteinPair.loc[:, header]
            proteinPair = proteinPair.reset_index(drop = True)
                
            if ('Protein A' not in proteinPair.columns) or ('Protein B' not in proteinPair.columns):
                self.ErrorMsg("Protein pairs is not available")
            
            if 'Publications' in proteinPair.columns:
                proteinPair = proteinPair[proteinPair['Publications'] >= pub_thres]
            
            prot = proteinData.loc[:, 'Accession']
            data = proteinData.loc[:, columns]
            dist = metrics.pairwise_distances(data, metric = self.AnalROCUI.comboBoxDistance.currentText())
            neg_values = np.triu(dist, k = 0).flatten()
            neg_values = neg_values[neg_values > 0]
            
            self.ROCNegValues = np.array(np.random.choice(list(neg_values), self.AnalROCUI.spinBoxRandom.value(), replace=False))
            self.ROCThread = ROCThread(prot, data, dist, proteinPair)
            self.ROCThread._ind.connect(self.ProcessBarROC)
            self.ROCThread._res.connect(self.ResultDataROC)
            self.ROCThread.start()
            self.ROCThread.finished.connect(self.VisualizeROC)

    
    def VisualizeROC(self):
        pos_values = 1 - np.array(self.resultDataROC)
        neg_values = 1 - np.array(self.ROCNegValues)
        values = list(pos_values) + list(neg_values)
        labels = [1] * len(pos_values) + [0] * len(neg_values)
        
        fpr, tpr, threshold = metrics.roc_curve(labels, values, pos_label = 1)
        auroc = np.round(metrics.roc_auc_score(labels, values), 4)
        self.AnalROCUI.figureROC.ROCFigure(fpr, tpr, auroc)
        

    def PlotProteinPairCurve(self):
        columns = self.columns
        proteinPair = self.AnalROCUI.tableView.model()._data
        proteinPair = proteinPair.reset_index(drop = True)
        
        i = self.AnalROCUI.tableView.selectedIndexes()[0].row()
        p1 = proteinPair.loc[i, 'Protein A']
        p2 = proteinPair.loc[i, 'Protein B']
        
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data
        
        self.AnalROCUI.figureGroup1.ProteinPairFigure(p1, p2, proteinData1, columns)
        self.AnalROCUI.figureGroup2.ProteinPairFigure(p1, p2, proteinData2, columns)


    def ResultDataROC(self, msg):
        self.resultDataROC.append(msg)
        

    def ProcessBarROC(self, msg):
        self.AnalROCUI.progressBar.setValue(int(msg))
        
        
    def CalcProteinPairChange(self):
        self.resultProtPair = []
        self.AnalROCUI.progressBar.setValue(0)
        self.AnalROCUI.pushButtonPval.setEnabled(False)
        columns = self.columns
        pub_thres = self.AnalROCUI.spinBoxPub.value()
        
        if self.AnalROCUI.tableView.model() is None:
            self.ErrorMsg('Not set protein complex')
        elif (self.tableProtein1.model() is None) or (self.tableProtein2.model() is None):
            self.ErrorMsg('Not set proteomics data')
        else:      
            proteinData1 = self.tableProtein1.model()._data
            proteinData2 = self.tableProtein2.model()._data    
            proteinPair = self.AnalROCUI.tableView.model()._data
            
            header = [c for c in proteinPair.columns if c in ['Protein A', 'Protein B', 'Publications']]
            proteinPair = proteinPair.loc[:, header]
            proteinPair = proteinPair.reset_index(drop = True)
        
            if 'Publications' in proteinPair.columns:
                proteinPair = proteinPair[proteinPair['Publications'] >= pub_thres]
            data1 = proteinData1.loc[:, columns]
            data2 = proteinData2.loc[:, columns]
            dist1 = metrics.pairwise_distances(data1, metric = self.AnalROCUI.comboBoxDistance.currentText())
            dist2 = metrics.pairwise_distances(data2, metric = self.AnalROCUI.comboBoxDistance.currentText())
            prot1 = proteinData1.loc[:, 'Accession']
            prot2 = proteinData2.loc[:, 'Accession']
        
            n = self.AnalROCUI.spinBoxRandom.value()
            self.PairThread = PairThread(prot1, dist1, prot2, dist2, proteinPair, n)
            self.PairThread._ind.connect(self.ProcessBarROC)
            self.PairThread._res.connect(self.ResultProtPair)
            self.PairThread.start()
            self.PairThread.finished.connect(self.VisualizeProtPair)        


    def VisualizeProtPair(self):
        pub_thres = self.AnalROCUI.spinBoxPub.value()
        proteinPair = self.AnalROCUI.tableView.model()._data
        header = [c for c in proteinPair.columns if c in ['Protein A', 'Protein B', 'Publications']]
        proteinPair = proteinPair.loc[:, header]
        proteinPair = proteinPair.reset_index(drop = True)
        
        if 'Publications' in proteinPair.columns:
            proteinPair = proteinPair[proteinPair['Publications'] >= pub_thres]
        proteinPairDist = pd.DataFrame(self.resultProtPair)
        proteinPairDist.columns = ['Distance change', 'p-value', 'Distance Group1', 'Distance Group2']
        proteinPair = pd.concat([proteinPair, proteinPairDist], axis=1)
        proteinPair = proteinPair.sort_values(by = 'p-value')
        self.AnalROCUI.tableView.setModel(TableModel(proteinPair))
        self.AnalROCUI.pushButtonPval.setEnabled(True)
        

    def ResultProtPair(self, msg):
        self.resultProtPair.append(msg)

    
    def OpenPreprocessing(self):
        self.PreprocessUI.show()
        
        
    def OpeniTSA(self):
        self.iTSAUI.show()


    def OpenNPTSA(self):
        self.resultDataTSA = []
        self.NPTSAUI.progressBar.setValue(0)
        self.NPTSAUI.show()
        if self.tableProtein1.model() is None or (self.tableProtein2.model() is None):
            self.ErrorMsg('Please input proteomics data')
            self.NPTSAUI.close()
        else:
            self.NPTSAUI.tableWidgetProteinList.clear()
    
    
    def ShowNPTSA(self):
        columns = self.columns
        self.NPTSAUI.tableWidgetProteinList.clear()
        self.NPTSAUI.progressBar.setValue(0)
        self.NPTSAUI.ButtonConfirm.setEnabled(False)
        
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data
        
        temps = np.array([float(t.replace('T', '')) for t in columns])
        cols = ['Accession'] + columns
        data_1 = proteinData1.loc[:, cols]
        data_2 = proteinData2.loc[:, cols]

        self.prots = np.intersect1d(list(data_1.iloc[:,0]), list(data_2.iloc[:,0]))
        # print(len(self.prots))
        
        self.NPTSAThread = NPTSAThread(self.prots, temps, data_1, data_2, self.NPTSAUI.comboBox.currentText())
        self.NPTSAThread._ind.connect(self.ProcessBarNPTSA)
        self.NPTSAThread._res.connect(self.ResultDataTSA)
        self.NPTSAThread.start()
        self.NPTSAThread.finished.connect(self.VisualizeNPTSA)       


    def VisualizeNPTSA(self):
        method = self.NPTSAUI.comboBox.currentText()
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data
        
        prots = self.prots
        columns = self.columns
        
        res = pd.DataFrame(self.resultDataTSA)
        res.columns = ['Group1_R2', 'Group2_R2', 'D1', 'D2', 'delta_D', 'min_Slope']
        
        if method == 'fitness':
            [d1, d2, s0_sq] = list(estimate_df(res['D1'], res['delta_D']))
        else:
            s0_sq = 1
        delta_D = res['delta_D'] / s0_sq
        p_Val = []
        for i in range(len(res)):
            s = delta_D[i]
            pv = stats.t.sf(abs(s - np.nanmean(delta_D)) / np.nanstd(delta_D), len(delta_D)-1)
            p_Val.append(pv)
        score = -np.log10(np.array(p_Val)) * (res['Group1_R2'] * res['Group2_R2']) ** 2
    
        res['Accession'] = prots
        res['delta_Tm'] = delta_D
        res['p_Val (-log10)'] = -np.log10(p_Val)
        res['Score'] = score
        res = np.round(res, 3)
    
        res = res[['Accession', 'Score', 'p_Val (-log10)', 'delta_Tm', 'Group1_R2', 'Group2_R2', 'D1', 'D2', 'min_Slope']]
        TSA_table = res.sort_values(by = 'Score', axis = 0, ascending = False)
        
        self.resultDataTSA = []
        self.TSA_table = TSA_table
        self.NPTSAUI.ButtonConfirm.setEnabled(True)
        self.NPTSAUI.FillTable(TSA_table)
        self.NPTSAUI.figureAvg.AverageTSAFigure(proteinData1, proteinData2, columns)


    def ShowNPTSACurve(self):
        columns = self.columns
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data
        
        header = [self.NPTSAUI.tableWidgetProteinList.horizontalHeaderItem(i).text() for i in range(self.NPTSAUI.tableWidgetProteinList.columnCount())]
        i = self.NPTSAUI.tableWidgetProteinList.selectedItems()[0].row()
        j = header.index('Accession')
        ProteinAccession = self.NPTSAUI.tableWidgetProteinList.item(i, j).text()

        self.NPTSAUI.figureTSA.SingleTSAFigure(proteinData1, proteinData2, columns, ProteinAccession)


    def ProcessBarNPTSA(self, msg):
        self.NPTSAUI.progressBar.setValue(int(msg))

    
    def OpenAnalTSA(self):
        self.resultDataTSA = []
        self.AnalTSAUI.progressBar.setValue(0)
        self.AnalTSAUI.show()
        if self.tableProtein1.model() is None or (self.tableProtein2.model() is None):
            self.ErrorMsg('Please input proteomics data')
            self.AnalTSAUI.close()
        else:
            pass
    
    
    def ProcessBarTSA(self, msg):
        self.AnalTSAUI.progressBar.setValue(int(msg))
        
    
    def ResultDataTSA(self, msg):
        self.resultDataTSA.append(msg)
        # print(msg)
    
    
    def ShowAnalTSA(self):
        columns = self.columns
        self.ColumnSelectUI.close()
        self.AnalTSAUI.ButtonConfirm.setEnabled(False)
        self.AnalTSAUI.tableWidgetProteinList.clear()
        self.AnalTSAUI.progressBar.setValue(0)
        
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data

        h_axis = self.AnalTSAUI.Boxhaxis.value()
        minR2 = self.AnalTSAUI.BoxR2.value()
        maxPlateau = self.AnalTSAUI.BoxPlateau.value()
        
        temps = np.array([float(t.replace('T', '')) for t in columns])
        cols = ['Accession'] + columns
        data_1 = proteinData1.loc[:, cols]
        data_2 = proteinData2.loc[:, cols]

        self.prots = np.intersect1d(list(data_1.iloc[:,0]), list(data_2.iloc[:,0]))
        
        self.CurveFitThread = CurveFitThread(self.prots, temps, data_1, data_2, minR2, maxPlateau, h_axis)
        self.CurveFitThread._ind.connect(self.ProcessBarTSA)
        self.CurveFitThread._res.connect(self.ResultDataTSA)
        self.CurveFitThread.start()
        self.CurveFitThread.finished.connect(self.VisualizeTSA)
        
        '''
        res = []
        for i, p in enumerate(prots):
            x = temps
            y1 = np.array(data_1[data_1.iloc[:,0] == p].iloc[0,1:])
            y2 = np.array(data_2[data_2.iloc[:,0] == p].iloc[0,1:])
            res.append(fit_curve(x, y1, y2, minR2, maxPlateau, h_axis))
            self.AnalTSAUI.progressBar.setValue(int(i / len(prots)))
        '''
        # res = Parallel(n_jobs=n_core, backend = 'threading')(delayed(fit_curve)(p) for p in prots)
        # res = pd.DataFrame(res)
    
    
    def VisualizeTSA(self):
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data
        
        prots = self.prots
        columns = self.columns
        
        res = pd.DataFrame(self.resultDataTSA)
        res.columns = ['Group1_R2', 'Group2_R2', 'Group1_Tm', 'Group2_Tm', 'delta_Tm', 'min_Slope']
    
        delta_Tm = res['delta_Tm']
        p_Val = []
        for i in range(len(res)):
            s = delta_Tm[i]
            pv = stats.t.sf(abs(s - np.nanmean(delta_Tm)) / np.nanstd(delta_Tm), len(delta_Tm)-1)
            p_Val.append(pv)
        score = -np.log10(np.array(p_Val)) * (res['Group1_R2'] * res['Group2_R2']) ** 2
    
        res['Accession'] = prots
        res['delta_Tm'] = delta_Tm
        res['p_Val (-log10)'] = -np.log10(p_Val)
        res['Score'] = score
        res = np.round(res, 3)
    
        res = res[['Accession', 'Score', 'p_Val (-log10)', 'delta_Tm', 'Group1_R2', 'Group2_R2', 'Group1_Tm', 'Group2_Tm', 'min_Slope']]
        TSA_table = res.sort_values(by = 'Score', axis = 0, ascending = False)
        
        self.resultDataTSA = []
        self.TSA_table = TSA_table
        self.AnalTSAUI.ButtonConfirm.setEnabled(True)
        self.AnalTSAUI.FillTable(TSA_table)
        self.AnalTSAUI.figureAvg.AverageTSAFigure(proteinData1, proteinData2, columns)

    
    def ShowTSACurve(self):
        columns = self.columns
        proteinData1 = self.tableProtein1.model()._data
        proteinData2 = self.tableProtein2.model()._data
        
        header = [self.AnalTSAUI.tableWidgetProteinList.horizontalHeaderItem(i).text() for i in range(self.AnalTSAUI.tableWidgetProteinList.columnCount())]
        i = self.AnalTSAUI.tableWidgetProteinList.selectedItems()[0].row()
        j = header.index('Accession')
        ProteinAccession = self.AnalTSAUI.tableWidgetProteinList.item(i, j).text()

        self.AnalTSAUI.figureTSA.SingleTSAFigure(proteinData1, proteinData2, columns, ProteinAccession)
        

    def SaveTSAData(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save", "","CSV Files (*.csv)", options=options)
        if fileName:
            data = self.TSA_table
            data.to_csv(fileName)
    

if __name__ == '__main__':
    
    import sys
    app = QApplication(sys.argv)
    ui = TCPA_Main()
    ui.show()
    sys.exit(app.exec_())
    