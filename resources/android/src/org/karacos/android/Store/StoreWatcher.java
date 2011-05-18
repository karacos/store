package org.karacos.android.Store;

import java.util.Timer;
import java.util.TimerTask;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;

public class StoreWatcher extends Service {
	private Timer timer = new Timer();
	public void onCreate() {
		super.onCreate();
		startService();
		}
	@Override
	public IBinder onBind(Intent arg0) {
		// TODO Auto-generated method stub
		return null;
	}
	
	private void startService() {
		timer.scheduleAtFixedRate( new TimerTask() {
			
			@Override
			public void run() {
				Log.d("StoreWatcher", "Recieved an event>>>");
			}
		}, 0, 30);
		
	}

	@Override
    public void onRebind(Intent intent) {
        super.onRebind(intent);
        Log.d("TestApp", ">>>onRebind()");
    }


    @Override
    public void onStart(Intent intent, int startId) {
        super.onStart(intent, startId);
        Log.d("TestApp", ">>>onStart()");
    }

    @Override
    public boolean onUnbind(Intent intent) {
        return super.onUnbind(intent);
    }
}
