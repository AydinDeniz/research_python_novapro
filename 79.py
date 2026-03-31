from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import importlib.util
import os
import zipfile
import shutil

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
db = SQLAlchemy(app)

plugins = {}

def load_plugin(plugin_path):
    if plugin_path.endswith(".zip"):
        with zipfile.ZipFile(plugin_path, "r") as zip_ref:
            extract_dir = "plugins/" + os.path.splitext(os.path.basename(plugin_path))[0]
            zip_ref.extractall(extract_dir)
            plugin_path = os.path.join(extract_dir, os.listdir(extract_dir)[0])

    if plugin_path.endswith(".py"):
        module_name = os.path.splitext(os.path.basename(plugin_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

def register_plugin_routes(plugin):
    if hasattr(plugin, "register_routes"):
        plugin.register_routes(app)

def register_plugin_cli(plugin):
    if hasattr(plugin, "register_cli"):
        plugin.register_cli(app)

@app.route("/plugins", methods=["POST"])
def upload_plugin():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    plugin_path = f"plugins/{file.filename}"
    file.save(plugin_path)
    plugin = load_plugin(plugin_path)
    if plugin:
        plugins[plugin_path] = plugin
        register_plugin_routes(plugin)
        register_plugin_cli(plugin)
        return jsonify({"message": "Plugin uploaded and registered"}), 201
    else:
        return jsonify({"error": "Failed to load plugin"}), 500

@app.route("/plugins", methods=["GET"])
def list_plugins():
    return jsonify(list(plugins.keys()))

@app.route("/plugins/<plugin_name>", methods=["DELETE"])
def delete_plugin(plugin_name):
    plugin_path = f"plugins/{plugin_name}"
    if plugin_path in plugins:
        del plugins[plugin_path]
        if os.path.exists(plugin_path):
            os.remove(plugin_path)
        return jsonify({"message": "Plugin deleted"}), 200
    else:
        return jsonify({"error": "Plugin not found"}), 404

@app.cli.command("list-plugins")
def list_plugins_cli():
    for plugin_path in plugins:
        print(plugin_path)

if __name__ == "__main__":
    if not os.path.exists("plugins"):
        os.makedirs("plugins")
    app.run(debug=True)
    
def register_routes(app):
    @app.route("/sample", methods=["GET"])
    def sample_route():
        return "Hello from sample plugin!"

def register_cli(app):
    @app.cli.command("sample-cli")
    def sample_cli():
        print("Running sample CLI command")