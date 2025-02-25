package org.hackcode;

import android.util.Log;

import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;  
import java.lang.reflect.Method;

/**
 * Created by Mason on 2018/2/8.
 */

public class ReflectUtils {  
      
    public static  Object invokeStaticMethod(String class_name, String method_name, Class[] pareTyple, Object[] pareVaules){  
          
        try {  
            Class obj_class = Class.forName(class_name);  
            Method method = obj_class.getMethod(method_name,pareTyple);  
            return method.invoke(null, pareVaules);  
        } catch (SecurityException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }  catch (IllegalArgumentException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
       } catch (IllegalAccessException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (NoSuchMethodException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (InvocationTargetException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (ClassNotFoundException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }  
        return null;
    }  
      
    public static  Object invokeMethod(String class_name, String method_name, Object obj ,Class[] pareTyple, Object[] pareVaules){  
          
       try {  
            Class obj_class = Class.forName(class_name);  
            Method method = obj_class.getMethod(method_name,pareTyple);  
            return method.invoke(obj, pareVaules);  
        } catch (SecurityException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }  catch (IllegalArgumentException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (IllegalAccessException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (NoSuchMethodException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (InvocationTargetException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (ClassNotFoundException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }  
        return null;  
          
    }

    public static  Object invokeDeclaredStaticMethod(String class_name, String method_name, Class[] pareTyple, Object[] pareVaules){

        try {
            Class obj_class = Class.forName(class_name);
            Method method = obj_class.getDeclaredMethod(method_name,pareTyple);
            method.setAccessible(true);
            return method.invoke(null, pareVaules);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;

    }
      
    public static Object getFieldObject(String class_name,Object obj, String filedName){  
        try {  
            Class obj_class = Class.forName(class_name);  
            Field field = obj_class.getDeclaredField(filedName);  
           field.setAccessible(true);  
            return field.get(obj);  
        } catch (SecurityException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
       } catch (NoSuchFieldException e) {  
           // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (IllegalArgumentException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (IllegalAccessException e) {  
           // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (ClassNotFoundException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }  
        return null;  
          
    }  
     
    public static Object getStaticFieldObject(String class_name, String filedName){  
          
        try {  
            Class obj_class = Class.forName(class_name);  
            Field field = obj_class.getDeclaredField(filedName);  
            field.setAccessible(true);  
           return field.get(null);  
       } catch (SecurityException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (NoSuchFieldException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
       } catch (IllegalArgumentException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (IllegalAccessException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (ClassNotFoundException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }  
        return null;  
         
    }  
      
    public static void setFieldObject(String classname, String filedName, Object obj, Object filedVaule){  
        try {  
            Class obj_class = Class.forName(classname);  
            Field field = obj_class.getDeclaredField(filedName);  
            field.setAccessible(true);  
            field.set(obj, filedVaule);  
        } catch (SecurityException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (NoSuchFieldException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (IllegalArgumentException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (IllegalAccessException e) {  
            // TODO Auto-generated catch block  
           e.printStackTrace();  
       } catch (ClassNotFoundException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }     
    }  
      
    public static void setStaticObject(String class_name, String filedName, Object filedVaule){  
        try {  
            Class obj_class = Class.forName(class_name);  
            Field field = obj_class.getDeclaredField(filedName);  
            field.setAccessible(true);  
            field.set(null, filedVaule);  
        } catch (SecurityException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (NoSuchFieldException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (IllegalArgumentException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
       } catch (IllegalAccessException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        } catch (ClassNotFoundException e) {  
            // TODO Auto-generated catch block  
            e.printStackTrace();  
        }         
    }  
  
}  