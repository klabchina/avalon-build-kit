//
//  JailbreakChecker.swift
//  IOSSecuritySuite
//
//  Created by wregula on 23/04/2019.
//  Copyright © 2019 wregula. All rights reserved.
//
//swiftlint:disable cyclomatic_complexity function_body_length type_body_length

import Foundation
import UIKit
import Darwin // fork
import MachO // dyld

public typealias FailedCheck = (check: JailbreakCheck, failMessage: String)

public enum JailbreakCheck: CaseIterable {
    case urlSchemes
    case existenceOfSuspiciousFiles
    case suspiciousFilesCanBeOpened
    case restrictedDirectoriesWriteable
    case fork
    case symbolicLinks
    case dyld
}

internal class JailbreakChecker {
    typealias CheckResult = (passed: Bool, failMessage: String)

    struct JailbreakStatus {
        let passed: Bool
        let failMessage: String // Added for backwards compatibility
        let failedChecks: [FailedCheck]
    }

    static func amIJailbroken() -> Bool {
        return !performChecks().passed
    }

    static func amIJailbrokenWithFailMessage() -> (jailbroken: Bool, failMessage: String) {
        let status = performChecks()
        return (!status.passed, status.failMessage)
    }

    static func amIJailbrokenWithFailedChecks() -> (jailbroken: Bool, failedChecks: [FailedCheck]) {
        let status = performChecks()
        return (!status.passed, status.failedChecks)
    }
    
    static func ObSt(arr: Array<Int>, mask: Int) -> String{
        var str = "";
        for dt in arr
        {
            let re = dt ^ mask;
            str.unicodeScalars.append(UnicodeScalar(re)!);
        }
        return str;
    }

    private static func performChecks() -> JailbreakStatus {
        var passed = true
        var failMessage = ""
        var result: CheckResult = (true, "")
        var failedChecks: [FailedCheck] = []

        for check in JailbreakCheck.allCases {
            switch check {
            case .urlSchemes:
                result = checkURLSchemes()
            case .existenceOfSuspiciousFiles:
                result = checkExistenceOfSuspiciousFiles()
            case .suspiciousFilesCanBeOpened:
                result = checkSuspiciousFilesCanBeOpened()
            case .restrictedDirectoriesWriteable:
                result = checkRestrictedDirectoriesWriteable()
            case .fork:
                if !EmulatorChecker.amIRunInEmulator() {
                    result = checkFork()
                } else {
                    print("App run in the emulator, skipping the fork check.")
                    result = (true, "")
                }
            case .symbolicLinks:
                result = checkSymbolicLinks()
            case .dyld:
                result = checkDYLD()
            }

            passed = passed && result.passed

            if !result.passed {
                failedChecks.append((check: check, failMessage: result.failMessage))

                if !failMessage.isEmpty {
                    failMessage += ", "
                }
            }

            failMessage += result.failMessage
        }

        return JailbreakStatus(passed: passed, failMessage: failMessage, failedChecks: failedChecks)
    }

    private static func canOpenUrlFromList(urlSchemes: [[Int]]) -> CheckResult {
        for urlScheme in urlSchemes {
            let strUrl = ObSt(arr: urlScheme, mask: KCDEF_MASK);
            if let url = URL(string: strUrl) {
                if UIApplication.shared.canOpenURL(url) {
                    return(false, "\(strUrl) URL scheme detected")
                }
            }
        }
        return (true, "")
    }

    private static func checkURLSchemes() -> CheckResult {
        var flag: (passed: Bool, failMessage: String) = (true, "")
        let urlSchemes = [
        [22, 13, 7, 6, 0, 10, 14, 22, 16, 89, 76, 76], //undecimus://
	    [16, 10, 15, 6, 12, 89, 76, 76], //sileo://
	    [25, 1, 17, 2, 89, 76, 76], //zbra://
	    [5, 10, 15, 25, 2, 89, 76, 76], //filza://
	    [2, 0, 23, 10, 21, 2, 23, 12, 17, 89, 76, 76], //activator://
        ]

        if Thread.isMainThread {
            flag = canOpenUrlFromList(urlSchemes: urlSchemes)
        } else {
            let semaphore = DispatchSemaphore(value: 0)
            DispatchQueue.main.async {
                flag = canOpenUrlFromList(urlSchemes: urlSchemes)
                semaphore.signal()
            }
            semaphore.wait()
        }
        return flag
    }

    private static func checkExistenceOfSuspiciousFiles() -> CheckResult {
        var paths = [
            [76, 22, 16, 17, 76, 16, 1, 10, 13, 76, 5, 17, 10, 7, 2, 78, 16, 6, 17, 21, 6, 17], ///usr/sbin/frida-server
            [76, 6, 23, 0, 76, 2, 19, 23, 76, 16, 12, 22, 17, 0, 6, 16, 77, 15, 10, 16, 23, 77, 7, 76, 6, 15, 6, 0, 23, 17, 2, 77, 15, 10, 16, 23], ///etc/apt/sources.list.d/electra.list
            [76, 6, 23, 0, 76, 2, 19, 23, 76, 16, 12, 22, 17, 0, 6, 16, 77, 15, 10, 16, 23, 77, 7, 76, 16, 10, 15, 6, 12, 77, 16, 12, 22, 17, 0, 6, 16], ///etc/apt/sources.list.d/sileo.sources
            [76, 77, 1, 12, 12, 23, 16, 23, 17, 2, 19, 19, 6, 7, 60, 6, 15, 6, 0, 23, 17, 2], ///.bootstrapped_electra
            [76, 22, 16, 17, 76, 15, 10, 1, 76, 15, 10, 1, 9, 2, 10, 15, 1, 17, 6, 2, 8, 77, 7, 26, 15, 10, 1], ///usr/lib/libjailbreak.dylib
            [76, 9, 1, 76, 15, 25, 14, 2], ///jb/lzma
            [76, 77, 0, 26, 7, 10, 2, 60, 13, 12, 60, 16, 23, 2, 16, 11], ///.cydia_no_stash
            [76, 77, 10, 13, 16, 23, 2, 15, 15, 6, 7, 60, 22, 13, 0, 83, 21, 6, 17], ///.installed_unc0ver
            [76, 9, 1, 76, 12, 5, 5, 16, 6, 23, 16, 77, 19, 15, 10, 16, 23], ///jb/offsets.plist
            [76, 22, 16, 17, 76, 16, 11, 2, 17, 6, 76, 9, 2, 10, 15, 1, 17, 6, 2, 8, 76, 10, 13, 9, 6, 0, 23, 14, 6, 77, 19, 15, 10, 16, 23], ///usr/share/jailbreak/injectme.plist
            [76, 6, 23, 0, 76, 2, 19, 23, 76, 22, 13, 7, 6, 0, 10, 14, 22, 16, 76, 22, 13, 7, 6, 0, 10, 14, 22, 16, 77, 15, 10, 16, 23], ///etc/apt/undecimus/undecimus.list
            [76, 21, 2, 17, 76, 15, 10, 1, 76, 7, 19, 8, 4, 76, 10, 13, 5, 12, 76, 14, 12, 1, 10, 15, 6, 16, 22, 1, 16, 23, 17, 2, 23, 6, 77, 14, 7, 86, 16, 22, 14, 16], ///var/lib/dpkg/info/mobilesubstrate.md5sums
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 76, 46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 77, 7, 26, 15, 10, 1], ///Library/MobileSubstrate/MobileSubstrate.dylib
            [76, 9, 1, 76, 9, 2, 10, 15, 1, 17, 6, 2, 8, 7, 77, 19, 15, 10, 16, 23], ///jb/jailbreakd.plist
            [76, 9, 1, 76, 2, 14, 5, 10, 7, 60, 19, 2, 26, 15, 12, 2, 7, 77, 7, 26, 15, 10, 1], ///jb/amfid_payload.dylib
            [76, 9, 1, 76, 15, 10, 1, 9, 2, 10, 15, 1, 17, 6, 2, 8, 77, 7, 26, 15, 10, 1], ///jb/libjailbreak.dylib
            [76, 22, 16, 17, 76, 15, 10, 1, 6, 27, 6, 0, 76, 0, 26, 7, 10, 2, 76, 5, 10, 17, 14, 20, 2, 17, 6, 77, 16, 11], ///usr/libexec/cydia/firmware.sh
            [76, 21, 2, 17, 76, 15, 10, 1, 76, 0, 26, 7, 10, 2], ///var/lib/cydia
            [76, 6, 23, 0, 76, 2, 19, 23], ///etc/apt
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 15, 10, 1, 76, 2, 19, 23], ///private/var/lib/apt
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 54, 16, 6, 17, 16, 76], ///private/var/Users/
            [76, 21, 2, 17, 76, 15, 12, 4, 76, 2, 19, 23], ///var/log/apt
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 32, 26, 7, 10, 2, 77, 2, 19, 19], ///Applications/Cydia.app
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 16, 23, 2, 16, 11], ///private/var/stash
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 15, 10, 1, 76, 2, 19, 23, 76], ///private/var/lib/apt/
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 15, 10, 1, 76, 0, 26, 7, 10, 2], ///private/var/lib/cydia
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 0, 2, 0, 11, 6, 76, 2, 19, 23, 76], ///private/var/cache/apt/
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 15, 12, 4, 76, 16, 26, 16, 15, 12, 4], ///private/var/log/syslog
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 23, 14, 19, 76, 0, 26, 7, 10, 2, 77, 15, 12, 4], ///private/var/tmp/cydia.log
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 42, 0, 26, 77, 2, 19, 19], ///Applications/Icy.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 46, 27, 55, 22, 1, 6, 77, 2, 19, 19], ///Applications/MxTube.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 49, 12, 0, 8, 34, 19, 19, 77, 2, 19, 19], ///Applications/RockApp.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 1, 15, 2, 0, 8, 17, 2, 82, 13, 77, 2, 19, 19], ///Applications/blackra1n.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 48, 33, 48, 6, 23, 23, 10, 13, 4, 16, 77, 2, 19, 19], ///Applications/SBSettings.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 37, 2, 8, 6, 32, 2, 17, 17, 10, 6, 17, 77, 2, 19, 19], ///Applications/FakeCarrier.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 52, 10, 13, 23, 6, 17, 33, 12, 2, 17, 7, 77, 2, 19, 19], ///Applications/WinterBoard.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 42, 13, 23, 6, 15, 15, 10, 48, 0, 17, 6, 6, 13, 77, 2, 19, 19], ///Applications/IntelliScreen.app
            [76, 19, 17, 10, 21, 2, 23, 6, 76, 21, 2, 17, 76, 14, 12, 1, 10, 15, 6, 76, 47, 10, 1, 17, 2, 17, 26, 76, 48, 33, 48, 6, 23, 23, 10, 13, 4, 16, 76, 55, 11, 6, 14, 6, 16], ///private/var/mobile/Library/SBSettings/Themes
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 76, 32, 26, 7, 10, 2, 48, 22, 1, 16, 23, 17, 2, 23, 6, 77, 7, 26, 15, 10, 1], ///Library/MobileSubstrate/CydiaSubstrate.dylib
            [76, 48, 26, 16, 23, 6, 14, 76, 47, 10, 1, 17, 2, 17, 26, 76, 47, 2, 22, 13, 0, 11, 39, 2, 6, 14, 12, 13, 16, 76, 0, 12, 14, 77, 10, 8, 6, 26, 77, 1, 1, 12, 23, 77, 19, 15, 10, 16, 23], ///System/Library/LaunchDaemons/com.ikey.bbot.plist
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 76, 39, 26, 13, 2, 14, 10, 0, 47, 10, 1, 17, 2, 17, 10, 6, 16, 76, 53, 6, 6, 13, 0, 26, 77, 19, 15, 10, 16, 23], ///Library/MobileSubstrate/DynamicLibraries/Veency.plist
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 76, 39, 26, 13, 2, 14, 10, 0, 47, 10, 1, 17, 2, 17, 10, 6, 16, 76, 47, 10, 21, 6, 32, 15, 12, 0, 8, 77, 19, 15, 10, 16, 23], ///Library/MobileSubstrate/DynamicLibraries/LiveClock.plist
            [76, 48, 26, 16, 23, 6, 14, 76, 47, 10, 1, 17, 2, 17, 26, 76, 47, 2, 22, 13, 0, 11, 39, 2, 6, 14, 12, 13, 16, 76, 0, 12, 14, 77, 16, 2, 22, 17, 10, 8, 77, 32, 26, 7, 10, 2, 77, 48, 23, 2, 17, 23, 22, 19, 77, 19, 15, 10, 16, 23], ///System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 48, 10, 15, 6, 12, 77, 2, 19, 19], ///Applications/Sileo.app
            [76, 21, 2, 17, 76, 1, 10, 13, 19, 2, 0, 8], ///var/binpack
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 51, 17, 6, 5, 6, 17, 6, 13, 0, 6, 33, 22, 13, 7, 15, 6, 16, 76, 47, 10, 1, 6, 17, 23, 26, 51, 17, 6, 5, 77, 1, 22, 13, 7, 15, 6], ///Library/PreferenceBundles/LibertyPref.bundle
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 51, 17, 6, 5, 6, 17, 6, 13, 0, 6, 33, 22, 13, 7, 15, 6, 16, 76, 48, 11, 2, 7, 12, 20, 51, 17, 6, 5, 6, 17, 6, 13, 0, 6, 16, 77, 1, 22, 13, 7, 15, 6], ///Library/PreferenceBundles/ShadowPreferences.bundle
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 51, 17, 6, 5, 6, 17, 6, 13, 0, 6, 33, 22, 13, 7, 15, 6, 16, 76, 34, 33, 26, 19, 2, 16, 16, 51, 17, 6, 5, 16, 77, 1, 22, 13, 7, 15, 6], ///Library/PreferenceBundles/ABypassPrefs.bundle
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 51, 17, 6, 5, 6, 17, 6, 13, 0, 6, 33, 22, 13, 7, 15, 6, 16, 76, 37, 15, 26, 41, 33, 51, 17, 6, 5, 16, 77, 1, 22, 13, 7, 15, 6], ///Library/PreferenceBundles/FlyJBPrefs.bundle
            [76, 22, 16, 17, 76, 15, 10, 1, 76, 15, 10, 1, 11, 12, 12, 8, 6, 17, 77, 7, 26, 15, 10, 1], ///usr/lib/libhooker.dylib
            [76, 22, 16, 17, 76, 15, 10, 1, 76, 15, 10, 1, 16, 22, 1, 16, 23, 10, 23, 22, 23, 6, 77, 7, 26, 15, 10, 1], ///usr/lib/libsubstitute.dylib
            [76, 22, 16, 17, 76, 15, 10, 1, 76, 16, 22, 1, 16, 23, 17, 2, 23, 6], ///usr/lib/substrate
            [76, 22, 16, 17, 76, 15, 10, 1, 76, 55, 20, 6, 2, 8, 42, 13, 9, 6, 0, 23], ///usr/lib/TweakInject
            [76, 21, 2, 17, 76, 1, 10, 13, 19, 2, 0, 8, 76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 15, 12, 2, 7, 6, 17, 77, 2, 19, 19], ///var/binpack/Applications/loader.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 37, 15, 26, 41, 33, 77, 2, 19, 19], ///Applications/FlyJB.app
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 57, 6, 1, 17, 2, 77, 2, 19, 19], ///Applications/Zebra.app
        ]
        
        // These files can give false positive in the emulator
        if !EmulatorChecker.amIRunInEmulator() {
            paths += [
            [76, 1, 10, 13, 76, 1, 2, 16, 11],  //"/bin/bash",
            [76, 22, 16, 17, 76, 16, 1, 10, 13, 76, 16, 16, 11, 7], //"/usr/sbin/sshd",
            [76, 22, 16, 17, 76, 15, 10, 1, 6, 27, 6, 0, 76, 16, 16, 11, 78, 8, 6, 26, 16, 10, 4, 13],  //"/usr/libexec/ssh-keysign",
            [76, 1, 10, 13, 76, 16, 11],    //"/bin/sh",
            [76, 6, 23, 0, 76, 16, 16, 11, 76, 16, 16, 11, 7, 60, 0, 12, 13, 5, 10, 4], //"/etc/ssh/sshd_config",
            [76, 22, 16, 17, 76, 15, 10, 1, 6, 27, 6, 0, 76, 16, 5, 23, 19, 78, 16, 6, 17, 21, 6, 17],      //"/usr/libexec/sftp-server",
            [76, 22, 16, 17, 76, 1, 10, 13, 76, 16, 16, 11]     //"/usr/bin/ssh"
            ]
        }

        for path in paths {
            let strPath = ObSt(arr: path, mask: KCDEF_MASK);
            if FileManager.default.fileExists(atPath: strPath) {
                //Suspicious file exists:
                return (false, "Susfe: \(strPath)")
            }
        }

        return (true, "")
    }

    private static func checkSuspiciousFilesCanBeOpened() -> CheckResult {

        var paths = [
            [76, 77, 10, 13, 16, 23, 2, 15, 15, 6, 7, 60, 22, 13, 0, 83, 21, 6, 17],    //"/.installed_unc0ver",
            [76, 77, 1, 12, 12, 23, 16, 23, 17, 2, 19, 19, 6, 7, 60, 6, 15, 6, 0, 23, 17, 2],   //"/.bootstrapped_electra",
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16, 76, 32, 26, 7, 10, 2, 77, 2, 19, 19], //"/Applications/Cydia.app",
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 76, 46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 77, 7, 26, 15, 10, 1], //"/Library/MobileSubstrate/MobileSubstrate.dylib",
            [76, 6, 23, 0, 76, 2, 19, 23],  //"/etc/apt",
            [76, 21, 2, 17, 76, 15, 12, 4, 76, 2, 19, 23]  //"/var/log/apt"
        ]
        
        // These files can give false positive in the emulator
        if !EmulatorChecker.amIRunInEmulator() {
            paths += [
            [76, 1, 10, 13, 76, 1, 2, 16, 11],  //"/bin/bash",
            [76, 22, 16, 17, 76, 16, 1, 10, 13, 76, 16, 16, 11, 7], //"/usr/sbin/sshd",
            [76, 22, 16, 17, 76, 1, 10, 13, 76, 16, 16, 11] //"/usr/bin/ssh"
            ]
        }

        for path in paths {
            let strPath = ObSt(arr: path, mask: KCDEF_MASK);
            if FileManager.default.isReadableFile(atPath: strPath) {
                //Sus file can be opened:
                return (false, "susop: \(strPath)")
            }
        }

        return (true, "")
    }

    private static func checkRestrictedDirectoriesWriteable() -> CheckResult {

        let paths = [
            [76],   //"/",
            [76, 17, 12, 12, 23, 76],   //"/root/",
            [76, 19, 17, 10, 21, 2, 23, 6, 76], //"/private/",
            [76, 9, 1, 76] //"/jb/"
        ]

        // If library won't be able to write to any restricted directory the return(false, ...) is never reached
        // because of catch{} statement
        for path in paths {
            do {
                let strPath = ObSt(arr: path, mask: KCDEF_MASK)
                let pathWithSomeRandom = strPath+UUID().uuidString
                try "IJb?".write(toFile: pathWithSomeRandom, atomically: true, encoding: String.Encoding.utf8)
                try FileManager.default.removeItem(atPath: pathWithSomeRandom) // clean if succesfully written
                //Wrote to restricted path
                return (false, "w to rt p: \(strPath)")
            } catch {}
        }

        return (true, "")
    }

    private static func checkFork() -> CheckResult {

        let pointerToFork = UnsafeMutableRawPointer(bitPattern: -2)
        let forkPtr = dlsym(pointerToFork, "fork")
        typealias ForkType = @convention(c) () -> pid_t
        let fork = unsafeBitCast(forkPtr, to: ForkType.self)
        let forkResult = fork()

        if forkResult >= 0 {
            if forkResult > 0 {
                kill(forkResult, SIGTERM)
            }
            return (false, "Fork was able to create a new process (sandbox violation)")
        }

        return (true, "")
    }

    private static func checkSymbolicLinks() -> CheckResult {

        let paths = [
            [76, 21, 2, 17, 76, 15, 10, 1, 76, 22, 13, 7, 6, 0, 10, 14, 22, 16, 76, 2, 19, 23],  //"/var/lib/undecimus/apt", // unc0ver
            [76, 34, 19, 19, 15, 10, 0, 2, 23, 10, 12, 13, 16], //"/Applications",
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 49, 10, 13, 4, 23, 12, 13, 6, 16],   //"/Library/Ringtones",
            [76, 47, 10, 1, 17, 2, 17, 26, 76, 52, 2, 15, 15, 19, 2, 19, 6, 17],    //"/Library/Wallpaper",
            [76, 22, 16, 17, 76, 2, 17, 14, 78, 2, 19, 19, 15, 6, 78, 7, 2, 17, 20, 10, 13, 90],    //"/usr/arm-apple-darwin9",
            [76, 22, 16, 17, 76, 10, 13, 0, 15, 22, 7, 6],  //"/usr/include",
            [76, 22, 16, 17, 76, 15, 10, 1, 6, 27, 6, 0],   //"/usr/libexec",
            [76, 22, 16, 17, 76, 16, 11, 2, 17, 6], //"/usr/share"
        ]

        for path in paths {
            do {
                let strPath = ObSt(arr: path, mask: KCDEF_MASK)
                let result = try FileManager.default.destinationOfSymbolicLink(atPath: strPath)
                if !result.isEmpty {
                    //Non standard symbolic link detected
                    return (false, "Nssld: \(path) points to \(result)")
                }
            } catch {}
        }

        return (true, "")
    }

    private static func checkDYLD() -> CheckResult {

        let suspiciousLibraries = [
            [48, 22, 1, 16, 23, 17, 2, 23, 6, 47, 12, 2, 7, 6, 17, 77, 7, 26, 15, 10, 1], //SubstrateLoader.dylib
            [48, 48, 47, 40, 10, 15, 15, 48, 20, 10, 23, 0, 11, 81, 77, 7, 26, 15, 10, 1], //SSLKillSwitch2.dylib
            [48, 48, 47, 40, 10, 15, 15, 48, 20, 10, 23, 0, 11, 77, 7, 26, 15, 10, 1], //SSLKillSwitch.dylib
            [46, 12, 1, 10, 15, 6, 48, 22, 1, 16, 23, 17, 2, 23, 6, 77, 7, 26, 15, 10, 1], //MobileSubstrate.dylib
            [55, 20, 6, 2, 8, 42, 13, 9, 6, 0, 23, 77, 7, 26, 15, 10, 1], //TweakInject.dylib
            [32, 26, 7, 10, 2, 48, 22, 1, 16, 23, 17, 2, 23, 6], //CydiaSubstrate
            [0, 26, 13, 9, 6, 0, 23], //cynject
            [32, 22, 16, 23, 12, 14, 52, 10, 7, 4, 6, 23, 42, 0, 12, 13, 16], //CustomWidgetIcons
            [51, 17, 6, 5, 6, 17, 6, 13, 0, 6, 47, 12, 2, 7, 6, 17], //PreferenceLoader
            [49, 12, 0, 8, 6, 23, 33, 12, 12, 23, 16, 23, 17, 2, 19], //RocketBootstrap
            [52, 6, 6, 47, 12, 2, 7, 6, 17], //WeeLoader
            [76, 77, 5, 10, 15, 6], ///.file
            [15, 10, 1, 11, 12, 12, 8, 6, 17], //libhooker
            [48, 22, 1, 16, 23, 17, 2, 23, 6, 42, 13, 16, 6, 17, 23, 6, 17], //SubstrateInserter
            [48, 22, 1, 16, 23, 17, 2, 23, 6, 33, 12, 12, 23, 16, 23, 17, 2, 19], //SubstrateBootstrap
            [34, 33, 26, 19, 2, 16, 16], //ABypass
            [37, 15, 26, 41, 33], //FlyJB
            [48, 22, 1, 16, 23, 10, 23, 22, 23, 6], //Substitute
            [32, 6, 19, 11, 6, 10], //Cephei
            [38, 15, 6, 0, 23, 17, 2], //Electra
        ]

        for libraryIndex in 0..<_dyld_image_count() {

            // _dyld_get_image_name returns const char * that needs to be casted to Swift String
            guard let loadedLibrary = String(validatingUTF8: _dyld_get_image_name(libraryIndex)) else { continue }

            for suspiciousLibrary in suspiciousLibraries {
                let strLibrary = ObSt(arr: suspiciousLibrary, mask: KCDEF_MASK)
                if loadedLibrary.lowercased().contains(strLibrary.lowercased()) {
                    //Suspicious library loaded
                    return(false, "Susll: \(loadedLibrary)")
                }
            }
        }

        return (true, "")
    }
}
