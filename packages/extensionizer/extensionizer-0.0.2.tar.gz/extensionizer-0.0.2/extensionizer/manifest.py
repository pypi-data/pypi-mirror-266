import json

class manifestme:
    def __init__(self, name, version, description, manifest_version=3):
        self.manifest_version = manifest_version
        self.name = name
        self.version = version
        self.description = description
        self.background = None
        self.content_scripts = []
        self.permissions = []

    def add_permission(self, permission):
        self.permissions.append(permission)

    def set_background(self, script):
        self.background = script

    def add_content_script(self, matches, js_files):
        content_script = {"matches": matches, "js": js_files}
        self.content_scripts.append(content_script)

    def to_dict(self):
        manifest_dict = {
            "manifest_version": self.manifest_version,
            "name": self.name,
            "version": self.version,
            "description": self.description,
        }
        if self.background:
            manifest_dict["background"] = self.background
        if self.permissions:
            manifest_dict["permissions"] = self.permissions
        if self.content_scripts:
            manifest_dict["content_scripts"] = self.content_scripts
        return manifest_dict

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
    
    def save_manifest(self, filename="manifest.json"):
        with open(filename, "w") as f:
            f.write(self.to_json())

class popup:
    @staticmethod
    def generate_files():
        # Generate popup.html content
        popup_html_content = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Popup</title>
    <link rel="stylesheet" href="popup.css">
</head>
<body>
    <div id="popup-content">
        <h1>Hello, this is a popup!</h1>
        <button id="popup-button">Click me!</button>
    </div>
    <script src="popup.js"></script>
</body>
</html>
"""
        # Generate popup.css content
        popup_css_content = """\
/* Add your CSS styles here */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

#popup-content {
    text-align: center;
}

#popup-button {
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}
"""

        # Generate popup.js content
        popup_js_content = """\
// Add your JavaScript code here
document.addEventListener('DOMContentLoaded', function() {
    var button = document.getElementById('popup-button');
    button.addEventListener('click', function() {
        alert('Button clicked!');
    });
});
"""

        return {
            "popup.html": popup_html_content,
            "popup.css": popup_css_content,
            "popup.js": popup_js_content
        }
