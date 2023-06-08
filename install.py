import launch

if not launch.is_installed("segno"):
    launch.run_pip("install segno", "segno")

if not launch.is_installed("qrcode-artistic"):
    launch.run_pip("install qrcode-artistic", "qrcode-artistic")
