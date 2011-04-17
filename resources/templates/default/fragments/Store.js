<% import karacos %>
<% import sys, traceback %>
% try:
	<% request = karacos.serving.get_request() %>
	<% session = karacos.serving.get_session() %>
	% if 'store_id' in request.str_params and 'base_id' in request.str_params:
		<% instance = karacos.base.db[request.str_params['base_id']].db[request.str_params['store_id']] %>
	KaraCos(function(){
		try {
			var store = KaraCos.Store;
			
			store.ready(function(readystore) {
				var template,
				len;
				jQuery.ajax({ url: "/fragment/get_items_list.jst",
					context: document.body,
					type: "GET",
					async: false,
					success: function(data) {
						template = jsontemplate.Template(data, KaraCos.jst_options);
					}});
				jQuery.ajax({ url: store.store_url+"/get_items_list",
					dataType: "json",
					async: false,
					contentType: 'application/json',
					context: document.body,
					type: "GET",
					success: function(data) {
						KaraCos('#StoreContent').append(template.expand(data));
						KaraCos('#StoreContent').sortable({
							placeholder: "ui-state-highlight"
						})
						KaraCos('.karacos_store_item').panel({
							collapsible:false
						});
						KaraCos.Store.activate_item_cart_buttons();
					}});
			});
			KaraCos.Store.init_store({url:'${instance._get_action_url()}'});
		} catch(e) {
			console.log(e);
		}
			

	});
	% endif
% except:
	<pre>
	${sys.exc_info()}
	---
	% for line in traceback.format_exc().splitlines():
		${line}
	% endfor
	</pre>
%endtry