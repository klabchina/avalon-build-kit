package org.hackcode;

import java.io.File;
import java.lang.ref.WeakReference;
import java.lang.reflect.Array;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

import android.app.ActivityManager;
import android.app.Application;
import android.app.Instrumentation;
import android.app.Presentation;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.os.IBinder;
import android.os.Process;
import android.os.RemoteException;
import android.system.Os;
import android.util.Log;

import org.hackcode.service.IsolatedService;

import dalvik.system.DexClassLoader;

/**
 * Created by Mason on 2018/2/8.
 */

public class ProxyApplication extends Application{

    private long timeTick;
	static{
		System.loadLibrary("klabniceway");
		System.loadLibrary("assistant1");
		System.loadLibrary("assistant2");
	}
	
	@Override
	public void onCreate() {
		try {

			if (!isUIProcess())
			{
				return;
			}

			// 如果源应用配置有Appliction对象，则替换为源应用Applicaiton，以便不影响源程序逻辑。  
			String appClassName = "com.mason.sotest.StartApplication";
			/**
			 * 调用静态方法android.app.ActivityThread.currentActivityThread
			 * 获取当前activity所在的线程对象
			 */
			Object currentActivityThread = ReflectUtils.invokeStaticMethod(  
			        "android.app.ActivityThread", "currentActivityThread",  
			        new Class[] {}, new Object[] {}); 
			/**
			 * 获取currentActivityThread中的mBoundApplication属性对象，该对象是一个
			 *  AppBindData类对象，该类是ActivityThread的一个内部类
			 */
			Object mBoundApplication = ReflectUtils.getFieldObject(  
			        "android.app.ActivityThread", currentActivityThread,  
			        "mBoundApplication"); 
			/**
			 * 获取mBoundApplication中的info属性，info 是 LoadedApk类对象
			 */
			Object loadedApkInfo = ReflectUtils.getFieldObject(  
			        "android.app.ActivityThread$AppBindData",  
			        mBoundApplication, "info");  
			 if(null == loadedApkInfo){
			    	Log.v("KlabHack", "[KlabHack]=>onCreate()=>loadedApkInfo is null!!!");
			  }else{
				  Log.v("KlabHack", "[KlabHack]=>onCreate()=>loadedApkInfo:" + loadedApkInfo);
			  }
			
			/**
			 * loadedApkInfo对象的mApplication属性置为null
			 */
			ReflectUtils.setFieldObject("android.app.LoadedApk", "mApplication",  
			        loadedApkInfo, null);  
			
			/**
			 * 获取currentActivityThread对象中的mInitialApplication属性
			 * 这货是个正牌的 Application
			 */
			Object oldApplication = ReflectUtils.getFieldObject(  
			        "android.app.ActivityThread", currentActivityThread,  
			        "mInitialApplication");

			/**
			 * 获取currentActivityThread对象中的mAllApplications属性
			 * 这货是 装Application的列表
			 */
			@SuppressWarnings("unchecked")
			ArrayList<Application> mAllApplications = (ArrayList<Application>) ReflectUtils  
			        .getFieldObject("android.app.ActivityThread",  
			                currentActivityThread, "mAllApplications"); 
			
			//列表对象终于可以直接调用了 remove调了之前获取的application 抹去记录的样子
			mAllApplications.remove(oldApplication); 
			
			/**
			 * 获取前面得到LoadedApk对象中的mApplicationInfo属性，是个ApplicationInfo对象
			 */
			ApplicationInfo appinfo_In_LoadedApk = (ApplicationInfo) ReflectUtils  
			        .getFieldObject("android.app.LoadedApk", loadedApkInfo,  
			                "mApplicationInfo"); 
			
			/**
			 * 获取前面得到AppBindData对象中的appInfo属性，也是个ApplicationInfo对象
			 */
			ApplicationInfo appinfo_In_AppBindData = (ApplicationInfo) ReflectUtils  
			        .getFieldObject("android.app.ActivityThread$AppBindData",  
			                mBoundApplication, "appInfo"); 
			
			//把这两个对象的className属性设置为从meta-data中获取的被加密apk的application路径
			appinfo_In_LoadedApk.className = appClassName;  
			appinfo_In_AppBindData.className = appClassName; 
			/**
			 * 调用LoadedApk中的makeApplication 方法 造一个application
			 * 前面改过路径了 
			 */
			Application app = (Application) ReflectUtils.invokeMethod(  
			        "android.app.LoadedApk", "makeApplication", loadedApkInfo,  
			        new Class[] { boolean.class, Instrumentation.class },  
			        new Object[] { false, null });  
			ReflectUtils.setFieldObject("android.app.ActivityThread",  
			        "mInitialApplication", currentActivityThread, app);



			if(null == app)
			{
				Log.e("KlabHack", "[KlabHack]=>onCreate()=>app is null!!!");
            }
            else
            {
                SharedPreferences sp = getSharedPreferences("first_load", Context.MODE_PRIVATE);
                boolean isLoaded = sp.getBoolean("is_loaded", false);
                if (!isLoaded)
                {
                    SharedPreferences.Editor ed = sp.edit();
                    ed.putBoolean("is_loaded", true);
                    ed.commit();
                }
                app.onCreate();
            }

            //magisk service protected
			final Context currentContext = this;
			Thread th = new Thread(new Runnable() {
				@Override
				public void run() {
					while (true)
					{
						try {
							if (serviceBinder == null)
							{
								Intent intent = new Intent(currentContext, IsolatedService.class);
								/*Binding to an isolated service */
								getApplicationContext().bindService(intent, mIsolatedServiceConnection, BIND_AUTO_CREATE);
							}
							else
							{
								Class proxy = Class.forName("org.hackcode.ProxyApplication");
								Random ra = new Random();

								Method methodItem = proxy.getMethod("checkMg" + String.valueOf(ra.nextInt(30)));
								methodItem.invoke(currentContext);
							}
							Thread.sleep(10000);

						}
						catch (InterruptedException e) {
							try {
								Thread.sleep(10000);
							} catch (InterruptedException ex) {
								ex.printStackTrace();
							}
						}
						catch (SecurityException sex)
						{
							try {
								Thread.sleep(10000);
							} catch (InterruptedException ex) {
								ex.printStackTrace();
							}
						}
						catch (Exception ex)
						{
							try {
								Thread.sleep(10000);
							} catch (InterruptedException ext) {
								ex.printStackTrace();
							}
						}

					}
				}
			});
			th.start();
		}
		catch (Exception e)
        {
			Log.v("KlabHack", "[KlabHack]=>onCreate() " + Log.getStackTraceString(e));
		}
	}

	public boolean isUIProcess() {
		ActivityManager am = ((ActivityManager) getSystemService(Context.ACTIVITY_SERVICE));
		List<ActivityManager.RunningAppProcessInfo> processInfos = null;
		try
		{
			processInfos = am.getRunningAppProcesses();
		}
		catch (SecurityException ex)
		{
			return false;
		}
		String mainProcessName = getPackageName();
		int myPid = android.os.Process.myPid();
		for (ActivityManager.RunningAppProcessInfo info : processInfos) {
			if (info.pid == myPid && mainProcessName.equals(info.processName)) {
				return true;
			}
		}
		return false;
	}
	
//	void exchangeDex(String libPath, ClassLoader parent, Object loadedApk)
//    {
//        String odexPath = this.getDir("assets", Context.MODE_PRIVATE).getAbsolutePath();
//        String targetFilePath = odexPath + "/TargetApk.zip";
//        DexClassLoader dLoader = new DexClassLoader(targetFilePath, odexPath, libPath, parent);
//
//        ReflectUtils.setFieldObject("android.app.LoadedApk", "mClassLoader", loadedApk, dLoader);
//    }

	@Override
	public void attachBaseContext(Context base)
	{

	    timeTick = System.currentTimeMillis();
		super.attachBaseContext(base);


		if (!isUIProcess())
		{
			return;
		}
		
		try {
			
			String targetFilePath = get_target((Application)this);
            File fr = new File(targetFilePath);
            boolean isLoaded = fr.exists();

			SharedPreferences sp = getSharedPreferences("vCode", Context.MODE_PRIVATE);
            int lastVersionCode = sp.getInt("version_code", 0);
            boolean isNewInstall = false;

            PackageInfo pi= getPackageManager().getPackageInfo(getPackageName(), 0);
            if (lastVersionCode != pi.versionCode)
            {
                isNewInstall = true;
                SharedPreferences.Editor ed = sp.edit();
                ed.putInt("version_code", pi.versionCode);
                ed.commit();
                if (isLoaded)
                {
                    fr.delete();
                }
            }

            Object currentActivityThread = ReflectUtils.invokeStaticMethod("android.app.ActivityThread", "currentActivityThread", new Class[] {}, new Object[] {});
			String packageName = getPackageName();
			Map mPackages = (Map) ReflectUtils.getFieldObject("android.app.ActivityThread", currentActivityThread, "mPackages");
			WeakReference wr = (WeakReference) mPackages.get(packageName);

//			Log.e("TestABI", packageName);
			ArrayList<String> libSearchPaths = new ArrayList<String>();
			libSearchPaths.add("/data/data/" + packageName + "/lib");
			libSearchPaths.add(pi.applicationInfo.nativeLibraryDir);
			libSearchPaths.add(pi.applicationInfo.sourceDir + "!" + "/lib");
			StringBuilder sb = new StringBuilder();
			for (String item : libSearchPaths)
			{
				sb.append(item);
				sb.append(File.pathSeparator);
			}

			if (isLoaded && !isNewInstall)
            {
				niceway_start((Application)this, sb.toString(), base.getClassLoader().getParent(), wr.get());
            }
            else
            {
                start((Application)this, sb.toString(), base.getClassLoader().getParent(), wr.get());
            }
		} catch (Exception e) {
			Log.v("KlabHack", "[KlabHack]=>attachBaseContext() " + Log.getStackTraceString(e));
		}
		

		
	}

	private IIsolatedService serviceBinder;

	private ServiceConnection mIsolatedServiceConnection = new ServiceConnection() {
		@Override
		public void onServiceConnected(ComponentName componentName, IBinder iBinder) {
			serviceBinder =  IIsolatedService.Stub.asInterface(iBinder);

			try {
				Class proxy = Class.forName("org.hackcode.ProxyApplication");
				Random ra = new Random();

				Method methodItem = proxy.getMethod("checkMg" + String.valueOf(ra.nextInt(30)));
				methodItem.invoke(ProxyApplication.this);
			} 
			catch (Exception ex)
			{
				ex.printStackTrace();
				return;
			}
		}

		@Override
		public void onServiceDisconnected(ComponentName componentName) {
			serviceBinder = null;
		}
	};

	private void checkTimeTick()
    {
//        long tickNew = System.currentTimeMillis();
//        Log.e("KlabHackTimeTick", Long.toString(tickNew - timeTick));
//        timeTick = tickNew;
    }

    public static native boolean mg_present(int pid);

    private native String get_target(Application wrapper);

    private native void start(Application wrapper, String libraryPath, ClassLoader parent, Object loadedApk);

	private native void niceway_start(Application wrapper, String libraryPath, ClassLoader parent, Object loadedApk);



	public void checkMg0() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg1() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg2() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg3() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg4() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg5() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg6() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg7() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg8() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg9() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg10() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg11() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg12() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg13() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg14() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg15() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg16() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg17() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg18() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg19() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg20() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg21() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg22() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg23() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg24() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg25() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg26() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg27() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg28() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg29() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

	public void checkMg30() throws RemoteException
	{
		boolean res = serviceBinder.checkPresent(android.os.Process.myPid());
		if (res)
		{
			Process.killProcess(Process.myPid());
		}
	}

}
