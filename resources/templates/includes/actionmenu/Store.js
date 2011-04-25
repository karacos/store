<% import karacos %>
<% import sys, traceback %>
% try:
<% request = karacos.serving.get_request() %>
<% session = karacos.serving.get_session() %>
% if 'instance_id' in request.str_params and 'base_id' in request.str_params:
	<% instance = karacos.base.db[request.str_params['base_id']].db[request.str_params['instance_id']] %>
	<% user_auth = instance.__domain__.get_user_auth() %>
	<% isstaff = 'anonymous@%s' % instance.__domain__['name'] != user_auth['name'] %>
	## 'group.staff@%s' % instance.__domain__['name'] in user_auth['groups'] %>
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
						}
					});
					KaraCos.authManager.authenticationHeader();
				});
				toolbar.prepend(button);
		})(toolbar);
	% endif
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