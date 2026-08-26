Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter signtool.exe -ErrorAction SilentlyContinue |
Where-Object { $_.FullName -match "\\x64\\signtool.exe$" } |
Sort-Object FullName -Descending |
Select-Object -First 1 -ExpandProperty FullName
