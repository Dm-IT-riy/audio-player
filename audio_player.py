import sys
from os.path import expanduser
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
	
		self.currentPlaylist = QMediaPlaylist()
		self.player = QMediaPlayer()
		self.userAction = -1			#0-stopped, 1-playing 2-paused
		self.player.currentMediaChanged.connect(self.row_changed)
		self.player.positionChanged.connect(self.position_changed)
		self.player.stateChanged.connect(self.qmp_stateChanged)
		self.player.durationChanged.connect(self.duration_changed)
		self.player.setVolume(0)

		#Add Status bar
		self.statusBar().showMessage('No Media')
		self.homeScreen()
		
	def homeScreen(self):
		#Set title of the MainWindow
		self.setWindowTitle('Music Player')
		self.setWindowIcon(QIcon('icons/main.png'))
		
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
		filemenu.addAction(self.filesOpen())
		filemenu.addAction(self.folderOpen())
		filemenu.addAction(self.save_playlist())
		filemenu.addAction(self.load_playlist())
		menubar.addAction(self.info())
	
	def addControls(self):
		controlArea = QVBoxLayout()		 #centralWidget
		time_sliderLayout = QHBoxLayout()
		seekVolumeLayout = QHBoxLayout() #volume slider
		controls = QHBoxLayout()
		playlistCtrlLayout = QHBoxLayout()
		playlistLayout = QVBoxLayout()
		playlistControls = QHBoxLayout()
		
		#creating buttons
		playBtn = QPushButton()
		playBtn.setIcon(QIcon('icons/play.png'))
		pauseBtn = QPushButton()
		pauseBtn.setIcon(QIcon('icons/pause.png'))
		stopBtn = QPushButton()
		stopBtn.setIcon(QIcon('icons/stop.png'))
		
		#creating play controls
		prevBtn = QPushButton()
		prevBtn.setIcon(QIcon('icons/prev.png'))
		nextBtn = QPushButton()
		nextBtn.setIcon(QIcon('icons/next.png'))

		#creating playlist controls
		addBtn = QPushButton('Add Files')
		addBtn.setIcon(QIcon('icons/add-list.png'))
		delBtn = QPushButton('Remove')
		delBtn.setIcon(QIcon('icons/bin.png'))
		self.playModeBtn = QPushButton('Play Mode')
		self.playModeBtn.setIcon(QIcon('icons/loop_off.png'))

		# creating time progress widgets
		self.currentTimeLabel = QLabel()
		self.currentTimeLabel.setMinimumSize(50, 0)
		self.currentTimeLabel.setAlignment(Qt.AlignCenter)
		self.currentTimeLabel.setText(hhmmss(0))

		self.time_slider = QSlider(Qt.Horizontal)
		self.time_slider.setRange(0, 0)
		self.time_slider.sliderMoved.connect(self.set_position)

		self.totalTimeLabel = QLabel()
		self.totalTimeLabel.setMinimumSize(50, 0)
		self.totalTimeLabel.setAlignment(Qt.AlignCenter)
		self.totalTimeLabel.setText(hhmmss(0))

		time_sliderLayout.addWidget(self.currentTimeLabel)
		time_sliderLayout.addWidget(self.time_slider)
		time_sliderLayout.addWidget(self.totalTimeLabel)

		#creating volume slider
		volumeSlider = QSlider()
		volumeSlider.setMinimum(0)
		volumeSlider.setMaximum(100)
		volumeSlider.setOrientation(Qt.Horizontal)
		volumeSlider.setTracking(False)
		volumeSlider.sliderMoved.connect(self.volumePosition)

		seekVolumeLabel1 = QLabel()
		seekVolumeLabel1.setMinimumSize(50, 0)
		seekVolumeLabel1.setAlignment(Qt.AlignCenter)
		seekVolumeLabel1.setPixmap(QPixmap('icons/volume_off.png'))
		seekVolumeLabel2 = QLabel()
		seekVolumeLabel2.setMinimumSize(50, 0)
		seekVolumeLabel2.setAlignment(Qt.AlignCenter)
		seekVolumeLabel2.setPixmap(QPixmap('icons/volume.png'))
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
		
		#play control button handlers
		prevBtn.clicked.connect(self.prevItemPlaylist)
		nextBtn.clicked.connect(self.nextItemPlaylist)
		playlistCtrlLayout.addWidget(prevBtn)
		playlistCtrlLayout.addWidget(nextBtn)

		#playlist widget
		self.listWidget = QListWidget()
		self.listWidget.itemDoubleClicked.connect(self.playlistHandler)
		self.listWidget.setStyleSheet('min-height: 200px;')
		playlistLayout.addWidget(self.listWidget)

		#playlist control button handlers
		addBtn.clicked.connect(self.openFiles)
		delBtn.clicked.connect(self.delFile)
		self.playModeBtn.clicked.connect(self.playback_mode)
		playlistControls.addWidget(addBtn)
		playlistControls.addWidget(delBtn)
		playlistControls.addWidget(self.playModeBtn)
		
		#Adding to the vertical layout
		controlArea.addLayout(time_sliderLayout)
		controlArea.addLayout(seekVolumeLayout)
		controlArea.addLayout(controls)
		controlArea.addLayout(playlistCtrlLayout)
		controlArea.addLayout(playlistLayout)
		controlArea.addLayout(playlistControls)
		return controlArea
	
	def playHandler(self):
		self.userAction = 1
		self.statusBar().showMessage('Playing')
		if self.player.state() == QMediaPlayer.StoppedState :
			if self.player.mediaStatus() == QMediaPlayer.NoMedia:
				if self.currentPlaylist.mediaCount() == 0:
					self.openFiles()
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
			
	def qmp_stateChanged(self):
		if self.player.state() == QMediaPlayer.StoppedState:
			self.player.stop()

	def position_changed(self, position):
		self.time_slider.blockSignals(True)
		self.time_slider.setValue(position)
		self.time_slider.blockSignals(False)
		if position >= 0:
			self.currentTimeLabel.setText(hhmmss(position))

	def duration_changed(self, duration):
		self.time_slider.setRange(0, duration)
		if duration >= 0:
			self.totalTimeLabel.setText(hhmmss(duration))

	def set_position(self, position):
		self.player.setPosition(position)

	def volumePosition(self, position):
		sender = self.sender()
		if isinstance(sender,QSlider):
			if self.player.isSeekable():
				self.player.setVolume(position)
		
	def increaseVolume(self):
		vol = self.player.volume()
		vol = min(vol+1, 100)
		self.player.setVolume(vol)
		
	def decreaseVolume(self):
		vol = self.player.volume()
		vol = max(vol-1, 0)
		self.player.setVolume(vol)
	
	def filesOpen(self):
		fileAc = QAction('Open Files',self)
		fileAc.setShortcut('Ctrl+O')
		fileAc.setStatusTip('Open Files')
		fileAc.triggered.connect(self.openFiles)
		return fileAc

	def openFiles(self):
		filesChoosen = QFileDialog.getOpenFileUrls(self, 'Open Music File', QUrl().fromLocalFile(expanduser('~')), 'Audio (*.mp3 *.ogg *.wav)')
		for file in filesChoosen[0]:
			self.currentPlaylist.addMedia(QMediaContent(file))
			self.listWidget.addItem(file.fileName())
	
	def folderOpen(self):
		folderAc = QAction('Open Folder',self)
		folderAc.setShortcut('Ctrl+D')
		folderAc.setStatusTip('Open Folder (Will add all the files in the folder) ')
		folderAc.triggered.connect(self.addFiles)
		return folderAc

	def load_playlist(self):
		playlistAc = QAction('Load Playlist', self)
		playlistAc.setShortcut('Ctrl+L')
		playlistAc.setStatusTip('Load Playlist')
		playlistAc.triggered.connect(self.playlist_action_load)
		return playlistAc

	def save_playlist(self):
		playlistAc = QAction('Save Playlist', self)
		playlistAc.setShortcut('Ctrl+S')
		playlistAc.setStatusTip('Save Playlist')
		playlistAc.triggered.connect(self.playlist_action_save)
		return playlistAc

	def playlist_action_save(self):
		filesChoosen = QFileDialog.getOpenFileUrl(self, 'Choose Save File', QUrl().fromLocalFile(expanduser('~')))
		self.currentPlaylist.save(filesChoosen[0], 'm3u8')

	def playlist_action_load(self):
		fileChoosen = QFileDialog.getOpenFileUrl(self, 'Choose Save File', QUrl().fromLocalFile(expanduser('~')), '*.m3u8')
		if fileChoosen[0].toLocalFile() != '':
			self.currentPlaylist.clear()
			self.listWidget.clear()
			self.currentPlaylist.load(fileChoosen[0], 'm3u8')
			for row in range(self.currentPlaylist.mediaCount()):
				item = self.currentPlaylist.media(row).canonicalUrl().fileName()
				self.listWidget.addItem(item)

	def addFiles(self):
		folderChoosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', expanduser('~'))
		it = QDirIterator(folderChoosen)
		it.next()
		while it.hasNext():
			if it.fileInfo().isDir() == False and it.filePath() != '.':
				fInfo = it.fileInfo()
				if fInfo.suffix() in ('mp3','ogg','wav'):
					self.listWidget.addItem(fInfo.fileName())
					self.currentPlaylist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
			it.next()

	def delFile(self):
		index = self.listWidget.currentIndex().row()
		self.listWidget.takeItem(index)
		self.currentPlaylist.removeMedia(index)

	def playback_mode(self):
		if self.currentPlaylist.playbackMode() == QMediaPlaylist.Sequential:
			self.currentPlaylist.setPlaybackMode(QMediaPlaylist.Loop)
			self.playModeBtn.setIcon(QIcon("icons/loop_on.png"))

		elif self.currentPlaylist.playbackMode() == QMediaPlaylist.Loop:
			self.currentPlaylist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
			self.playModeBtn.setIcon(QIcon('icons/item_loop.png'))

		elif self.currentPlaylist.playbackMode() == QMediaPlaylist.CurrentItemInLoop:
			self.currentPlaylist.setPlaybackMode(QMediaPlaylist.Random)
			self.playModeBtn.setIcon(QIcon('icons/shuffle.png'))

		elif self.currentPlaylist.playbackMode() == QMediaPlaylist.Random:
			self.currentPlaylist.setPlaybackMode(QMediaPlaylist.Sequential)
			self.playModeBtn.setIcon(QIcon('icons/loop_off.png'))

	def playlistHandler(self):
		index = self.listWidget.currentIndex().row()
		self.currentPlaylist.setCurrentIndex(index)
	
	def row_changed(self):
		index = self.currentPlaylist.currentIndex()
		self.listWidget.setCurrentRow(index)
			
	def info(self):
		infoAc = QAction('Info', self)
		infoAc.setShortcut('F1')
		infoAc.setStatusTip('Help (F1)')
		infoAc.triggered.connect(self.displayHelp)
		return infoAc
	
	def displayHelp(self):
		fullText = '''Select audio: button 'Add Files' or 'Ctrl+O'<br>
					  Select folder: menu 'File' or 'Ctrl+D'
					  <hr>Author: Dima Sakovski'''
		infoBox = QMessageBox(self)
		infoBox.setWindowTitle('Help')
		infoBox.setText(fullText)
		infoBox.addButton('OK',QMessageBox.AcceptRole)
		infoBox.show()
	
	def prevItemPlaylist(self):
		try:
			self.player.playlist().previous()
		except:
			self.displayHelp()

	def nextItemPlaylist(self):
		try:
			self.player.playlist().next()
		except:
			self.displayHelp()
	
	def closeEvent(self, *args):
		qApp.quit()

# convert from milliseconds to hh:mm:ss
def hhmmss(ms):
    s = round(ms / 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return (f'{h}:{m}:{s}') if h else (f'{m}:{s}')			
	
if __name__ == '__main__':
	app = QApplication(sys.argv)
	exit = MainWindow()
	sys.exit(app.exec_())