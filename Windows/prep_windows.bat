# min lenght passwords
net accounts /minpwlen:12

#disable xbox game bar
# only powershel?

# disable telemetry
sc config "diagtrack" start=disabled
sc config "dmwappushservice" start=disable
reg add "HKLM\SOFTWARE\Policies\\Microsoft\Windows\DataCollection"/v AllowTelemtery/t REG_DWORD/d 0 /f

# delete onedrive (version 64)
TASKKILL /f /im OneDrive.exe
%systemroot%\SysWOW64\OneDriveSetup.exe /uninstall
# for 32 bit:
#%systemroot%\System32\OneDriveSetup.exe /uninstall

# disable ssh
sc config "ssh-agent" start=disabled
sc config "sshd" start=disabled

# disabe ftpsvc
sc config "ftpsvc" start=disabled

# disable RasAuto
sc config "rasauto" start=disabled

#disable TermService
sc config "termservice" start=disabled