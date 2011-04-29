KaraCos.Store.ready(function(store) {
	bo = function(store) {
		this.store = store;
		
		this.init();
	}
	
	bo.prototype = {
		/**
		 * initialize backoffice
		 */
		init: function() {
			var backoffice = this;
			jQuery.ajax({ url: store.store_url+"/_backoffice/get_user_actions_forms",
				dataType: "json",
				async: false,
				contentType: 'application/json',
				context: document.body,
				type: "GET",
				success: function(data) {
					if (data.success) {
						backoffice.elem = KaraCos('#store_backoffice');
						backoffice.elem.find('#store_backoffice_actions').tabs();
					}
				}
			});
			
		},
		shipping_ui: function(element) {
			var backoffice = this;
			this.shipping_ui_elem = element;
			element.accordion();
			element.find('#new_shipping_rate form button').click(function(event) {
				var form = KaraCos.$(this).closest('form'),
					method,
					params = {};
				event.stopImmediatePropagation();
				event.preventDefault();
				
				$.each(form.serializeArray(), function(i, field) {
					if (field.name === "method") {
						method = field.value;
					} else {
						params[field.name] = field.value;
					}
				}); // each
				KaraCos.action({ url: form.attr('action'),
					method: method,
					async: false,
					params: params,
					callback: function(data) {
//						backoffice.shipping_ui.dialog("destroy");
						
						KaraCos.$.ajax({ url: "/fragment/view_shipping_rates?office_id=" +
									store.office.id + "&base_id=" + store.office.db,
							async: false,
							context: document.body,
							type: "GET",
							success: function(data) {
								backoffice.shipping_ui_elem.accordion('activate', 0);
								backoffice.shipping_ui_elem.find("#existing_shipping_rates")
									.empty()
									.append(data);
							},
							failure: function() {
								alert('error');
							}
						});
						
					},
					error: function(data) {
						console.log(data);
						alert('error');
					}
				}); // post
			});
		},
		payment_ui: function(elem,forms) {
			var backoffice = this;
//			console.log(forms);
			this.payment_ui_elem = elem;
			KaraCos.$.ajax({ url: "/fragment/set_services.jst",
				async: false,
				context: document.body,
				type: "GET",
				success: function(data) {
					var template = jsontemplate.Template(data, KaraCos.jst_options);
					try {
						backoffice.payment_ui_elem.empty()
						.append(template.expand({'store_url':store.store_url, 'forms': forms})).accordion();
						
					} catch (e) {
						console.log(e);
					}
				}});
		},
		carts_management_ui: function(elem) {
			var backoffice = this;
			backoffice.carts_management_elem = elem;
			elem.accordion();
			elem.find(".karacos_button").each(
					function(i,kcbtn) {
						var $kcbtn = KaraCos.$(kcbtn);
						$kcbtn.button();
						KaraCos.button($kcbtn,
								function(result){
							if (typeof result.error !== "undefined") {
								KaraCos.alert(result.error.message,[{'label': 'Ok'}]);
							} else {
								KaraCos.alert(result.message,[{'label': 'Ok'}]);
								backoffice.elem.find('#store_backoffice_actions').tabs('load', 2);
							}
						});
					});
			
			this.management_ui_elem = elem;
			return backoffice;
		}
	}
	KaraCos.Store.BackOffice = new bo(store);
});				