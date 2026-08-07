Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
Set WshShell = CreateObject("WScript.Shell")

q = Chr(34)
backendDir = scriptDir & "\backend"
venvPython = backendDir & "\.venv\Scripts\python.exe"

setupStep = ""
If Not fso.FileExists(venvPython) Then
    setupStep = "python -m venv .venv && .venv\Scripts\python -m pip install --upgrade pip && .venv\Scripts\python -m pip install -r requirements.txt && "
End If

cmd = "cmd /c cd /d " & q & backendDir & q & " && " & setupStep & ".venv\Scripts\python desktop.py > " & q & scriptDir & "\desktop.log" & q & " 2>&1"

WshShell.Run cmd, 0, False
