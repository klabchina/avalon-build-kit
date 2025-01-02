package org.hackcode.service;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.system.Os;
import android.util.Log;

import org.hackcode.IIsolatedService;
import org.hackcode.ProxyApplication;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * Created by Mason on 2021-03-18.
 */
public class IsolatedService extends Service {
    private String[] blackListedMountPaths = { "/sbin/.magisk/", "/sbin/.core/mirror", "/sbin/.core/img", "/sbin/.core/db-0/magisk.db"};

    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    private final IIsolatedService.Stub mBinder = new IIsolatedService.Stub(){
        public boolean checkPresent(int mainPid){
            boolean result = false;

            File file = new File("/proc/self/mounts");

            try {
                FileInputStream fis = new FileInputStream(file);
                BufferedReader reader = new BufferedReader(new InputStreamReader(fis));
                String str;
                int count =0;
                while((str = reader.readLine()) != null && (count==0)){
                    //Log.d(TAG, "MountPath:"+ str);
                    for(String path:blackListedMountPaths){
                        if(str.contains(path)){
                            count++;
                            break;
                        }
                    }
                }
                reader.close();
                fis.close();
                if(count > 0){
                    result = true;
                }else {
                    result = ProxyApplication.mg_present(mainPid);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }

            return result;
        }
    };
}
