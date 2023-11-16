import launch
import importlib.metadata
import packaging.version

def compare_versions(package, version_required):
    try:
        version_installed = importlib.metadata.version(package)
    except Exception:
        return False
    
    if packaging.version.parse(version_installed) < packaging.version.parse(version_required):
        return False
    
    return True

if not compare_versions("segno", "1.5.3"):
    launch.run_pip('install "segno>=1.5.3"', "requirements for webui-qrcode-generator")