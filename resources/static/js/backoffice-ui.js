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
			elem.accordion({
				autoHeight: false,
				navigation: true,
				scrollable: true});
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
			elem.find(".add_tracking_number").each(
				function(i,trckbtn) {
					var $trckbtn = KaraCos.$(trckbtn),
					model;
					$trckbtn.button();
					model = VIE.ContainerManager.getInstanceForContainer($trckbtn.closest("[about]"));
					$trckbtn.button().click(
						function(event){
							if (typeof backoffice.cart_window === "undefined") {
								backoffice.cart_window = KaraCos('#kc_backoffice_cart');
								if (backoffice.cart_window.length === 0) {
									backoffice.cart_window = KaraCos('<div id="kc_backoffice_cart"/>');
									KaraCos('body').append(backoffice.cart_window);
								}
							}
							backoffice.cart_window.empty().append('<form>Tracking number : <input type="TEXT" name="tracking_number"/> <br/>' +
									'Transporter : <input type="TEXT" name="shipment_supplier"/><br/><button>Valider</button></form>');
							backoffice.cart_window.dialog({width: '500px', modal:true});
							backoffice.cart_window.dialog('show');
							backoffice.cart_window.find("button").button().click(
								function(event) {
									var params = {};
									event.stopImmediatePropagation();
									event.preventDefault();
									$.each($(this).closest('form').serializeArray(), function(i, field) {
										if (field.name === "method") {
											method = field.value;
										} else {
											params[field.name] = field.value;
										}
									}); // each
									params['cart_id'] = model.get('cart_id'); 
									KaraCos.action({
										url: store.store_url+"/_backoffice",
										method: 'process_cart_shipping',
										async: false,
										params: params,
										callback: function(data) {
											if (data.success) {
												backoffice.cart_window.empty().text("Le numero de suivi est renseigne");
												backoffice.elem.find('#store_backoffice_actions').tabs('load', 2);
												}
											}
										});
									
								});
						});
				});
			elem.find(".show_cart").each(
				function(i, showbtn){
					var $showbtn = KaraCos.$(showbtn),
						model;
					model = VIE.ContainerManager.getInstanceForContainer($showbtn.closest("[about]"));
					$showbtn.button().click(
						function(event){
							KaraCos.action({
								url: store.store_url,
								method: 'get_cart',
								async: false,
								params: {'cart_id': model.get('cart_id')},
								callback: function(data) {
									KaraCos.$.ajax({ url: "/fragment/show_cart.jst",
										async: false,
										context: document.body,
										type: "GET",
										success: function(tmplsrc) {
											var template = jsontemplate.Template(tmplsrc, KaraCos.jst_options);
											if (typeof backoffice.cart_window === "undefined") {
												backoffice.cart_window = KaraCos('#kc_backoffice_cart');
												if (backoffice.cart_window.length === 0) {
													backoffice.cart_window = KaraCos('<div id="kc_backoffice_cart"/>');
													KaraCos('body').append(backoffice.cart_window);
												}
											}
											backoffice.cart_window.empty().append(template.expand(data.result));
											backoffice.cart_window.dialog({width: '500px', modal:true});
											backoffice.cart_window.dialog('show');
											backoffice.cart_window.find("button").button().click(
												function(event){
													KaraCos.action({
														url: store.store_url+"/_backoffice",
														method: 'prepare_cart',
														async: false,
														params: {'cart_id': model.get('cart_id')},
														callback: function(data) {
															if (data.success) {
																backoffice.cart_window.empty().text("Cette commande est consideree !");
																backoffice.elem.find('#store_backoffice_actions').tabs('load', 2);
																}
															}
														});
												});
										}
									})
								}
							});
						});
				});
			this.management_ui_elem = elem;
			return backoffice;
		}
	}
	KaraCos.Store.BackOffice = new bo(store);
});				