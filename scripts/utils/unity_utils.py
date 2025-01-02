from utils import file_utils
from utils import cli_utils
from utils import conf_utils
import os

__author__ = 'Mason'

def encrypt_unity(mono_encrypt_ver, decompile_dir):
    mono_path = "config/mono/" + mono_encrypt_ver
    mono_path = file_utils.get_full_path(mono_path)
    if not file_utils.exists(mono_path):
        return

    #copy mono
    target_lib_path = file_utils.get_full_path(os.path.join(decompile_dir, "lib"))
    file_utils.copy_files(os.path.join(mono_path, "armv7a/libmono.so"), os.path.join(target_lib_path, "armeabi/libmono.so"))
    file_utils.copy_files(os.path.join(mono_path, "armv7a/libmono.so"), os.path.join(target_lib_path, "armeabi-v7a/libmono.so"))
    file_utils.copy_files(os.path.join(mono_path, "x86/libmono.so"), os.path.join(target_lib_path, "x86/libmono.so"))

    #encrypt dll
    unity_dll_csharp = file_utils.get_full_path(decompile_dir + "/assets/bin/Data/Managed/Assembly-CSharp.dll");
    unity_dll_csharp_plugin = file_utils.get_full_path(decompile_dir + "/assets/bin/Data/Managed/Assembly-CSharp-firstpass.dll");

    if file_utils.exists(unity_dll_csharp):
        _encrypt_file(unity_dll_csharp)

    if file_utils.exists(unity_dll_csharp_plugin):
        _encrypt_file(unity_dll_csharp_plugin)

def _encrypt_file(file):
    file_ctrl = open(file, "rb")
    data = file_ctrl.read()
    file_ctrl.close()

    barr = bytearray(data)
    #print type(barr)
    #print len(barr)

    for num in range(0,len(barr)):
        if num % 2 == 0:
            if barr[num] + 1 > 255:
                barr[num] = 0
            else:
                barr[num] = barr[num] + 1
        else:
            if barr[num] - 1 < 0:
                barr[num] = 255
            else:
                barr[num] = barr[num] - 1

    output = open(file, 'wb')
    output.write(barr)
    output.close()