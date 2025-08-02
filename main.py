import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMenu, QMessageBox
from PyQt5.QtCore import QTimer
from profile_manager import load_profiles, save_profiles
from media_widget import MediaWidget

class DesktopManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.save_scheduled = False
        self.profiles = load_profiles()
        self.current_profile_name = None

        self.widgets = []

        default = next((p for p in self.profiles if p["name"] == "Default"), None)
        if not default:
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "Select Image or GIF to Put on Desktop",
                "",
                "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            if not file_path: sys.exit(0)

            # Create Default profile with one image
            default = {
                "name": "Default",
                "media": [{
                    "path": file_path,
                    "x": 100,
                    "y": 100,
                    "width": 150,
                    "height": 150
                }]
            }
            self.profiles.append(default)
        self.load_profile(default)
        sys.exit(self.app.exec_())

    def create_widget(self, path):
        self.widgets.append(MediaWidget(path, self.show_context_menu))
    
    def create_widget(self, path):
        callbacks = {
            "context_menu": self.show_context_menu,
            "save": self.request_save,
        }
        self.widgets.append(MediaWidget(path, callbacks))
        self.request_save()

    def delete_widget(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
            widget.close()
            widget.deleteLater()
        self.request_save()
    
    def delete_all_widgets(self):
        for widget in self.widgets:
            widget.close()
            widget.deleteLater()
        self.widgets = []

    def show_context_menu(self, widget, global_pos):
        menu = QMenu()

        if widget is not None:
            del_action = menu.addAction("Delete")
            del_action.triggered.connect(lambda: self.delete_widget(widget))
            menu.addSeparator()

        add_action = menu.addAction("Add Image/GIF...")
        add_action.triggered.connect(lambda: self.open_file_dialog(widget))

        if self.profiles:
            profile_menu = QMenu("Profiles")
            for profile in self.profiles:
                action = profile_menu.addAction(profile["name"])
                action.triggered.connect(lambda checked=False, p=profile: self.load_profile(p))
            menu.addMenu(profile_menu)

        new_profile_action = menu.addAction("New Profile...")
        new_profile_action.triggered.connect(lambda: self.prompt_new_profile(widget))

        menu.addSeparator()

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.quit)

        menu.exec_(global_pos)

    def open_file_dialog(self, widget):
        file_path, t = QFileDialog.getOpenFileName(
            widget, # weird: if None, then crashes if dialog is cancelled
            "Select Image or GIF",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.create_widget(file_path)

    def load_profile(self, profile):
        self.current_profile_name = profile["name"]
        media = profile.get("media", [])
        if not media: return

        self.delete_all_widgets()
        for m in media:
            path = m["path"]
            x = m.get("x", 100)
            y = m.get("y", 100)
            w = m.get("width", 150)
            h = m.get("height", 150)
            self.create_widget(path)
            self.widgets[-1].setGeometry(x, y, w, h)
        self.request_save()
    
    def request_save(self):
        if not self.save_scheduled:
            self.save_scheduled = True
            QTimer.singleShot(0, self.save_current_profile)
    
    def save_current_profile(self):
        self.save_scheduled = False # reset flag
        if not self.current_profile_name: return

        media_data = []
        for widget in self.widgets:
            geom = widget.geometry()
            media_data.append({
                "path": widget.image_path,
                "x": geom.x(),
                "y": geom.y(),
                "width": geom.width(),
                "height": geom.height(),
            })

        for profile in self.profiles:
            if profile["name"] == self.current_profile_name:
                profile["media"] = media_data
                break
        else:
            self.profiles.append({
                "name": self.current_profile_name,
                "media": media_data
            })

        save_profiles(self.profiles)

    def prompt_new_profile(self, widget):
        name, ok = QInputDialog.getText(widget, "New Profile", "Enter profile name:")
        if not ok or not name.strip():
            return # Cancelled or empty name
        name = name.strip()

        # Check for duplicates
        if any(p["name"] == name for p in self.profiles):
            QMessageBox.warning(widget, "Error", f"A profile named '{name}' already exists.")
            return

        # Save current profile
        self.save_current_profile()
        
        # Activate the new profile
        self.current_profile_name = name
        self.request_save()

    def quit(self):
        self.delete_all_widgets()
        self.app.quit()

if __name__ == '__main__':
    DesktopManager()
