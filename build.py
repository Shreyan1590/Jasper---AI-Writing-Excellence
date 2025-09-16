import PyInstaller.__main__
import os
import shutil

def build_app():
    # Create build directory if it doesn't exist
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # PyInstaller configuration
    PyInstaller.__main__.run([
        'main.py',
        '--name=TextProcessingSuite',
        '--onefile',
        '--windowed',
        '--distpath=build/dist',
        '--workpath=build/work',
        '--specpath=build'
    ])
    
    print("Build completed! Executable is in build/dist directory")

if __name__ == "__main__":
    build_app()