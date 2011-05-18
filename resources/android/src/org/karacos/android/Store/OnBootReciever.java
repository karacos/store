package org.karacos.android.Store;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.ComponentName;
import android.util.Log;

public class OnBootReciever extends BroadcastReceiver {

	@Override
	public void onReceive(Context context, Intent intent) {
		Log.d("OnBootReciever", "Recieved an event>>>");
		if ("android.intent.action.BOOT_COMPLETED".equals(intent.getAction())) { 
			Log.d("OnBootReciever", "Got the Boot Event>>>");
			Log.d("OnBootReciever", "Starting StoreWatcher>>>");
			context.startService(new Intent().setComponent(new ComponentName(
					context.getPackageName(), StoreWatcher.class.getName())));			
		}

	}

}
