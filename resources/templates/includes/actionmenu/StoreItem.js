<% import karacos %>
<% import sys, traceback %>
% try:
<% request = karacos.serving.get_request() %>
<% session = karacos.serving.get_session() %>
<% response = karacos.serving.get_response() %>
<% instance = None %>
%try:
	<% instance = response.__instance__ %>
%except:
	
%endtry
% if 'instance_id' in request.str_params and 'base_id' in request.str_params:
<% instance = karacos.base.db[request.str_params['base_id']].db[request.str_params['instance_id']] %>
% endif

% if instance != None:
<% node_actions = instance._get_actions() %>
(function(submenu){
	var 
		item, subsubmenu,
		actionwindow = KaraCos.actionMenu.actionWindow;
	% if 'publish_node' in node_actions:
		
		item = KaraCos('<li class="publish_node_storeitem"><a href="#">Mettre en vente</a></li>');
		item.click(function(){
			KaraCos.action({ url: "${instance._get_action_url()}",
				method: 'publish_node',
				async: false,
				params: {},
				callback: function(data) {
					if (data.success) {
						submenu.find(".unpublish_node_storeitem").show();
						submenu.find(".publish_node_storeitem").hide();
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
		
		item = KaraCos('<li class="unpublish_node_storeitem"><a href="#">Retirer de la vente</a></li>');
		item.click(function(){
			KaraCos.action({ url: "${instance._get_action_url()}",
				method: 'unpublish_node',
				async: false,
				params: {},
				callback: function(data) {
					if (data.success) {
						submenu.find(".publish_node_storeitem").show();
						submenu.find(".unpublish_node_storeitem").hide();
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
		submenu.find(".unpublish_node_storeitem").show();
		submenu.find(".publish_node_storeitem").hide();
	%else:
		submenu.find(".publish_node_storeitem").show();
		submenu.find(".unpublish_node_storeitem").hide();
	%endif
	% if 'set_main_pic' in node_actions:
		item = KaraCos('<li id="unpublish_node_storeitem"><a href="#">Image principale</a></li>');
		item.click(function(){
			KaraCos.Browser({'panels':
				[{  type:'grid',
					template: '/fragment/set_main_pic_grid.jst',
					selectiontype: 'single',
					datasource:{
						type:'json',
						url:'${instance._get_action_url()}',
						params: {method:'get_atts', id:1, params:{}}
					},
					onselect: function($item){
						var img_name = $item.closest('[about]').attr('about').split(':')[3];
						console.log("Setting " + img_name + " as main pic.");
						KaraCos.action({ url: "${instance._get_action_url()}",
							method: 'set_main_pic',
							async: false,
							params: {main_pic:img_name},
							callback: function(data) {
								if (data.success) {
									KaraCos.Browser.dialog('hide');
								}
							}
						});
					}
				}]
			});
		});
		submenu.append(item);
	% endif
	item = KaraCos('<li><a href="#">Resource</a><li>');
	subsubmenu = KaraCos('<ul></ul>');
	(function(submenu) {
		<%include file="/includes/actionmenu/Resource.js"/>
	})(subsubmenu);
	if (subsubmenu.find('li').length > 0) {
		submenu.append(item);
		item.append(subsubmenu);
	}
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