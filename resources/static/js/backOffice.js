define('store/backOffice', ['jquery','store/Store', 'karacos'],
	function($,store, karacos) {
	bo = function(store, conf) {
		this.store = store;
		this.conf = conf;
		this.init();
	}
	
	var 
		karacos = KaraCos;
	
	bo.prototype = {
		/**
		 * initialize backoffice
		 */
		init: function() {
			var backoffice = this;
			jQuery.ajax({ url: store.store_url+"/_backoffice/get_user_actions_forms",
				dataType: "json",
				cache: false,
				async: false,
				contentType: 'application/json',
				context: document.body,
				type: "GET",
				success: function(data) {
					if (data.success) {
						backoffice.elem = $('#store_backoffice');
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
				var form = $(this).closest('form'),
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
				karacos.action({ url: form.attr('action'),
					method: method,
					async: false,
					params: params,
					callback: function(data) {
//						backoffice.shipping_ui.dialog("destroy");
						
						$.ajax({ url: "/fragment/view_shipping_rates?office_id=" +
									store.office.id + "&base_id=" + store.office.db,
							async: false,
							cache: false,
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
		settings_ui: function(elem) {
			var backoffice = this, method, params;
//			console.log(forms);
			this.settings_ui_elem = elem;
			elem.find(".apply_form").click(function(event){
				
				var form = $(this).closest('form'),
				method,
				params = {};
				$.each(form.serializeArray(), function(i, field) {
					if (field.name === "method") {
						method = field.value;
					} else {
						params[field.name] = field.value;
					}
				}); // each
				karacos.action({ url: form.attr('action'),
					method: method,
					async: false,
					params: params,
					callback: function(data) {
						karacos.alert(data.message);
					}
				});
				return false;
			});
			
		},
		payment_ui: function(elem,forms) {
			var backoffice = this;
//			console.log(forms);
			this.payment_ui_elem = elem;
			$.ajax({ url: "/fragment/set_services.jst",
				async: false,
				cache: false,
				context: document.body,
				type: "GET",
				success: function(data) {
					var template = jsontemplate.Template(data, karacos.jst_options);
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
			function refreshCartsUI() {
				backoffice.elem.find('#store_backoffice_actions').tabs('load', 3);

			}
			backoffice.carts_management_elem = elem;
			elem.accordion({
				autoHeight: false,
				navigation: true,
				scrollable: true});
			elem.find(".karacos_button").each(
				function(i,kcbtn) {
					var $kcbtn = $(kcbtn);
					$kcbtn.button();
					karacos.button($kcbtn,
							function(result){
						if (typeof result.error !== "undefined") {
							karacos.alert(result.error.message,[{'label': 'Ok'}]);
						} else {
							karacos.alert(result.message,[{'label': 'Ok'}]);
							refreshCartsUI();
						}
					});
				});
			elem.find(".add_tracking_number").each(
				function(i,trckbtn) {
					var $trckbtn = $(trckbtn),
					model;
					$trckbtn.button();
					model = VIE.ContainerManager.getInstanceForContainer($trckbtn.closest("[about]"));
					$trckbtn.button().click(
						function(event){
							if (typeof backoffice.cart_window === "undefined") {
								backoffice.cart_window = $('#kc_backoffice_cart');
								if (backoffice.cart_window.length === 0) {
									backoffice.cart_window = $('<div id="kc_backoffice_cart"/>');
									$('body').append(backoffice.cart_window);
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
									karacos.action({
										url: store.store_url+"/_backoffice",
										method: 'process_cart_shipping',
										async: false,
										params: params,
										callback: function(data) {
											if (data.success) {
												backoffice.cart_window.empty().text("Le numero de suivi est renseigne");
												refreshCartsUI();
												}
											}
										});
									
								});
						});
				});
			elem.find(".view_payment").each(function viewPayment(i, paybtn){
				var $paybtn = $(paybtn),
					cart_id = $paybtn.closest("tr").find('[property*=cart_id]').text();
				$paybtn.button().click(function(){
					karacos.action({
						url: store.store_url+"/_backoffice",
						method: 'get_payment',
						async: false,
						params: {'cart_id': cart_id},
						callback: function(data) {
							$.ajax({ url: "/fragment/payment_details.jst",
								async: false,
								cache: false,
								context: document.body,
								type: "GET",
								success: function(tmplsrc) {
									var template = jsontemplate.Template(tmplsrc, karacos.jst_options);
									if (typeof backoffice.payment_window === "undefined") {
										backoffice.payment_window = $('#kc_backoffice_payment');
										if (backoffice.payment_window.length === 0) {
											backoffice.payment_window = $('<div id="kc_backoffice_payment"/>');
											$('body').append(backoffice.payment_window);
										}
									}
									backoffice.payment_window.empty().append(template.expand(data));
									backoffice.payment_window.dialog({width: '500px', modal:true});
									backoffice.payment_window.dialog('show');
								}
							});
						}
					});
				});
			});
			elem.find(".show_cart").each(
				function(i, showbtn){
					var $showbtn = $(showbtn),
						model;
					model = VIE.ContainerManager.getInstanceForContainer($showbtn.closest("[about]"));
					$showbtn.button().click(
						function(event){
							karacos.action({
								url: store.store_url,
								method: 'get_cart',
								async: false,
								params: {'cart_id': model.get('cart_id')},
								callback: function(data) {
									$.ajax({ url: "/fragment/show_cart.jst",
										async: false,
										cache: false,
										context: document.body,
										type: "GET",
										success: function(tmplsrc) {
											var template = jsontemplate.Template(tmplsrc, karacos.jst_options);
											if (typeof backoffice.cart_window === "undefined") {
												backoffice.cart_window = $('#kc_backoffice_cart');
												if (backoffice.cart_window.length === 0) {
													backoffice.cart_window = $('<div id="kc_backoffice_cart"/>');
													$('body').append(backoffice.cart_window);
												}
											}
											backoffice.cart_window.empty().append(template.expand(data.result));
											backoffice.cart_window.dialog({width: '500px', modal:true});
											backoffice.cart_window.dialog('show');
											backoffice.cart_window.find("button").button().click(
												function(event){
													karacos.action({
														url: store.store_url+"/_backoffice",
														method: 'prepare_cart',
														async: false,
														params: {'cart_id': model.get('cart_id')},
														callback: function(data) {
															if (data.success) {
																backoffice.cart_window.empty().text("Cette commande est consideree !");
																refreshCartsUI();
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
	return bo;
});				