import launch

requirements = ["python-barcode", "segno"]
missing = []

for i in requirements:
    if not launch.is_installed(i):
        missing.append(i)
        
if missing:
    launch.run_pip(f"install {' '.join(missing)}", "requirements for webui-qrcode-generator")