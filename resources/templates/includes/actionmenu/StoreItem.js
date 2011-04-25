<% import karacos %>
<% import sys, traceback %>
% try:
<% request = karacos.serving.get_request() %>
<% session = karacos.serving.get_session() %>
% if 'instance_id' in request.str_params and 'base_id' in request.str_params:
<% instance = karacos.base.db[request.str_params['base_id']].db[request.str_params['instance_id']] %>
<% node_actions = instance._get_actions() %>
(function(submenu){
	var 
		item, subsubmenu,
		actionwindow = KaraCos.actionMenu.actionWindow;
	% if 'publish_node' in node_actions:
		
		item = KaraCos('<li id="publish_node_storeitem"><a href="#">Mettre en vente</a></li>');
		item.click(function(){
			KaraCos.action({ url: "${instance._get_action_url()}",
				method: 'publish_node',
				async: false,
				params: {},
				callback: function(data) {
					if (data.success) {
						submenu.find("#unpublish_node_storeitem").show();
						submenu.find("#publish_node_storeitem").hide();
						submenu.fgmenu();
						actionwindow.empty().append(data.message);
						actionwindow.dialog({width: '400px', modal:true}).show();
						
					}
				},
				error: function(data) {
					
				}
			}); // POST login form
		});
		submenu.append(item);
	%endif
	% if 'unpublish_node' in node_actions:
		
		item = KaraCos('<li id="unpublish_node_storeitem"><a href="#">Retirer de la vente</a></li>');
		item.click(function(){
			KaraCos.action({ url: "${instance._get_action_url()}",
				method: 'unpublish_node',
				async: false,
				params: {},
				callback: function(data) {
					if (data.success) {
						submenu.find("#publish_node_storeitem").show();
						submenu.find("#unpublish_node_storeitem").hide();
						//submenu.fgmenu();
						actionwindow.empty().append(data.message);
						actionwindow.dialog({width: '400px', modal:true}).show();
						
					}
				},
				error: function(data) {
					
				}
			}); // POST login form
		});
		submenu.append(item);
	%endif
	% if instance._is_sell_open():
		submenu.find("#unpublish_node_storeitem").show();
		submenu.find("#publish_node_storeitem").hide();
	%else:
		submenu.find("#publish_node_storeitem").show();
		submenu.find("#unpublish_node_storeitem").hide();
	%endif
	item = KaraCos('<li><a href="#">Resource</a><li>');
	subsubmenu = KaraCos('<ul></ul>');
	submenu.append(item);
	(function(submenu) {
		<%include file="/includes/actionmenu/Resource.js"/>
	})(subsubmenu);
	item.append(subsubmenu);
})(submenu);
% endif
% except:
	some errors :
	<pre>
		${sys.exc_info()}
		---
		%for line in traceback.format_exc().splitlines():
			${line}
		%endfor
	</pre>
% endtry