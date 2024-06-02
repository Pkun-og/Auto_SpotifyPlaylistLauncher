from PyQt5 import QtCore, QtWidgets, QtGui
import webbrowser
import time
import pyautogui
import json
import os
import requests
from bs4 import BeautifulSoup
import winreg


class SpotifyLauncher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.playlists = []
        self.load_playlists()
        self.initUI()
    def initUI(self):
        self.setWindowTitle('Spotify Playlist Launcher')
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #1DB954;")

        main_layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Choose one:")
        label.setFont(QtGui.QFont('Helvetica', 14))
        label.setStyleSheet("color: white;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(label)
        

        self.playlist_list = QtWidgets.QListWidget()
        self.playlist_list.setFont(QtGui.QFont('Helvetica', 12))
        main_layout.addWidget(self.playlist_list)
        self.update_playlist_list()

        entry_frame = QtWidgets.QHBoxLayout()

        self.url_entry = QtWidgets.QLineEdit()
        self.url_entry.setFont(QtGui.QFont('Helvetica', 12))
        self.url_entry.setPlaceholderText("Enter the Spotify playlist URL:")
        entry_frame.addWidget(self.url_entry)

        add_button = QtWidgets.QPushButton('Add Playlist')
        add_button.setFont(QtGui.QFont('Helvetica', 12, QtGui.QFont.Bold))
        add_button.setStyleSheet("""
                        QPushButton {
                                 background-color: white;
                                 color: #1DB954;
                                 border: none;
                                 padding: 10px 20px;
                            }
                        QPushButton:hover {
                                 background-color: #1DB954;
                                 color: white;
                        }
                    """)
        add_button.clicked.connect(self.add_playlist)
        entry_frame.addWidget(add_button)

        main_layout.addLayout(entry_frame)

        button_layout = QtWidgets.QHBoxLayout()

        #Edit button
        edit_button = QtWidgets.QPushButton('Edit')
        edit_button.setFont(QtGui.QFont('Helvetica', 12, QtGui.QFont.Bold))
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1DB954;
                border: none;
                padding: 10px 20px;
            }
            QPushButton:hover{
                background-color: #1DB954;
                color: white;
            }
              """)
        edit_button.clicked.connect(self.edit_playlist)
        button_layout.addWidget(edit_button)

        #Remove Button
        remove_button = QtWidgets.QPushButton('Remove')
        remove_button.setFont(QtGui.QFont('Helvetica', 12, QtGui.QFont.Bold))
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1DB954;
                border: none;
                padding: 10px 20px;                
            }
            QPushButton:hover {
                background-color: #1DB954;
                color: white;
            }
                """)
        remove_button.clicked.connect(self.remove_playlist)
        button_layout.addWidget(remove_button)


        play_button = QtWidgets.QPushButton('Play')
        play_button.setFont(QtGui.QFont('Helvetica', 12, QtGui.QFont.Bold))
        play_button.setStyleSheet("""
            QPushButton{
                background-color: white;
                color: #1DB954;
                border: none;
                padding: 10px 20px;
            }
            QPushButton:hover{
                background-color: #1DB954;
                color: white;
            }
              """)
        play_button.clicked.connect(self.play_playlist)
        button_layout.addWidget(play_button)

        quit_button = QtWidgets.QPushButton('Quit')
        quit_button.setFont(QtGui.QFont('Helvetica', 12, QtGui.QFont.Bold))
        quit_button.setStyleSheet("""
            QPushButton{
                background-color: white;
                color: #1DB954;
                border: none;
                padding: 10px 20px;
            }
            QPushButton: hover{
                background-color: #1DB954;
                color: white;
            }
                """)
        quit_button.clicked.connect(self.close)
        button_layout.addWidget(quit_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.destroyed.connect(self.save_playlists)
        self.startup_checkbox = QtWidgets.QCheckBox("Run on Startup")
        self.startup_checkbox.setFont(QtGui.QFont('Helvetica', 12))
        self.startup_checkbox.setStyleSheet("color: white;")
        self.startup_checkbox.setChecked(self.is_startup_enabled())
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)


    def is_startup_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "SpotifyPlaylistLauncher")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
    
    def toggle_startup(self, state):
        if state == QtCore.Qt.Checked:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
            exe_path = sys.executable
            winreg.SetValueEx(key, "SpotifyPlaylistLauncher", 0, winreg.REG_SZ, f'"{exe_path}')
            winreg.CloseKey(key)
        else:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(key, "SpotifyPlaylistLauncher")
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass

    def add_playlist(self):
        url = self.url_entry.text()
        if url and url.startswith("https://open.spotify.com/playlist/"):
            playlist_name = self.get_playlist_name(url)
            if playlist_name:
                self.playlists.append((playlist_name, url))
                self.playlist_list.addItem(playlist_name)
                self.url_entry.clear()
                self.save_playlists()
        else:
            QtWidgets.QMessageBox.warning(self, "Invalid URL", "Please enter a valid Spotify playlist URL.")
    def edit_playlist(self):
        selected_items = self.playlist_list.selectedItems()
        if selected_items:
            current_url = selected_items[0].text()
            new_url, ok = QtWidgets.QInputDialog.getText(self, "Edit Playlist URL", "Enter new URL:", QtWidgets.QLineEdit.Normal, current_url)
            if ok and new_url:
                selected_items[0].setText(new_url)
                self.playlists[self.playlist_list.row(selected_items[0])] = new_url
                self.save_playlists()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to retrieve playlist name.")
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a playlist to edit.")
    
    def remove_playlist(self):
        selected_items = self.playlist_list.selectedItems()
        if selected_items:
            for item in selected_items:
                self.playlists.remove(item.text())
                self.playlist_list.takeItem(self.playlist_list.row(item))
            self.save_playlists()
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a playlist to remove.")

    def play_playlist(self):
        selected_items = self.playlist_list.selectedItems()
        if selected_items:
            playlist_name = selected_items[0].text()
            playlist_url = None
            for name, url in self.playlists:
                if name == playlist_name:
                    playlist_url = url
                    print(f"Playlist URL for '{playlist_name}': {playlist_url}")
                    break
        
            if playlist_url:
                # Path to the Brave browser executable (adjust if necessary)
                brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

            # Register the Brave browser
                webbrowser.register('brave', None, webbrowser.BackgroundBrowser(brave_path))
            
                print(f"Opening playlist URL: {playlist_url}")
            # Open the playlist URL in Brave browser
                webbrowser.get('brave').open_new_tab(playlist_url)
            
            # Wait for the page to load
                time.sleep(10)  # Adjust the wait time if necessary
            
            # Simulate pressing the Play button (assuming it's in focus or can be tabbed to)
                play_button_location = pyautogui.locateCenterOnScreen(r"C:\Users\Mirai\Pictures\Screenshots\Screenshot 2024-06-03 000315.png", confidence=0.9)

            # Click the play button
                if play_button_location:
                    pyautogui.click(play_button_location)
                else:
                    print("Play button not found on the screen.")
                self.close()
            else:
                QtWidgets.QMessageBox.warning(self, "No URL", "Failed to get URL for selected playlist.")
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a playlist to play.")

    def get_playlist_name(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    return title_tag.text.replace(' - Spotify', '').strip()
        except Exception as e:
            print(f"Failed to retrieve playlist name: {e}")
        return None
    
    def save_playlists(self):
        try:
            with open('playlists.json', 'w') as file:
                json.dump(self.playlists, file)
            print("Playlists saved successfully.")
        except Exception as e:
            print(f"Faled to save playlists: {e}")

    def load_playlists(self):
        try:
            if os.path.exists('playlists.json'):
                with open('playlists.json', 'r') as file:
                    self.playlists = json.load(file)
            else:
                print("No playlists file found. Starting fresh.")
        except Exception as e:
            print(f"Failed to load playlists: {e}")
            
    def update_playlist_list(self):
        self.playlist_list.clear()
        for name, url in self.playlists:
            self.playlist_list.addItem(name)

if __name__== '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    launcher = SpotifyLauncher()
    launcher.show()
    sys.exit(app.exec_())