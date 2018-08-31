# Adds custom spreadsheet columns and right-click menu for setting the Shot Status, and Artist Shot Assignement.
import hiero.core
import hiero.ui
from PySide2 import (QtCore, QtWidgets, QtGui)

# Set to True, if you wat 'Set Status' right-click menu, False if not
kAddStatusMenu = True

# Set to True, if you wat 'Assign Artist' right-click menu, False if not
kAssignArtistMenu = True

# The Custom Spreadsheet Columns
class CustomSpreadsheetColumns(QtCore.QObject):
  """
    A class defining custom columns for Spreadsheet view. This has a similar, but
    slightly simplified, interface to the QAbstractItemModel and QItemDelegate classes.
  """
  global gStatusTags
  global gArtistList


  currentView = hiero.ui.activeView()

  # This is the list of Columns available
  gCustomColumnList = [
    { 'name' : 'Tags', 'cellType' : 'readonly'},
    { 'name' : 'Notes', 'cellType' : 'readonly' },
    { 'name' : 'Bid', 'cellType' : 'dropdown' },
    { 'name' : 'Artist', 'cellType' : 'dropdown' },
    { 'name' : 'Department', 'cellType' : 'readonly' },        
  ]

  def numColumns(self):
    """
      Return the number of custom columns in the spreadsheet view
    """
    return len( self.gCustomColumnList )

  def columnName(self, column):
    """
      Return the name of a custom column
    """
    return self.gCustomColumnList[column]['name']

  def getTagsString(self,item):
    """
      Convenience method for returning all the Notes in a Tag as a string
    """    
    tagNames = []
    tags = item.tags()
    for tag in tags:
      tagNames+=[tag.name()]
    tagNameString = ','.join(tagNames)
    return tagNameString

  def getNotes(self,item):
    """
      Convenience method for returning all the Notes in a Tag as a string
    """        
    notes = ''
    tags = item.tags()
    for tag in tags:
      note = tag.note()
      if len(note)>0:
        notes+=tag.note()+', '
    return notes[:-2]
    
  def getData(self, row, column, item):
    """
      Return the data in a cell
    """
    currentColumn = self.gCustomColumnList[column]
    if currentColumn['name'] == 'Tags':
      return self.getTagsString(item)


    if currentColumn['name'] == 'Notes':
      try:
        note = self.getNotes(item)
      except:
        note = ''
      return note

    if currentColumn['name'] == 'Bid':
      status = item.status()
      if not status:
        status = "--"
      return str(status)                            

    if currentColumn['name'] == 'Artist':
      if item.artist():
        name = item.artist()['artistName']
        return name
      else:
        return '--'

    if currentColumn['name'] == 'Department':
      if item.artist():
        dep = item.artist()['artistDepartment']
        return dep
      else:
        return '--'    

    return ""

  def getTooltip(self, row, column, item):
    """
      Return the tooltip for a cell
    """
    currentColumn = self.gCustomColumnList[column]
    if currentColumn['name'] == 'Tags':
      return str([item.name() for item in item.tags()])

    if currentColumn['name'] == 'Notes':
      return str(self.getNotes(item))
    return ""

  def getBackground(self, row, column, item):
    """
      Return the background colour for a cell
    """
    if not item.source().mediaSource().isMediaPresent():
      return QtGui.QColor(80, 20, 20)
    return None

  def getForeground(self, row, column, item):
    """
      Return the foreground colour for a cell
    """
    return None
  
  def getFont(self, row, column, item):
    """
      Return the font for a cell
    """
    return None

  def setData(self, row, column, item, data):
    """
      Set the data in a cell - unused in this example
    """
    
    return None

  def getIcon(self, row, column, item):
    """
      Return the icon for a cell
    """
    currentColumn = self.gCustomColumnList[column]

    
    if currentColumn['name'] == 'Artist':
      try:
        return QtGui.QIcon(item.artist()['artistIcon'])
      except:
        return None
    return None

  def getSizeHint(self, row, column, item):
    """
      Return the size hint for a cell
    """ 

    return QtCore.QSize(20, 20)      

  def paintCell(self, row, column, item, painter, option):
    """
      Paint a custom cell. Return True if the cell was painted, or False to continue
      with the default cell painting.
    """
    currentColumn = self.gCustomColumnList[column]
    if currentColumn['name'] == 'Tags':
      if option.state & QtWidgets.QStyle.State_Selected:
        painter.fillRect(option.rect, option.palette.highlight())
      iconSize = 20
      r = QtCore.QRect(option.rect.x(), option.rect.y()+(option.rect.height()-iconSize)/2, iconSize, iconSize)
      tags = item.tags()
      if len(tags) > 0:
        painter.save()
        painter.setClipRect(option.rect)
        for tag in item.tags():
          M = tag.metadata()
          if not(M.hasKey('tag.status') or  M.hasKey('tag.artistID')):
            QtGui.QIcon(tag.icon()).paint(painter, r, QtCore.Qt.AlignLeft)
            r.translate(r.width()+2, 0)
        painter.restore()
        return True


      QtGui.QIcon(QtGui.QPixmap.fromImage(imageView)).paint(painter, r, QtCore.Qt.AlignCenter)
      painter.setPen(pen)
      painter.drawRoundedRect(r,1,1)
      painter.restore()
      return True      
      
    return False

  def createEditor(self, row, column, item, view):
    """
      Create an editing widget for a custom cell
    """
    self.currentView = view

    currentColumn = self.gCustomColumnList[column]
    if currentColumn['cellType'] == 'readonly':
      cle = QtWidgets.QLabel()
      cle.setEnabled(False)
      cle.setVisible(False)
      return cle

    if currentColumn['name']=='Colourspace':
      cb = QtWidgets.QComboBox()
      for colourspace in self.gColourSpaces:
        cb.addItem(colourspace)
      cb.currentIndexChanged.connect(self.colourspaceChanged)
      return cb

    if currentColumn['name']=='Bid':
      cb = QtWidgets.QComboBox()
      cb.addItem('')
      for key in gStatusTags.keys():
        cb.addItem(QtGui.QIcon(gStatusTags[key]), key)
      cb.addItem('--')  
      cb.currentIndexChanged.connect(self.statusChanged)

      return cb

    if currentColumn['name']=='Artist':
      cb = QtWidgets.QComboBox()
      cb.addItem('')
      for artist in gArtistList:
        cb.addItem(artist['artistName'])
      cb.addItem('--')  
      cb.currentIndexChanged.connect(self.artistNameChanged);
      return cb
    return None

  def setModelData(self, row, column, item, editor):
    return False


  def dropMimeData(self, row, column, item, data, items):
    """
      Handle a drag and drop operation - adds a Dragged Tag to the shot
    """
    for thing in items:
      if isinstance(thing,hiero.core.Tag):
        item.addTag(thing)
    return None


  def statusChanged(self, arg):
    """
      This method is called when Shot Status widget changes index.
    """
    view = hiero.ui.activeView()
    selection = view.selection()
    status = self.sender().currentText()
    project = selection[0].project()    
    with project.beginUndo("Set Status"):
      # A string of '--' characters denotes clear the status
      if status != '--':
        for trackItem in selection:
          trackItem.setStatus(status)
      else:
        for trackItem in selection:
          tTags = trackItem.tags()
          for tag in tTags:
            if tag.metadata().hasKey('tag.status'):
              trackItem.removeTag(tag)
              break 


  def artistNameChanged(self, arg):
    """
      This method is called when Artist widget changes index.
    """
    view = hiero.ui.activeView()
    selection = view.selection()
    name = self.sender().currentText()
    project = selection[0].project()    
    with project.beginUndo("Assign Artist"):
      # A string of '--' denotes clear the assignee...
      if name != '--':
        for trackItem in selection:
          trackItem.setArtistByName(name)
      else:
        for trackItem in selection:
          tTags = trackItem.tags()
          for tag in tTags:
            if tag.metadata().hasKey('tag.artistID'):
              trackItem.removeTag(tag)
              break

def _getArtistFromID(self,artistID):
  """ getArtistFromID -> returns an artist dictionary, by their given ID"""
  global gArtistList
  artist = [element for element in gArtistList if element['artistID'] == int(artistID)]
  if not artist:
    return None
  return artist[0]

def _getArtistFromName(self,artistName):
  """ getArtistFromID -> returns an artist dictionary, by their given ID """
  global gArtistList
  artist = [element for element in gArtistList if element['artistName'] == artistName]
  if not artist:
    return None
  return artist[0]  

def _artist(self):
  """_artist -> Returns the artist dictionary assigned to this shot"""
  artist = None
  tags = self.tags()
  for tag in tags:
    if tag.metadata().hasKey('tag.artistID'):
      artistID = tag.metadata().value('tag.artistID')
      artist = self.getArtistFromID(artistID)
  return artist

def _updateArtistTag(self,artistDict):
  # A shot will only have one artist assigned. Check if one exists and set accordingly
  artistTag = None
  tags = self.tags()
  for tag in tags:
    if tag.metadata().hasKey('tag.artistID'):
      artistTag = tag
      break
  
  if not artistTag:
    artistTag = hiero.core.Tag('Artist')
    artistTag.setIcon(artistDict['artistIcon'])
    artistTag.metadata().setValue('tag.artistID', str(artistDict['artistID']))
    artistTag.metadata().setValue('tag.artistName', str(artistDict['artistName']))
    artistTag.metadata().setValue('tag.artistDepartment', str(artistDict['artistDepartment']))
    self.sequence().editFinished()    
    self.addTag(artistTag)
    self.sequence().editFinished()
    return

  artistTag.setIcon(artistDict['artistIcon'])
  artistTag.metadata().setValue('tag.artistID', str(artistDict['artistID']))
  artistTag.metadata().setValue('tag.artistName', str(artistDict['artistName']))
  artistTag.metadata().setValue('tag.artistDepartment', str(artistDict['artistDepartment']))
  self.sequence().editFinished()
  return

def _setArtistByName(self,artistName):
  """ setArtistByName(artistName) -> sets the artist tag on a TrackItem by a given artistName string"""
  global gArtistList

  artist = self.getArtistFromName(artistName)
  if not artist:
    print 'Artist name: %s was not found in the gArtistList.' % str(artistName)
    return

  # Do the update.
  self.updateArtistTag(artist)

def _setArtistByID(self,artistID):
  """ setArtistByID(artistID) -> sets the artist tag on a TrackItem by a given artistID integer"""
  global gArtistList

  artist = self.getArtistFromID(artistID)
  if not artist:
    print 'Artist name: %s was not found in the gArtistList.' % str(artistID)
    return

  # Do the update.
  self.updateArtistTag(artist)

# Inject status getter and setter methods into hiero.core.TrackItem
hiero.core.TrackItem.artist = _artist
hiero.core.TrackItem.setArtistByName = _setArtistByName
hiero.core.TrackItem.setArtistByID = _setArtistByID  
hiero.core.TrackItem.getArtistFromName = _getArtistFromName
hiero.core.TrackItem.getArtistFromID = _getArtistFromID
hiero.core.TrackItem.updateArtistTag = _updateArtistTag
  
def _status(self):
  """status -> Returns the Shot status. None if no Status is set."""

  status = None
  tags = self.tags()
  for tag in tags:
    if tag.metadata().hasKey('tag.status'):
      status = tag.metadata().value('tag.status')
  return status

def _setStatus(self, status):
  """setShotStatus(status) -> Method to set the Status of a Shot. 
  Adds a special kind of status Tag to a TrackItem
  Example: myTrackItem.setStatus('Final')

  @param status - a string, corresponding to the Status name
  """
  global gStatusTags

  # Get a valid Tag object from the Global list of statuses
  if not status in gStatusTags.keys():
    print 'Status requested was not a valid Status string.'
    return 

  # A shot should only have one status. Check if one exists and set accordingly 
  statusTag = None
  tags = self.tags()
  for tag in tags:
    if tag.metadata().hasKey('tag.status'):
      statusTag = tag
      break
  
  if not statusTag:
    statusTag = hiero.core.Tag('Status')
    statusTag.setIcon(gStatusTags[status])
    statusTag.metadata().setValue('tag.status', status) 
    self.addTag(statusTag)

  statusTag.setIcon(gStatusTags[status])
  statusTag.metadata().setValue('tag.status', status)
  
  self.sequence().editFinished()
  return

# Inject status getter and setter methods into hiero.core.TrackItem
hiero.core.TrackItem.setStatus = _setStatus
hiero.core.TrackItem.status = _status

# This is a convenience method for returning QtGui.QActions with a triggered method based on the title string
def titleStringTriggeredAction(title, method, icon = None):
  action = QtWidgets.QAction(title,None)
  action.setIcon(QtGui.QIcon(icon))
  
  # We do this magic, so that the title string from the action is used to set the status
  def methodWrapper():
    method(title)
  
  action.triggered.connect( methodWrapper )
  return action

# Menu which adds a Set Status Menu to Timeline and Spreadsheet Views
class SetStatusMenu(QtWidgets.QMenu):

  def __init__(self):
      QtWidgets.QMenu.__init__(self, "Set Bid", None)

      global gStatusTags
      self.statuses = gStatusTags
      self._statusActions = self.createStatusMenuActions()      

      # Add the Actions to the Menu.
      for act in self.menuActions:
        self.addAction(act)
      
      hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
      hiero.core.events.registerInterest("kShowContextMenu/kSpreadsheet", self.eventHandler)      

  def createStatusMenuActions(self):
    self.menuActions = []
    for status in self.statuses:
      self.menuActions+=[titleStringTriggeredAction(status,self.setStatusFromMenuSelection, icon=gStatusTags[status])]

  def setStatusFromMenuSelection(self, menuSelectionStatus):
    selectedShots  = [item for item in self._selection if (isinstance(item,hiero.core.TrackItem))]
    selectedTracks  = [item for item in self._selection if (isinstance(item,(hiero.core.VideoTrack,hiero.core.AudioTrack)))]

    # If we have a Track Header Selection, no shots could be selected, so create shotSelection list
    if len(selectedTracks)>=1:
      for track in selectedTracks:
        selectedShots+=[item for item in track.items() if (isinstance(item,hiero.core.TrackItem))]

    # It's possible no shots exist on the Track, in which case nothing is required
    if len(selectedShots)==0:
      return

    currentProject = selectedShots[0].project()

    with currentProject.beginUndo("Set Bid"):
      # Shots selected
      for shot in selectedShots:
        shot.setStatus(menuSelectionStatus)

  # This handles events from the Project Bin View
  def eventHandler(self,event):
    if not hasattr(event.sender, 'selection'):
      # Something has gone wrong, we should only be here if raised
      # by the Timeline/Spreadsheet view which gives a selection.
      return
    
    # Set the current selection
    self._selection = event.sender.selection()

    # Return if there's no Selection. We won't add the Menu.
    if len(self._selection) == 0:
      return
    
    event.menu.addMenu(self)

### Additional Fun Stuff for assigning Artists

# Global list of Artist Name Dictionaries
# Note: Override this to add different names, icons, department, IDs.
gArtistList = [{'artistName':'John Smith','artistIcon':'icons:TagActor.png','artistDepartment':'3D', 'artistID':0},
{'artistName':'Savlvador Dali','artistIcon':'icons:TagActor.png','artistDepartment':'Roto', 'artistID':1},
{'artistName':'Leonardo Da Vinci','artistIcon':'icons:TagActor.png','artistDepartment':'Paint','artistID':2},
{'artistName':'Claude Monet','artistIcon':'icons:TagActor.png','artistDepartment':'Comp','artistID':3},
{'artistName':'Pablo Picasso','artistIcon':'icons:TagActor.png','artistDepartment':'Animation','artistID':4}]



# THIS USED TO BE A STATUS LIST, BUT I MADE IT A PRICE LIST FOR BIDDING
# BECAUSE IT IS A DICTIONARY, IT DOESN'T WANT TO STAY IN ORDER, WHICH ISN'T COOL!
#
# Global Dictionary of Status Tags. 
# Note: This can be overwritten if you want to add a new status cellType or custom icon
# Override the gStatusTags dictionary by adding your own 'Status':'Icon.png' key-value pairs.
# Add new custom keys like so: gStatusTags['For Client'] = 'forClient.png'
gStatusTags = {'$100':'icons:status/TagReadyToStart.png',
  '$150':'icons:status/TagReadyToStart.png',
  '$200':'icons:status/TagReadyToStart.png',
  '$250':'icons:status/TagReadyToStart.png',
  '$300':'icons:status/TagReadyToStart.png',
  '$350':'icons:status/TagReadyToStart.png',
  '$400':'icons:status/TagReadyToStart.png',
  '$450':'icons:status/TagReadyToStart.png',
  '$500':'icons:status/TagReadyToStart.png',
  '$550':'icons:status/TagReadyToStart.png',
  '$600':'icons:status/TagReadyToStart.png',
  '$650':'icons:status/TagReadyToStart.png',
  '$700':'icons:status/TagReadyToStart.png',
  '$750':'icons:status/TagReadyToStart.png',
  '$800':'icons:status/TagReadyToStart.png',
  '$850':'icons:status/TagReadyToStart.png',
  '$900':'icons:status/TagReadyToStart.png',
  '$950':'icons:status/TagReadyToStart.png',
  '$1000':'icons:status/TagReadyToStart.png',
  '$1050':'icons:status/TagReadyToStart.png',
  '$1100':'icons:status/TagReadyToStart.png',
  '$1150':'icons:status/TagReadyToStart.png',
  '$1200':'icons:status/TagReadyToStart.png',
  '$1250':'icons:status/TagReadyToStart.png',
  '$1300':'icons:status/TagReadyToStart.png',
  '$1350':'icons:status/TagReadyToStart.png',
  '$1400':'icons:status/TagReadyToStart.png',
  '$1450':'icons:status/TagReadyToStart.png',
  '$1500':'icons:status/TagReadyToStart.png',
  '$1550':'icons:status/TagReadyToStart.png',
  '$1600':'icons:status/TagReadyToStart.png'}

# Menu which adds a Set Status Menu to Timeline and Spreadsheet Views
class AssignArtistMenu(QtWidgets.QMenu):

  def __init__(self):
      QtWidgets.QMenu.__init__(self, "Assign Artist", None)

      global gArtistList
      self.artists = gArtistList
      self._artistsActions = self.createAssignArtistMenuActions()      

      # Add the Actions to the Menu.
      for act in self.menuActions:
        self.addAction(act)
      
      hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
      hiero.core.events.registerInterest("kShowContextMenu/kSpreadsheet", self.eventHandler)      

  def createAssignArtistMenuActions(self):
    self.menuActions = []
    for artist in self.artists:
      self.menuActions+=[titleStringTriggeredAction(artist['artistName'],self.setArtistFromMenuSelection, icon=artist['artistIcon'])]

  def setArtistFromMenuSelection(self, menuSelectionArtist):
    selectedShots  = [item for item in self._selection if (isinstance(item,hiero.core.TrackItem))]
    selectedTracks  = [item for item in self._selection if (isinstance(item,(hiero.core.VideoTrack,hiero.core.AudioTrack)))]

    # If we have a Track Header Selection, no shots could be selected, so create shotSelection list
    if len(selectedTracks)>=1:
      for track in selectedTracks:
        selectedShots+=[item for item in track.items() if (isinstance(item,hiero.core.TrackItem))]

    # It's possible no shots exist on the Track, in which case nothing is required
    if len(selectedShots)==0:
      return

    currentProject = selectedShots[0].project()

    with currentProject.beginUndo("Assign Artist"):
      # Shots selected
      for shot in selectedShots:
        shot.setArtistByName(menuSelectionArtist)

  # This handles events from the Project Bin View
  def eventHandler(self,event):
    if not hasattr(event.sender, 'selection'):
      # Something has gone wrong, we should only be here if raised
      # by the Timeline/Spreadsheet view which gives a selection.
      return
    
    # Set the current selection
    self._selection = event.sender.selection()

    # Return if there's no Selection. We won't add the Menu.
    if len(self._selection) == 0:
      return
    
    event.menu.addMenu(self)    

# Optionally add the 'Set Status' and Artist menus to Timeline and Spreadsheet
if kAddStatusMenu:
  setStatusMenu = SetStatusMenu()

if kAssignArtistMenu:
  assignArtistMenu = AssignArtistMenu()

# Register our custom columns
hiero.ui.customColumn = CustomSpreadsheetColumns()
