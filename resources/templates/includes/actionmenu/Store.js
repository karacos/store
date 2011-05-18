<% import karacos %>
<% import sys, traceback %>
% try:
<% request = karacos.serving.get_request() %>
<% session = karacos.serving.get_session() %>
% if 'instance_id' in request.str_params and 'base_id' in request.str_params:
	<% instance = karacos.base.db[request.str_params['base_id']].db[request.str_params['instance_id']] %>
	<% user_auth = instance.__domain__.get_user_auth() %>
	<% isstaff = 'anonymous@%s' % instance.__domain__['name'] != user_auth['name'] %>
	<% node_actions = instance._get_actions() %>
	## 'group.staff@%s' % instance.__domain__['name'] in user_auth['groups'] %>
	% try:
		(function(submenu){
			var 
			item;
			actionwindow = KaraCos.actionMenu.actionWindow;
			
		
			})(submenu);
		% if 'w_browse' in instance._get_backoffice_node()._get_actions():
			(function(toolbar) {
				
				var button = KaraCos('<button">Administration boutique</button>')
					.button()
					.click(function(event) {
						var url = '${instance._get_backoffice_node()._get_action_url()}';
						History.pushState(null, null, url);
						KaraCos.$.ajax({
							url: url,
							headers: {'Karacos-Fragment': 'true'},
							success: function(data) {
								KaraCos('#MainContent').empty().append(data);
								KaraCos.authManager.authenticationHeader();
							}
						});
					});
					toolbar.prepend(button);
			})(toolbar);
		% endif
	% except:
		(function(toolbar) {
			var button = KaraCos('<button">Creer backoffice</button>')
				.button()
				.click(function(event) {
					var url = '${instance._get_action_url()}';
					KaraCos.action({
						url: url,
						method: 'create_child_node',
						async: false,
						params: {
							'name': '_backoffice',
							'type': 'StoreBackOffice',
							'base': false
						},
						callback: function(data) {
							KaraCos.authManager.authenticationHeader();
						}
					});
				});
				toolbar.prepend(button);
		})(toolbar);
	%endtry
% endif
<%include file="/includes/actionmenu/StoreParent.js"/>
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