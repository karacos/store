<% import karacos %>
<% import sys, traceback %>
% try:
	<% request = karacos.serving.get_request() %>
	<% session = karacos.serving.get_session() %>
	% if 'store_id' in request.str_params and 'base_id' in request.str_params:
		<% instance = karacos.base.db[request.str_params['base_id']].db[request.str_params['store_id']] %>
try {
	(function(){
		store = KaraCos.Store;
		store.show_page = function(){
			var store = this;
			console.log("Running show_page");
			store.page = {};
			try {
				var template,
				len;
				jQuery.ajax({ url: "/fragment/get_items_list.jst",
					context: document.body,
					type: "GET",
					async: false,
					success: function(jstsrc) {
						template = jsontemplate.Template(jstsrc, KaraCos.jst_options);
					}});
				jQuery.ajax({ url: store.store_url+"/get_items_list",
					dataType: "json",
					async: false,
					contentType: 'application/json',
					context: document.body,
					type: "GET",
					success: function(data) {
						var main_content = KaraCos('#MainContent');
						console.log("items list fetched");
						try {
							main_content.empty();
							main_content.append(template.expand(data));
							main_content.find('.karacos_store_item').panel({
								collapsible:false
							});
//						.sortable({
//								placeholder: "ui-state-highlight"
//							});
							store.activate_item_cart_buttons();							
						} catch(e) {
							console.log("Exception in show_page");
							console.log(e);
						}
					}
				});
			} catch(e) {
				console.log(e);
			}
		};
	})(KaraCos);
} catch (e) {
	console.log(e);
}
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