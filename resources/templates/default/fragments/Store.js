<% import karacos %>
<% import sys, traceback %>
% try:
	<% request = karacos.serving.get_request() %>
	<% session = karacos.serving.get_session() %>
	% if 'store_id' in request.str_params and 'base_id' in request.str_params:
		<% instance = karacos.base.db[request.str_params['base_id']].db[request.str_params['store_id']] %>
	define('store/show_page',['jquery'], function($){
		store = KaraCos.Store;
		if (typeof store.show_page === "undefined"){
			store.show_page = function(count,page){
				$($("#store_page_nav_header li").get(page)).addClass('ui-state-over');
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
							KaraCos.action({ url: store.store_url,
								method: "get_store_items_list",
								async: false,
								params:{count:count,page:page},
								callback: function(data) {
									var main_content = KaraCos('#StoreContent');
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
						}});
				} catch(e) {
					console.log(e);
				}
				$("#store_page_nav_header li").button().click(
						function(event){
							event.stopImmediatePropagation();
							event.preventDefault();
							var $this = $(this), url;
							url = $this.find('a').attr("href");
							History.pushState(null, null, url);
							$.ajax({
								url: url,
								headers: {'Karacos-Fragment': 'true'},
								success: function(data) {
									$('#MainContent').empty().append(data);
								}
							});
						});
					
			}; // function store.sow_page
			
		}
		return store;
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