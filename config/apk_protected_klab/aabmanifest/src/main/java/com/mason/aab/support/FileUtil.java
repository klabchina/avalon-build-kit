package com.mason.aab.support;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;

public class FileUtil {
    public static void saveFile(String filepath,byte [] data)throws Exception{
        if(data != null)
        {
            File file  = new File(filepath);
            if(file.exists()){
                file.delete();
            }
            FileOutputStream fos = new FileOutputStream(file);
            fos.write(data,0,data.length);
            fos.flush();
            fos.close();
        }
    }

    public static void saveFile(String filepath, String data)throws Exception{
        // 创建文件对象
        File fileText = new File(filepath);
        // 向文件写入对象写入信息
        FileWriter fileWriter = new FileWriter(fileText);

        // 写文件
        fileWriter.write(data);
        // 关闭
        fileWriter.close();

    }
}
