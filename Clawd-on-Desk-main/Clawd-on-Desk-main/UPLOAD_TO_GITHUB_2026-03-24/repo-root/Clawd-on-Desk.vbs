Dim ws
Set ws = CreateObject("WScript.Shell")
ws.CurrentDirectory = "D:\ClaudeonDesk-WindowsEyes\Clawd-on-Desk-main\Clawd-on-Desk-main\UPLOAD_TO_GITHUB_2026-03-24\repo-root"
ws.Run "cmd /c npm start", 0, False
