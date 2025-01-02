//
//  ReverseEngineeringToolsChecker.swift
//  IOSSecuritySuite
//
//  Created by wregula on 24/04/2019.
//  Copyright © 2019 wregula. All rights reserved.
//

import Foundation
import MachO // dyld

internal class ReverseEngineeringToolsChecker {

    static func amIReverseEngineered() -> Bool {
        return (checkDYLD() || checkExistenceOfSuspiciousFiles() || checkOpenedPorts())
    }

    private static func checkDYLD() -> Bool {

        let suspiciousLibraries = [
            [37, 17, 10, 7, 2, 36, 2, 7, 4, 6, 23], //"FridaGadget",
            [5, 17, 10, 7, 2],  //"frida", // Needle injects frida-somerandom.dylib
            [0, 26, 13, 9, 6, 0, 23],   //"cynject",
            [15, 10, 1, 0, 26, 0, 17, 10, 19, 23]   //"libcycript"
        ]

        for libraryIndex in 0..<_dyld_image_count() {

            // _dyld_get_image_name returns const char * that needs to be casted to Swift String
            guard let loadedLibrary = String(validatingUTF8: _dyld_get_image_name(libraryIndex)) else { continue }

            for suspiciousLibrary in suspiciousLibraries {
                let strLibrary = JailbreakChecker.ObSt(arr: suspiciousLibrary, mask: KCDEF_MASK);
                if loadedLibrary.lowercased().contains(strLibrary.lowercased()) {
                    NSLog("0xe1");
                    return true
                }
            }
        }

        return false
    }

    private static func checkExistenceOfSuspiciousFiles() -> Bool {

        let paths = [
            [76, 22, 16, 17, 76, 16, 1, 10, 13, 76, 5, 17, 10, 7, 2, 78, 16, 6, 17, 21, 6, 17]  //"/usr/sbin/frida-server"
        ]

        for path in paths {
            let strPath = JailbreakChecker.ObSt(arr: path, mask: KCDEF_MASK);
            if FileManager.default.fileExists(atPath: strPath) {
                NSLog("0xe2")
                return true
            }
        }

        return false
    }

    private static func checkOpenedPorts() -> Bool {

        let ports = [
            27042, // default Frida
            4444 // default Needle
        ]

        for port in ports {

            if canOpenLocalConnection(port: port) {
                NSLog("0xe4")
                return true
            }
        }

        return false
    }

    private static func canOpenLocalConnection(port: Int) -> Bool {

        func swapBytesIfNeeded(port: in_port_t) -> in_port_t {
            let littleEndian = Int(OSHostByteOrder()) == OSLittleEndian
            return littleEndian ? _OSSwapInt16(port) : port
        }

        var serverAddress = sockaddr_in()
        serverAddress.sin_family = sa_family_t(AF_INET)
        serverAddress.sin_addr.s_addr = inet_addr("127.0.0.1")
        serverAddress.sin_port = swapBytesIfNeeded(port: in_port_t(port))
        let sock = socket(AF_INET, SOCK_STREAM, 0)

        let result = withUnsafePointer(to: &serverAddress) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                connect(sock, $0, socklen_t(MemoryLayout<sockaddr_in>.stride))
            }
        }
        
        defer {
            close(sock)
        }

        if result != -1 {
            NSLog("0xe5")
            return true // Port is opened
        }

        return false
    }
    
    // EXPERIMENTAL
    private static func checkPSelectFlag() -> Bool {
        var kinfo = kinfo_proc()
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        var size = MemoryLayout<kinfo_proc>.stride
        let sysctlRet = sysctl(&mib, UInt32(mib.count), &kinfo, &size, nil, 0)

        if sysctlRet != 0 {
            print("Error occured when calling sysctl(). This check may not be reliable")
        }
        NSLog("0xe6")
        return (kinfo.kp_proc.p_flag & P_SELECT) != 0
    }
}
