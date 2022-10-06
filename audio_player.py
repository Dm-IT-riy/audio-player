import sys
from os.path import expanduser
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
	
		self.currentPlaylist = QMediaPlaylist()
		self.player = QMediaPlayer()
		self.userAction = -1			#0-stopped, 1-playing 2-paused
		self.player.mediaStatusChanged.connect(self.qmp_mediaStatusChanged)
		self.player.stateChanged.connect(self.qmp_stateChanged)
		self.player.positionChanged.connect(self.qmp_positionChanged)
		self.player.positionChanged.connect(self.qmp_volumeChanged)
		self.player.setVolume(0)

		#Add Status bar
		self.statusBar().showMessage('No Media')
		self.homeScreen()
		
	def homeScreen(self):
		#Set title of the MainWindow
		self.setWindowTitle('Music Player')
		
		#Create Menubar
		self.createMenubar()
		
		#Add Control Bar
		controlBar = self.addControls()

		#need to add both infoscreen and control bar to the central widget.
		centralWidget = QWidget()
		centralWidget.setLayout(controlBar)
		self.setCentralWidget(centralWidget)
		
		#Set Dimensions of the MainWindow
		self.resize(500, 150)
		
		#show everything
		self.show()
		
	def createMenubar(self):
		menubar = self.menuBar()
		filemenu = menubar.addMenu('File')
		filemenu.addAction(self.fileOpen())
		filemenu.addAction(self.folderOpen())
		menubar.addAction(self.info())
	
	def addControls(self):
		controlArea = QVBoxLayout()		 #centralWidget
		seekSliderLayout = QHBoxLayout()
		seekVolumeLayout = QHBoxLayout() #volume slider
		controls = QHBoxLayout()
		playlistCtrlLayout = QHBoxLayout()
		playlistLayout = QVBoxLayout()
		
		#creating buttons
		playBtn = QPushButton('Play')		#play button
		pauseBtn = QPushButton('Pause')		#pause button
		stopBtn = QPushButton('Stop')		#stop button
		
		#creating playlist controls
		prevBtn = QPushButton('Prev Song')
		nextBtn = QPushButton('Next Song')
		
		#creating seek slider
		seekSlider = QSlider()
		seekSlider.setMinimum(0)
		seekSlider.setMaximum(100)
		seekSlider.setOrientation(Qt.Horizontal)
		seekSlider.setTracking(False)
		seekSlider.sliderMoved.connect(self.seekPosition)
		
		seekSliderLabel1 = QLabel('0.00')
		seekSliderLabel2 = QLabel('0.00')
		seekSliderLayout.addWidget(seekSliderLabel1)
		seekSliderLayout.addWidget(seekSlider)
		seekSliderLayout.addWidget(seekSliderLabel2)

		#creating volume slider
		volumeSlider = QSlider()
		volumeSlider.setMinimum(0)
		volumeSlider.setMaximum(100)
		volumeSlider.setOrientation(Qt.Horizontal)
		volumeSlider.setTracking(False)
		volumeSlider.sliderMoved.connect(self.volumePosition)

		seekVolumeLabel1 = QLabel('0')
		seekVolumeLabel2 = QLabel('100')
		seekVolumeLayout.addWidget(seekVolumeLabel1)
		seekVolumeLayout.addWidget(volumeSlider)
		seekVolumeLayout.addWidget(seekVolumeLabel2)		
		
		#Add handler for each button. Not using the default slots.
		playBtn.clicked.connect(self.playHandler)
		pauseBtn.clicked.connect(self.pauseHandler)
		stopBtn.clicked.connect(self.stopHandler)
		
		#Adding to the horizontal layout
		controls.addWidget(playBtn)
		controls.addWidget(pauseBtn)
		controls.addWidget(stopBtn)
		
		#playlist control button handlers
		prevBtn.clicked.connect(self.prevItemPlaylist)
		nextBtn.clicked.connect(self.nextItemPlaylist)
		playlistCtrlLayout.addWidget(prevBtn)
		playlistCtrlLayout.addWidget(nextBtn)

		#playlist widget
		self.listWidget = QListWidget()
		self.listWidget.itemClicked.connect(self.playlistHandler)
		playlistLayout.addWidget(self.listWidget)
		
		#Adding to the vertical layout
		controlArea.addLayout(seekSliderLayout)
		controlArea.addLayout(seekVolumeLayout)
		controlArea.addLayout(controls)
		controlArea.addLayout(playlistCtrlLayout)
		controlArea.addLayout(playlistLayout)
		return controlArea
	
	def playHandler(self):
		self.userAction = 1
		self.statusBar().showMessage('Playing')
		if self.player.state() == QMediaPlayer.StoppedState :
			if self.player.mediaStatus() == QMediaPlayer.NoMedia:
				print(self.currentPlaylist.mediaCount())
				if self.currentPlaylist.mediaCount() == 0:
					self.openFile()
				if self.currentPlaylist.mediaCount() != 0:
					self.player.setPlaylist(self.currentPlaylist)
			elif self.player.mediaStatus() == QMediaPlayer.LoadedMedia:
				self.player.play()
			elif self.player.mediaStatus() == QMediaPlayer.BufferedMedia:
				self.player.play()
		elif self.player.state() == QMediaPlayer.PlayingState:
			pass
		elif self.player.state() == QMediaPlayer.PausedState:
			self.player.play()
			
	def pauseHandler(self):
		self.userAction = 2
		self.statusBar().showMessage(f"Paused '{self.player.metaData(QMediaMetaData.Title)}' at position {self.centralWidget().layout().itemAt(0).layout().itemAt(0).widget().text()}")
		self.player.pause()
			
	def stopHandler(self):
		self.userAction = 0
		self.statusBar().showMessage(f"Stopped '{self.player.metaData(QMediaMetaData.Title)}'")
		if self.player.state() == QMediaPlayer.PlayingState:
			self.stopState = True
			self.player.stop()
		elif self.player.state() == QMediaPlayer.PausedState:
			self.player.stop()
		elif self.player.state() == QMediaPlayer.StoppedState:
			pass
		
	def qmp_mediaStatusChanged(self):
		if self.player.mediaStatus() == QMediaPlayer.LoadedMedia and self.userAction == 1:
			durationT = self.player.duration()
			self.centralWidget().layout().itemAt(0).layout().itemAt(1).widget().setRange(0,durationT)
			self.centralWidget().layout().itemAt(0).layout().itemAt(2).widget().setText(f'{int(durationT/60000)}:{int((durationT/1000)%60)}')
			self.player.play()
			
	def qmp_stateChanged(self):
		if self.player.state() == QMediaPlayer.StoppedState:
			self.player.stop()
	
	def qmp_positionChanged(self, position,senderType=False):
		sliderLayout = self.centralWidget().layout().itemAt(0).layout()
		if senderType == False:
			sliderLayout.itemAt(1).widget().setValue(position)
		#update the text label
		sliderLayout.itemAt(0).widget().setText(f'{int(position/60000)}:{int((position/1000)%60)}')
	
	def seekPosition(self, position):
		sender = self.sender()
		if isinstance(sender,QSlider):
			if self.player.isSeekable():
				self.player.setPosition(position)

	def volumePosition(self, position):
		sender = self.sender()
		if isinstance(sender,QSlider):
			if self.player.isSeekable():
				self.player.setVolume(position)
			
	def qmp_volumeChanged(self):
		sliderLayout = self.centralWidget().layout().itemAt(1).layout()
		volume = str(self.player.volume())
		sliderLayout.itemAt(0).widget().setText(volume)
		
	def increaseVolume(self):
		vol = self.player.volume()
		vol = min(vol+1, 100)
		self.player.setVolume(vol)
		
	def decreaseVolume(self):
		vol = self.player.volume()
		vol = max(vol-1, 0)
		self.player.setVolume(vol)
	
	def fileOpen(self):
		fileAc = QAction('Open File',self)
		fileAc.setShortcut('Ctrl+O')
		fileAc.setStatusTip('Open File')
		fileAc.triggered.connect(self.openFile)
		return fileAc
		
	def openFile(self):
		fileChoosen = QFileDialog.getOpenFileUrl(self, 'Open Music File', QUrl(expanduser('~')), 'Audio (*.mp3 *.ogg *.wav)')
		if fileChoosen != None:
			self.currentPlaylist.addMedia(QMediaContent(fileChoosen[0]))
			self.listWidget.addItem(fileChoosen[0].fileName())
	
	def folderOpen(self):
		folderAc = QAction('Open Folder',self)
		folderAc.setShortcut('Ctrl+D')
		folderAc.setStatusTip('Open Folder (Will add all the files in the folder) ')
		folderAc.triggered.connect(self.addFiles)
		return folderAc

	def addFiles(self):
		folderChoosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', expanduser('~'))
		if folderChoosen != None:
			it = QDirIterator(folderChoosen)
			it.next()
			while it.hasNext():
				if it.fileInfo().isDir() == False and it.filePath() != '.':
					fInfo = it.fileInfo()
					print(it.filePath(),fInfo.suffix())
					if fInfo.suffix() in ('mp3','ogg','wav'):
						print('added file ',fInfo.fileName())
						self.listWidget.addItem(fInfo.fileName())
						self.currentPlaylist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
				it.next()

	def playlistHandler(self):
		index = self.listWidget.currentIndex().row()
		self.currentPlaylist.setCurrentIndex(index)
			
	def info(self):
		infoAc = QAction('Info', self)
		infoAc.setShortcut('Ctrl+I')
		infoAc.setStatusTip('Help (Ctrl+I)')
		infoAc.triggered.connect(self.displayHelp)
		return infoAc
	
	def displayHelp(self):
		fullText = '''Select audio: menu 'File' or 'Ctrl+O'<br>
					  Select folder: menu 'File' or 'Ctrl+D'
					  <hr>Author: Dima Sakovski'''
		infoBox = QMessageBox(self)
		infoBox.setWindowTitle('Help')
		infoBox.setText(fullText)
		infoBox.addButton('OK',QMessageBox.AcceptRole)
		infoBox.show()
	
	def prevItemPlaylist(self):
		self.player.playlist().previous()
	
	def nextItemPlaylist(self):
		self.player.playlist().next()
	
	def closeEvent(self, *args):
		qApp.quit()
			
	
if __name__ == '__main__':
	app = QApplication(sys.argv)
	exit = MainWindow()
	sys.exit(app.exec_())