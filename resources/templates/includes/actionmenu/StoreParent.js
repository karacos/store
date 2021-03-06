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
(function storeParentInstanceMenu(submenu){
	var 
		button,
		actionwindow = KaraCos.actionMenu.actionWindow;
	% if 'create_store_folder' in node_actions:
		item = KaraCos('<li><a href="#">Créer un dossier</a></li>');
		item.click(function clickCreateFolder(){
					KaraCos.getForm({
						url: '${instance._get_action_url()}',
						form: "create_store_folder",
						callback: function(data, form) {
							var create_child_node_template = jsontemplate.Template(form, KaraCos.jst_options);
							actionwindow.empty().append(create_child_node_template.expand(data));
							actionwindow.find('.form_create_store_folder_button').button()
							.click(function() {
								var params = {},
									method = 'create_store_folder';
								$.each($(this).closest('form').serializeArray(), function(i, field) {
									if (field.name === "method") {
										method = field.value;
									} else {
										params[field.name] = field.value;
									}
								}); // each
								KaraCos.action({ url: '${instance._get_action_url()}',
									method: method,
									async: false,
									params: params,
									callback: function(data) {
										if (data.success) {
											
											actionwindow.dialog('close');
											
										}
									},
									error: function(data) {
										
									}
								}); // POST login form
							});  // click
							actionwindow.dialog({width: '600px',
												modal:true,
												title: 'Créer un dossier'}).show();
						}
					});
				});
		submenu.append(item);
	%endif
	% if 'create_storeitem' in node_actions:
		button = KaraCos('<li><a href="#">Créer un article</a></li>');
		button.click(function(event){
			event.stopImmediatePropagation();
			event.preventDefault();
					KaraCos.getForm({
						url: '${instance._get_action_url()}',
						form: "create_storeitem",
						callback: function(data, form) {
							var create_child_node_template = jsontemplate.Template(form, KaraCos.jst_options);
							actionwindow.empty().append(create_child_node_template.expand(data));
							actionwindow.find('.form_create_storeitem_button').button()
							.click(function() {
								var params = {},
									method = 'create_storeitem';
								$.each($(this).closest('form').serializeArray(), function(i, field) {
									if (field.name === "method") {
										method = field.value;
									} else {
										params[field.name] = field.value;
									}
								}); // each
								KaraCos.action({ url: '${instance._get_action_url()}',
									method: method,
									async: false,
									params: params,
									callback: function(data) {
										if (data.success) {
											
											actionwindow.dialog('close');
											
										}
									},
									error: function(data) {
										
									}
								}); // POST login form
							});  // click
							actionwindow.dialog({width: '600px', modal:true}).show();
						}
					});
				});
		submenu.append(button);
	%endif
	% if 'unpublish_node' in node_actions:
		item = KaraCos('<li id="unpublish_node_storeitem"><a href="#">Fermer au public</a></li>');
		item.click(function(event){
			KaraCos.action({ url: '${instance._get_action_url()}',
			method: 'unpublish_node',
			async: false,
			params: {},
			callback: function(data) {
				if (data.success) {
					actionwindow.empty().append(data.message);
					actionwindow.dialog({width: '400px', modal:true}).show();
					$('#publish_node_storeitem').show();
					$('#unpublish_node_storeitem').hide();
				}
			},
			error: function(data) {
					
				}
			});
		});
		submenu.append(item);
	% endif
	% if 'publish_node' in node_actions:
		item = KaraCos('<li id="publish_node_storeitem"><a href="#">Ouvrir au public</a></li>');
		item.click(function(event){
			KaraCos.action({ url: '${instance._get_action_url()}',
			method: 'publish_node',
			async: false,
			params: {},
			callback: function(data) {
				if (data.success) {
					actionwindow.empty().append(data.message);
					actionwindow.dialog({width: '400px', modal:true}).show();
					$('#publish_node_storeitem').hide();
					$('#unpublish_node_storeitem').show();
				}
			},
			error: function(data) {
					
				}
			});
		});
		submenu.append(item);
	% endif
	% if instance._is_public():
		$('#publish_node_storeitem').hide();
		$('#unpublish_node_storeitem').show();
	%else:
		$('#publish_node_storeitem').show();
		$('#unpublish_node_storeitem').hide();
	% endif
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
