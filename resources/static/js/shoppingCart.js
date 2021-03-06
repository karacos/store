define('store/shoppingCart',
		['jquery','store/Store','store/handler.Store.pay_cart'],
	function($,store, handlersRegistry) {
		var karacos,
		// main function
			ShoppingCart = function() {
				/**
				 * The Shopping Cart object
				 */
				this.init();
				return this;
			},

		// Prototype for ShoppingCart
			shoppingCartProto = {
					/**
					 * Object Initialization
					 */
					init: function() {
						this.win = $('#Shopping_cart');
						if (this.win.length == 0) {
							$('body').append('<div id="Shopping_cart"/>');
							this.win = $('#Shopping_cart');
						}
					},
					/**
					 * fallback to jquery find
					 */
					find: function(selector) {
						return this.win.find(selector);
					},
					/**
					 * If user email is not set, ask user for it
					 * @param callback
					 */
					verify_email: function(callback) {
						
						if (KaraCos.authManager.user_actions_forms.email === null) {
							$.ajax({
								url:"/fragment/set_user_email.jst",
								context: document.body,
								type: "GET",
								cache: false,
								async: true,
								success: function(data){
	//						var emailtemplate = jsontemplate.Template(data, KaraCos.jst_options);
									store.emailwin = $("#set_email_window");
									if (store.emailwin.length === 0) {
										$('body').append('<div id="set_email_window"/>');
										store.emailwin = $("#set_email_window");
									} // emailwin
									store.emailwin.empty().append(data);
									store.emailwin.dialog({width: '80%',modal:true}).show();
									store.emailwin.find('.form_set_email_button')
									.button().click(function(event){
										var $this = $(this), params = {}, method = 'set_user_email';
										$.each($this.closest('form').serializeArray(), function(i, field) {
											if (field.name === "method") {
												method = field.value;
											} else {
												params[field.name] = field.value;
											}
										}); // each
										KaraCos.action({ url: '/',
											method: method,
											async: false,
											params: params,
											callback: function(data) {
												if (data.success) {
													KaraCos.authManager.user_actions_forms.email = params['email'];
													store.emailwin.dialog('close');
													callback();
												}
											},
											error: function(data) {
												
											}
										}); // POST login form
									});
								}
							});
						} else {
							callback();
						}
					},
					/**
					 * Add an adress to shopping cart adrtype of :
					 * "billing" // adds a billing adress
					 * "shipping" // adds a shipping adress
					 */
					add_adr: function(adrtype) {
						var store = KaraCos.Store,
						cart = this,
						winid;
						cart.current_op = "add_cart_" + adrtype;
						cart.adrtype = adrtype;
						winid = cart.adrtype + "_adress_form";
						store.adrwin = KaraCos("#" + winid);
						if (store.adrwin.length === 0) {
							$('body').append('<div id="'+ winid +'"/>');
							store.adrwin = KaraCos("#" + winid);
						} // store.adrwin.length
						store.adrwin.empty().text("loading...");
						store.adrwin.dialog({width: '90%', top: '0px', modal:true});
						store.adrwin.dialog('show');
						KaraCos.getForm({
							url:"/store",
							form:cart.current_op,
							callback: function showAdrForm(data,form) {
								var template = jsontemplate.Template(form, KaraCos.jst_options),
								labelfield, newadrform, adraccord, adrtemplate, winid;
								
								store.adrwin.empty().append(template.expand(data));
								newadrform = store.adrwin.find("#add_adr_form");
								adraccord = store.adrwin.find("#karacos_adress_accordion");
								store.get_user_adr();
								if (store.user_adrs_list.length > 0) {
									// there are some known addresses of this user
									adraccord.prepend('<h3>Choisir une adresse</h3><div id="kc_existing_adresses"/>');
									$.ajax({ url: "/fragment/adr_show.jst",
										context: document.body,
										type: "GET",
										async: true,
										success: function(data) {
											var adrtemplate = jsontemplate.Template(data, KaraCos.jst_options);
											adraccord.find('#kc_existing_adresses').append(adrtemplate.expand({adresses: store.user_adresses}))
											adraccord.find('#kc_existing_adresses div.[typeof*="karacos"]').click(function() {
												// What happens on existing adress click :
												
												var modify_adr_form,
												modify_adr_template,
												that = this;
												if (adraccord.find('#kc_existing_adress').length === 0) {
													adraccord.append('<h3>Utiliser une adresse</h3><div id="kc_existing_adress"/>');											
												}
												modify_adr_form = adraccord.find('#kc_existing_adress');
												$.ajax({ url: "/fragment/modify_use_adr.jst",
													context: document.body,
													type: "GET",
													cache: false,
													async: true,
													success: function(data) {
														var modify_adr_template = jsontemplate.Template(data, KaraCos.jst_options),
														model = VIE.ContainerManager.getInstanceForContainer(KaraCos.$(that));
														model.attributes.method = cart.current_op;
														model.attributes.action = store.store_url;
														modify_adr_form.empty().append(modify_adr_template.expand(model.attributes));
														adraccord.accordion("destroy");
														adraccord.accordion({
															autoHeight: false,
															navigation: true});
														adraccord.accordion('activate',2);
														
													}
												});
												
											});
											
										},
										error: function(data) {
											
										}});
								}
								adraccord.delegate("button", 'click', function(event) {
									/**
									 * 
									 */
									var 
									form = $(this).closest('form');
									
									event.stopImmediatePropagation();
									event.preventDefault();
									cart.process_adr_form(form,store);
									return false;
								}); // delegate
								
								$("#add_adr_form form").submit(function(event) {
									var form = $(this.target);
									event.stopImmediatePropagation();
									event.preventDefault();
									cart.process_adr_form(form,store);
									return false;
								});
								
								adraccord.accordion({
									autoHeight: false,
									navigation: true});
								store.adrwin.show(); //
							}
						});
					},
					/**
					 * 
					 */
					process_adr_form: function(form,store) {
						var 
						method,
						cart = this,
						params = {};
						$.each(form.serializeArray(), function(i, field) {
							if (field.name === "method") {
								method = field.value;
							} else {
								params[field.name] = field.value;
							}
						}); // each
						if (method === 'add_cart_shipping') {
							this.process_set_shipping_adr(form,store,params);
							store.cart.data.data.shipping = params.label;
							
						}
						if (method === 'add_cart_billing') {
							this.process_set_billing_adr(form,store,params);
							store.cart.data.data.billing = params.label;
						}
						
					},
					/**
					 * 
					 */
					process_set_billing_adr: function(form, store,params) {
						var cart = this;
						KaraCos.action({ url: form.attr('action'),
							method: 'add_cart_billing',
							async: false,
							params: params,
							callback: function(data) {
								store.cart.data.data.billing_adr = data.data;
								$.ajax({ url: "/fragment/adr_show_cart.jst",
									context: document.body,
									type: "GET",
									cache: false,
									async: true,
									success: function(data) {
										var adrtemplate = jsontemplate.Template(data, KaraCos.jst_options);
										store.cart.data.data.billing_adr.label = "Adresse de facturation"; 
										store.cart.find('.billing_adr_panel').empty()
										.append(adrtemplate.expand(store.cart.data.data.billing_adr));
										cart.check_state();
									}
								});
								store.adrwin.dialog("close");
								cart.check_state();
							}
						});
					},
					/**
					 * 
					 */
					process_set_shipping_adr: function(form, store,params) {
						var cart = this;
						KaraCos.action({ url: form.attr('action'),
							method: 'add_cart_shipping',
							async: false,
							params: params,
							callback: function(data) {
								cart.calculate_shipping(function(error) {
									if (error === null) {
										store.adrwin.dialog("close");
									} else {
										alert(error);
									}
								});
								
							},
							error: function(data) {
								console.log(data);
							}
						}); // post
					},
					/**
					 * 
					 */
					calculate_shipping: function(callback) {
						var cart = this;
						KaraCos.action({url: store.store_url,
							method: 'calculate_shipping',
							async:true,
							callback: function(data) {
								var total_ht, total_ttc;
								if (data.success) {
									store.cart.data.data.shipping_adr = data.data.adress;
									cart.data.data.cart_total = Number(Number(cart.data.data.cart_total) + Number(data.data.shipping)).toFixed(2).toString();
									cart.data.data.cart_net_total = Number(Number(cart.data.data.cart_net_total) + Number(data.data.shipping)).toFixed(2).toString();
									cart.data.data.shipping = data.data.shipping;
									//cart.process_render();						
									$.ajax({ url: "/fragment/adr_show_cart.jst",
										context: document.body,
										type: "GET",
										cache: false,
										async: true,
										success: function(data) {
											var adrtemplate = jsontemplate.Template(data, KaraCos.jst_options);
											store.cart.data.data.shipping_adr.label = "Adresse de livraison"; 
											store.cart.find('.shipping_adr_panel').empty()
											.append(adrtemplate.expand(store.cart.data.data.shipping_adr));
										}
									});
									cart.check_state();
									if (typeof callback === "function") {
										callback(null);
									}
								} else {
									callback(data.message);
								}
							},
							error: function(data) {
								cart.check_state();
								if (typeof callback === "function") {
									callback(data.message);
								}
								//alert("Can't calculate shipping !!!");
							}});
					},
					/**
					 * Shows the shopping cart
					 */
					show: function() {
						var cart = this,
							store = KaraCos.Store;
						cart.win.empty().dialog({width: "80%",
							modal:true,
							title: "Votre caddie"}).show();
						KaraCos.getForm({
							url:KaraCos.Store.store_url,
							form:'get_shopping_cart',
							noparams: function(data) {
								$.ajax({ url: "/fragment/get_shopping_cart.jst?store_id=" + store.id + "&base_id=" + store.base_id,
									context: document.body,
									type: "GET",
									cache: false,
									async: false,
									success: function(form) {
										cart.template = jsontemplate.Template(form, KaraCos.jst_options);
										cart.data = data;
										cart.process_render();
										//cart.check_state();
									}
								});
							}
						});
						return this;
					},
					/**
					 * Process rendering and event bindings
					 */
					process_render: function() {
						var 
							cart = this,
							pay_button;
						
						
						cart.win.empty().append(cart.template.expand(cart.data));
						
						cart.find('.set_shipping_button').click(function(){
							KaraCos.authManager.provideLoginUI(function(){
								cart.verify_email(function(){
									KaraCos.Store.cart.add_adr('shipping');
								});
							},"Nous devons vous identifier pour enregistrer votre adresse"); // provideLoginUI sipping
						}); // click
						cart.find('.set_billing_button').click(function(){
							KaraCos.authManager.provideLoginUI(function(){
								cart.verify_email(function(){
									KaraCos.Store.cart.add_adr('billing');
								});
							},"Nous devons vous identifier pour enregistrer votre adresse");// provideLoginUI billing
						}); // click
						cart.check_state();
						
						KaraCos.Store.activate_item_cart_buttons("#shopping_cart_grid",function(model) {
							cart.process_change_number(model);
						});
						
						// Waiting Screen while payment transaction is initialized with Payment Service Provider
						cart.paymentWaiting = cart.find("#paymentWaiting");
						if (cart.paymentWaiting.length === 0) {
							// TODO: l10n
							cart.paymentWaiting = $('<div style="display:none" id="paymentWaiting"></div>');
							cart.win.append(cart.paymentWaiting);
						}
						cart.find('.pay_button img').click(function(event){
							var 
								$this = $(this).parent(),
								model = VIE.ContainerManager.getInstanceForContainer($this),
								result;
							event.stopImmediatePropagation();
							event.preventDefault();
							cart.paymentWaiting
								.empty()
								.append('<p>Vous allez etre redirrigés vers le prestataire de paiement</p>')
								.dialog({
									modal: true
								})
								.show();
							result = Backbone.sync('process',model);
							handlersRegistry.returnHandlers['pay_cart'](result, null,
									function(data) {
								if (data.success) {
									
									document.location = data.data.url;
								} else {
									cart.paymentWaiting.empty()
										.append("<p>Erreur pendant la transaction, votre panier est annulé</p>");
									if (typeof data.message === "string") {
										cart.paymentWaiting.append("<p>" + data.message + "</p>");
									}
								}
							});
						});
					},
					/**
					 * Update shopping cart display informations when item number modified in cart
					 */
					process_change_number: function(model) {
						var cart = this,
						items, modified_item,
						number = Number(model.attributes.number);
						modified_item = cart.data.data.items.reduce(function() {
							console.log(arguments);
							var result;
		//			if (arguments[0] === true) {
							for (var i=0, len = arguments[3].length; i < len; i++) {
								if (arguments[3][i].id === model.attributes.item_id) {
									result = arguments[3][i];
									result.cart_index = i;
									return result;
								}
							}
		//			} else {
		//				return true;
		//			}
						});
						modified_item.number = number;
						modified_item.net_total = number * modified_item.net_price;
						modified_item.total = number * modified_item.price;
						modified_item.tax_total = number * modified_item.tax * modified_item.price;
						
						cart.data.data.items[modified_item.cart_index] = modified_item;
						total = 0;
						net_total = 0;
						tax_total = 0;
						cart.data.data.items.map(function(e,i){
							total = total + e.total;
							net_total = net_total + e.net_total;
							tax_total = tax_total + e.tax_total;
						});
						cart.data.data.cart_total = total;
						cart.data.data.cart_net_total = net_total;
						cart.data.data.cart_tax_total = tax_total;
						cart.process_render();
						cart.calculate_shipping(function(error) {
							if (error === null) {
								store.adrwin.dialog("close");
							} else {
								alert(error);
							}
						});
					},
					/**
					 * Check cart state
					 */
					check_state: function() {
						var cart = this,
							validation_message = $("#validation_message");
						if (validation_message.length === 0) {
							validation_message = $('<div id="validation_message"></div>');
							$('body').append(validation_message);
						}
						KaraCos.action({url: store.store_url,
							params: {},
							method: 'validate_cart',
							async:true,
							callback: function(validateResult) {
								var cbfunc = function(data){
									if (data.success) {
										// cart contains all required info, pay button activated
										cart.find(".pay_button").show()
										.click(function(event){
											event.stopImmediatePropagation();
											event.preventDefault();
										});
									} else {
										cart.find(".pay_button").hide();
									}
								};
								if (handlersRegistry.returnHandlers['validate_cart'] !== undefined) {
									handlersRegistry.returnHandlers['validate_cart'](validateResult,undefined,cbfunc);
								} else {
									cbfunc(validateResult);
								}
								
							},
							error: function(data) {
								
								var cart_validate_handle = function(data) {
									if (data.message) {
										validation_message.empty()
											.append(data.message);
										if (data.type === "billing") {
											var billButton = $("<button>Ajouter adresse de facturation</button>");
											billButton.click(function(){
												KaraCos.authManager.provideLoginUI(function(){
													cart.verify_email(function(){
														KaraCos.Store.cart.add_adr('billing');
														validation_message.dialog('destroy');
													});
												},"Nous devons vous identifier pour enregistrer votre adresse"); // provideLoginUI sipping
											}); // click
											validation_message.append(billButton);
										}
										if (data.type === "shipping") {
											var shipButton = $("<button>Ajouter adresse de livraison</button>");
											shipButton.click(function(){
												KaraCos.authManager.provideLoginUI(function(){
													cart.verify_email(function(){
														KaraCos.Store.cart.add_adr('shipping');
														validation_message.dialog('destroy');
													});
												},"Nous devons vous identifier pour enregistrer votre adresse"); // provideLoginUI sipping
											}); // click
											validation_message.append(shipButton);
										}
										if (data.type === "email") {
											validation_message.append('<div> \
														<div>Please enter a valid email</div> \
														<div><input type="text" name="email"/>\
														<button>update Email</button></div>\
													</div>');
											validation_message.find("button").button().click(function(e){
												e.stopImmediatePropagation();
												e.preventDefault();
												karacos.action({
													url: '/',
													method: "set_user_email",
													params: {"email": validation_message.find("input").val()},
													async: true,
													callback: function(setEmailResult) {
														if (setEmailResult.success) {
															karacos.action({
																url:"", //store url
																method: "add_cart_customer_email",
																params: {"email":validation_message.find("input").val()},
																callback: function(setCartEmail) {
																	if (setCartEmail.success) {
																		validation_message.dialog('destroy');
																		cart.check_state();
																	}
																}
															});
														}
													},
													error: function(setEmailError) {
														if (validation_message.find(".error").length === 0) {
															validation_message.append('<div class="error">Invalid email format</div>');
														}
													}
												});
												;
											});
										}
										validation_message.dialog({modal: true});
									}
								};
								
								cart.find(".pay_button").hide();
								if (handlersRegistry.returnHandlers['validate_cart'] !== undefined) {
									handlersRegistry.returnHandlers['validate_cart'](data, undefined, function(){
										cart_validate_handle(data);
									});
								} else {
									cart_validate_handle(data);
								}
							}
						});
					}
			};
		ShoppingCart.prototype = jQuery.extend(true,ShoppingCart.prototype,shoppingCartProto);
		$('body').bind('kcready', function() {
			karacos = KaraCos;
			karacos.ShoppingCart = ShoppingCart;
		});
		
		return ShoppingCart;
		
});