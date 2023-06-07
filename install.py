import launch

if not launch.is_installed("segno"):
    launch.run_pip("install segno", "requirements for webui-qrcode-generator")