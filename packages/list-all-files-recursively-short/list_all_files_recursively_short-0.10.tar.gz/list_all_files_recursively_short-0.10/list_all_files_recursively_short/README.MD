

# List files + 8.3 path

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install list-all-files-recursively-short


```PY
from list_all_files_recursively_short import get_folder_file_complete_path, bufferconfig

bufferconfig.buffer_long_path = 1024

fi = get_folder_file_complete_path(
    folders=[r"C:\Program Files\Microsoft Visual Studio"]
)
for file in fi[:10]:
    print(file.folder, file.file, file.path, file.ext, file.name83)

# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7 servicehub.config.json C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\servicehub.config.json .json C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\SERVIC~1.JSO
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE adodb.manifest C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\adodb.manifest .manifest C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\ADODB~1.MAN
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-core-file-l1-2-0.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-core-file-l1-2-0.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\API-MS~1.DLL
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-core-file-l2-1-0.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-core-file-l2-1-0.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\API-MS~2.DLL
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-core-localization-l1-2-0.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-core-localization-l1-2-0.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\API-MS~3.DLL
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-core-processthreads-l1-1-1.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-core-processthreads-l1-1-1.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\API-MS~4.DLL
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-core-synch-l1-2-0.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-core-synch-l1-2-0.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\APF10C~1.DLL
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-core-timezone-l1-1-0.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-core-timezone-l1-1-0.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\AP7902~1.DLL
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-crt-convert-l1-1-0.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-crt-convert-l1-1-0.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\APFD9C~1.DLL
# C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE api-ms-win-crt-environment-l1-1-0.dll C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\api-ms-win-crt-environment-l1-1-0.dll .dll C:\PROGRA~1\MICROS~4\2022\COMMUN~1\Common7\IDE\APC00F~1.DLL
```