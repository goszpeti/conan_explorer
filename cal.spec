# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


def Entrypoint(dist, group, name, **kwargs):
    import pkg_resources

    # get toplevel packages of distribution from metadata
    def get_toplevel(dist):
        distribution = pkg_resources.get_distribution(dist)
        if distribution.has_metadata('top_level.txt'):
            return list(distribution.get_metadata('top_level.txt').split())
        else:
            return []

    kwargs.setdefault('hiddenimports', [])
    packages = []
    for distribution in kwargs['hiddenimports']:
        packages += get_toplevel(distribution)

    kwargs.setdefault('pathex', [])
    # get the entry point
    ep = pkg_resources.get_entry_info(dist, group, name)
    # insert path of the egg at the verify front of the search path
    kwargs['pathex'] = [ep.dist.location] + kwargs['pathex']
    # script name must not be a valid module name to avoid name clashes on import
    script_path = os.path.join(workpath, name + '-script.py')
    print("creating script for entry point", dist, group, name)
    with open(script_path, 'w') as fh:
        print("import", ep.module_name, file=fh)
        print("%s.%s()" % (ep.module_name, '.'.join(ep.attrs)), file=fh)
        for package in packages:
            print("import", package, file=fh)

    return Analysis(
        [script_path] + kwargs.get('scripts', []),
        **kwargs
    )
import os

a = Entrypoint('conan_app_launcher', 'gui_scripts', 'conan_app_launcher',
               pathex=[],
               binaries=[],
               datas=[("./src/conan_app_launcher", "conan_app_launcher")],
               hiddenimports=[],
               hookspath=[],
               hooksconfig={},
               runtime_hooks=[],
               excludes=["debugpy"],
               win_no_prefer_redirects=False,
               win_private_assemblies=False,
               cipher=block_cipher,
               noarchive=False
)

to_keep = []
to_exclude = {'Qt5dbus.dll', 'Qt5Network.dll', 'Qt5Qml.dll', "Qt5DBus.dll", "Qt5QmlModels.dll",
              'Qt5Quick.dll', 'Qt5Svg.dll', 'Qt5WebSockets.dll', "d3dcompiler_47.dll", "opengl32sw.dll",
              "libicudata.so.66", "libgtk-3.so.0" ,"libQt5Quick.so.5", "libQt5Qml.so.5" ,"libicui18n.so.66", "libicui18n.so.66",
              "libQt5Network.so.5", "libQt5QmlModels.so.5"
              }

# Iterate through the list of included binaries.
for (dest, source, kind) in a.binaries:
    # Skip anything we don't need.
    if os.path.split(dest)[1] in to_exclude:
        continue
    to_keep.append((dest, source, kind))

a.binaries = to_keep

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='conan_app_launch_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='src/conan_app_launcher/assets/icons/icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='cal')
