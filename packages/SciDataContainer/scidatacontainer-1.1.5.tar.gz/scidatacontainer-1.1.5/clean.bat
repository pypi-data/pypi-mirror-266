@echo off
rmdir build /s /q
rmdir dist /s /q
rmdir SciDataContainer.egg-info /s /q
del VERSION /q
del test\*.zdc /q
rem del MANIFEST /q
