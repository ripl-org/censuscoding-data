# geocoding-data

## Windows setup
1. **Create and activate virtual environment**
   ```ps1
   # Create virtual env
   python -m venv geocode
   # Set execution policy (if necessary) and activate environment
   try { .\geocode\Scripts\Activate.ps1 }
   catch { 
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     .\geocode\Scripts\Activate.ps1
   }

   # Install pip
   python -m pip install --upgrade pip
   ```

2. **Install all dependencies except Fiona**
   ```ps1
   python -m pip install pandas pyproj rtree scons shapely usaddress
   ```

3. **Download GDAL and Fiona Built Distributions**
Download the correct [GDAL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal)
and [Fiona](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona) built distributions
and store them in `.\geocode\Lib\site-packages\`.
The correct versions are based on current Python version and operating system. For
example, a user with Python 3.9.7 on a Windows 64-bit system would select the 
`GDAL‑<version>‑cp39‑cp39‑win_amd64.whl` GDAL distribution and 
`Fiona‑<version>‑cp39‑cp39‑win_amd64.whl` Fiona distribution files.

4. **Install GDAL and Fiona**
   ```ps1
   python -m pip install .\geocode\Lib\site-packages\GDAL-<version>-cp39-cp39-win_amd64.whl .\geocode\Lib\site-packages\Fiona-<version>-cp39-cp39-win_amd64.whl
   ```

## Build
Run `scons` in the root directory.
