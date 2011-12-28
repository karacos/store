define("store/actions", ["jquery"], function($){
	var karacos, auth, storeActions;
	function StoreActions(config) {
		if (typeof config === "undefined") {
			config = {};
		}
		this.config = config;
		this.dialog_elem = config.dialog_elem;
		storeActions = this;
		$('body').bind('kcauth', function(){
			karacos = KaraCos;
			auth = karacos.authManager;
			if (typeof storeActions.config.url === "undefined") {
				storeActions.config.url = karacos.config.page_url;
			}
		});
	}
	
	$.extend(StoreActions.prototype,{
		service_handlers: {
			'paypal_express': function(data) {
			},
			'paybox': function(data) {
				if (data.success) {
					var $form, $field; 
					if (typeof data.data === "object") {
						if (typeof data.data.target_url === "string") {
							$form = $('<form/>');
							$('body').empty().append('<h2>redirecting to payment page</h2>');
							$form.attr("method", "POST");
							$form.attr("action", data.data.target_url);
							$.each(data.data.params, function(k,v){
								$field = $('<input type="hidden"/>');
								$field.attr("name",k);
								$field.attr("value",v);
								$form.append($field);
							});
							$('body').append($form);
							$form.submit();
						}
					}
				} else {
					if (typeof data.data === "object") {
						if (typeof data.data.errurl === "string") {
							document.location = data.data.errurl;
							return;
						} else {
						}
					} else {
					}
				}
			}
		},
		handlers: {
			'pay_dummy_cart': function(data) {
				if (typeof data.data === "object") {
					if (typeof data.data.service === "string") {
						if (typeof storeActions.service_handlers[data.data.service] === "function") {
							storeActions.service_handlers[data.data.service](data);
						}
					}
				}
			}
		},
		handle_action_form: function(action_name) {
			if (typeof storeActions.handlers[action_name] === "function") {
				$('[kc-action="'+action_name+'"]').closest('form').submit(
						function(e) {
							var
								$form = $(e.target),
								method,
								params = {};
							e.preventDefault();
							e.stopImmediatePropagation();
							$('[kc-action="'+action_name+'"]').button("disable");
							$.each($form.serializeArray(), function(i,e) {
								if (e.name === "method") {
									method = e.value;
								} else {
									params[e.name] = e.value;
								}
							});
							$.ajax({
								url: $form.attr('action'),
								type: 'POST',
								dataType: "json",
								cache: false,
								contentType: 'application/json',
								context: document.body,
								async: true,
								data: $.toJSON({method: method, id:1, params: params}),
								success: function(data) {
									storeActions.handlers[action_name](data);
								}
							})
						});
			}
		},
	});
	return StoreActions;
})