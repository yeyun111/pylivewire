"""
A crappy GUI for intelligent scissors/livewire with 
# Left click to set seed
# Right click to finish
# Mid click to export image file
"""

from __future__ import division
import time
import cv2
from PyQt4 import QtGui, QtCore
from threading import Thread
from livewire import Livewire

class ImageWin(QtGui.QWidget):
    def __init__(self):
        super(ImageWin, self).__init__()
        self.setupUi()
        self.active = False
        self.seed_enabled = True
        self.seed = None
        self.path_map = {}
        self.path = []
        
    def setupUi(self):
        self.hbox = QtGui.QVBoxLayout(self)
        
        # Load and initialize image
        self.image_path = ''
        while self.image_path == '':
            self.image_path = QtGui.QFileDialog.getOpenFileName(self, '', '', '(*.bmp *.jpg *.png)')
        self.image = QtGui.QPixmap(self.image_path)
        self.cv2_image = cv2.imread(str(self.image_path))
        self.lw = Livewire(self.cv2_image)
        self.w, self.h = self.image.width(), self.image.height()
        
        self.canvas = QtGui.QLabel(self)
        self.canvas.setMouseTracking(True)
        self.canvas.setPixmap(self.image)
        
        self.status_bar = QtGui.QStatusBar(self)
        self.status_bar.showMessage('Left click to set a seed')
        
        self.hbox.addWidget(self.canvas)
        self.hbox.addWidget(self.status_bar)
        self.setLayout(self.hbox)
    
    def mousePressEvent(self, event):            
        if self.seed_enabled:
            pos = event.pos()
            x, y = pos.x()-self.canvas.x(), pos.y()-self.canvas.y()
            
            if x < 0:
                x = 0
            if x >= self.w:
                x = self.w - 1
            if y < 0:
                y = 0
            if y >= self.h:
                y = self.h - 1

            # Get the mouse cursor position
            p = y, x
            seed = self.seed
            
            # Export bitmap
            if event.buttons() == QtCore.Qt.MidButton:
                filepath = QtGui.QFileDialog.getSaveFileName(self, 'Save image audio to', '', '*.bmp\n*.jpg\n*.png')
                image = self.image.copy()
                
                draw = QtGui.QPainter()
                draw.begin(image)
                draw.setPen(QtCore.Qt.blue)
                if self.path_map:
                    while p != seed:
                        draw.drawPoint(p[1], p[0])
                        for q in self.lw._get_neighbors(p):
                            draw.drawPoint(q[1], q[0])
                        p = self.path_map[p]
                if self.path:
                    draw.setPen(QtCore.Qt.green)
                    for p in self.path:
                        draw.drawPoint(p[1], p[0])
                        for q in self.lw._get_neighbors(p):
                            draw.drawPoint(q[1], q[0])
                draw.end()
                
                image.save(filepath, quality=100)
            
            else:
                self.seed = p
                
                if self.path_map:
                    while p != seed:
                        p = self.path_map[p]
                        self.path.append(p)
                
                # Calculate path map
                if event.buttons() == QtCore.Qt.LeftButton:
                    Thread(target=self._cal_path_matrix).start()
                    Thread(target=self._update_path_map_progress).start()
                
                # Finish current task and reset
                elif event.buttons() == QtCore.Qt.RightButton:
                    self.path_map = {}
                    self.status_bar.showMessage('Left click to set a seed')
                    self.active = False
    
    def mouseMoveEvent(self, event):
        if self.active and event.buttons() == QtCore.Qt.NoButton:
            pos = event.pos()
            x, y = pos.x()-self.canvas.x(), pos.y()-self.canvas.y()

            if x < 0 or x >= self.w or y < 0 or y >= self.h:
                pass
            else:
                # Draw livewire
                p = y, x
                path = []
                while p != self.seed:
                    p = self.path_map[p]
                    path.append(p)
                
                image = self.image.copy()
                draw = QtGui.QPainter()
                draw.begin(image)
                draw.setPen(QtCore.Qt.blue)
                for p in path:
                    draw.drawPoint(p[1], p[0])
                if self.path:
                    draw.setPen(QtCore.Qt.green)
                    for p in self.path:
                        draw.drawPoint(p[1], p[0])
                draw.end()
                self.canvas.setPixmap(image)
    
    def _cal_path_matrix(self):
        self.seed_enabled = False
        self.active = False
        self.status_bar.showMessage('Calculating path map...')
        path_matrix = self.lw.get_path_matrix(self.seed)
        self.status_bar.showMessage(r'Left: new seed / Right: finish')
        self.seed_enabled = True
        self.active = True
        
        self.path_map = path_matrix
    
    def _update_path_map_progress(self):
        while not self.seed_enabled:
            time.sleep(0.1)
            message = 'Calculating path map... {:.1f}%'.format(self.lw.n_processed/self.lw.n_pixs*100.0)
            self.status_bar.showMessage(message)
        self.status_bar.showMessage(r'Left: new seed / Right: finish')
