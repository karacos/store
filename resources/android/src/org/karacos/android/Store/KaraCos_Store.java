package org.karacos.android.Store;

import android.R;
import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public class KaraCos_Store extends Activity {
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
     // We want to view some very simple text, so we need a TextView
        TextView tv = new TextView(this);
        // Put some text to the newly created TextVIew
        tv.setText("Hello Android - by: anddev.org n" +
        		"This is soooo simple =D ");
        // Tell our App to display the textView
        this.setContentView(tv); 
    }
}