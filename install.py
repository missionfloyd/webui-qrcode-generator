import launch

requirements = ["qrcode", "segno"]
missing = []

for i in requirements:
    if not launch.is_installed(i):
        missing.append(i)
        
if missing:
    launch.run_pip(f"install qrcode {' '.join(missing)}", "requirements for webui-qrcode-generator")