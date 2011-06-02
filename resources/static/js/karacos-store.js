KaraCos.Store = {
			is_ready: false,
			ready_func: [],
			/**
			 * 
			 */
			get_user_adr: function() {
				var cart = this;
				KaraCos.action({
					url: '/store',
					method: 'get_user_adresses',
					params: {},
					async: false,
					callback: function(data) {
						cart.user_adresses = data.data;
						cart.user_adrs_list = [];
						KaraCos.$.each(cart.user_adresses, function(i,e) {
							cart.user_adrs_list.push(e.label);
						});
					}
				});
			},
			/**
			 * 
			 */
			ready: function(callback) {
				if (this.is_ready) {
					callback(this);
				} else {
					this.ready_func.push(callback);
				}
			},
			
			/**
			 * Store initialization method
			 */
			init_store: function(config) {
				try {
					if (this.is_ready && this.store_url === config.url) {
						console.log('store already initialized at that url');
					} else {
						this.store_url = config.url;
						this.is_ready = true;
						console.log('initializing store');
						/**
						 * Formatter for numbers in jsontemplates
						 */
						KaraCos.jst_options.more_formatters['fprice'] = function (s) {
							number = Number(s);
							return (number.toFixed(2)).toString();
						};
						len = this.ready_func.length;
						for(var i = 0; i < len; i++) {
							try {
								console.log("store_init["+i+"]");
								console.log(this.ready_func[i]);
								this.ready_func[i](this);
							} catch(e) {
								console.log(e);
							}
						}
					}
				} catch(e) {
					console.log(e);
				}
			},
			/**
			 * Enables/disables inc/dec buttons for items in cart
			 * 
			 * params : callback : if given, in case of success
			 * 
			 */
			activate_item_cart_buttons: function(selector,callback) {
				var selected = KaraCos('body');
				if (typeof selector !== "undefined") {
					selected = KaraCos(selector);
				}
				try {
					selected.find('.inc_number').button({
						icons: {primary: "ui-icon-carat-1-n"}, 
						text: false})
						.click(function(){
							var item_cart,
							number, m,
							kcmethod = jQuery(this).closest("[about]");
							item_cart = kcmethod.find('.item_cart_number');
							number = Number(item_cart.text());
							number += 1;
							item_cart.empty().append(number);
							m = VIE.ContainerManager.getInstanceForContainer(kcmethod);
							Backbone.sync('_update',m);
							if (typeof callback !== "undefined") {
								callback(m);
							}
						});
					selected.find('.dec_number').button({
						icons: {primary: "ui-icon-carat-1-s"},
						text: false})
						.click(function(){
							var item_cart,
							number, m,
							kcmethod = jQuery(this).closest("[about]");
							item_cart = kcmethod.find('.item_cart_number');
							number = Number(item_cart.text());
							number -= 1;
							item_cart.empty().append(number);
							m = VIE.ContainerManager.getInstanceForContainer(kcmethod);
							Backbone.sync('_update',m);
							if (typeof callback !== "undefined") {
								callback(m);
							}
						});					
				} catch (e) {
					console.log(e);
				}
			}
	};
(function(KaraCos, document){
	var shoppingCartProto, store = KaraCos.Store;
		
	shoppingCartProto = {
		/**
		 * fallback to jquery find
		 */
		find: function(selector) {
			return this.win.find(selector);
		},
		/**
		 * Add an adress to shopping cart adrtype of :
		 * "billing" // adds a billing adress
		 * "shipping" // adds a shipping adress
		 */
		add_adr: function(adrtype) {
			var store = KaraCos.Store,
				cart = this;
			cart.current_op = "add_cart_" + adrtype;
			cart.adrtype = adrtype;
			KaraCos.getForm({
				url:"/store",
				form:cart.current_op,
				callback: function(data,form) {
					var template = jsontemplate.Template(form, KaraCos.jst_options),
						labelfield, newadrform, adraccord, adrtemplate, winid;
					winid = cart.adrtype + "_adress_form";
					store.adrwin = KaraCos("#" + winid);
					if (store.adrwin.length === 0) {
						KaraCos('body').append('<div id="'+ winid +'"/>');
						store.adrwin = KaraCos("#" + winid);
					} // store.adrwin.length
					
					store.adrwin.empty().append(template.expand(data));
					store.adrwin.dialog({width: '600px', modal:true});
					store.adrwin.dialog('show');
					newadrform = store.adrwin.find("#add_adr_form");
					adraccord = store.adrwin.find("#karacos_adress_accordion");
					store.get_user_adr();
					if (store.user_adrs_list.length > 0) {
						// there are some known addresses of this user
						adraccord.prepend('<h3>Choisir une adresse</h3><div id="kc_existing_adresses"/>');
						KaraCos.$.ajax({ url: "/fragment/adr_show.jst",
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
									KaraCos.$.ajax({ url: "/fragment/modify_use_adr.jst",
										context: document.body,
										type: "GET",
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
								
							}});
						adraccord.delegate("button", 'click', function(event) {
							/**
							 * 
							 */
							var 
								form = KaraCos.$(this).closest('form');
							
							event.stopImmediatePropagation();
							event.preventDefault();
							cart.process_adr_form(form,store);
							return false;
						}); // delegate
					}
					
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
				store.cart.data.data.shipping_adr = params.label;
				
			}
			if (method === 'add_cart_billing') {
				this.process_set_billing_adr(form,store,params);
				store.cart.data.data.billing_adr = params.label;
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
					store.cart.billing_adr = data.data;
					KaraCos.$.ajax({ url: "/fragment/adr_show_cart.jst",
						context: document.body,
						type: "GET",
						async: true,
						success: function(data) {
							var adrtemplate = jsontemplate.Template(data, KaraCos.jst_options);
							store.cart.billing_adr.label = "Adresse de facturation"; 
							store.cart.find('.billing_adr_panel').empty()
								.append(adrtemplate.expand(store.cart.billing_adr));
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
					cart.calculate_shipping();
					store.adrwin.dialog("close");
					
				},
				error: function(data) {
					console.log(data);
				}
			}); // post
		},
		/**
		 * 
		 */
		calculate_shipping: function() {
			var cart = this;
			KaraCos.action({url: store.store_url,
				method: 'calculate_shipping',
				async:true,
				callback: function(data) {
					if (data.success) {
						store.cart.shipping_adr = data.data.adress;
						store.cart.find('.set_shipping_button').empty().text(data.data.shipping);
						KaraCos.$.ajax({ url: "/fragment/adr_show_cart.jst",
							context: document.body,
							type: "GET",
							async: true,
							success: function(data) {
								var adrtemplate = jsontemplate.Template(data, KaraCos.jst_options);
								store.cart.shipping_adr.label = "Adresse de livraison"; 
								store.cart.find('.shipping_adr_panel').empty()
								.append(adrtemplate.expand(store.cart.shipping_adr));
							}
						});
						cart.check_state();
					}
				},
				error: function(data) {
					console.log(data);
					cart.check_state();
					//alert("Can't calculate shipping !!!");
				}});
		},
		/**
		 * 
		 */
		init: function() {
			this.win = KaraCos('#Shopping_cart');
			if (this.win.length == 0) {
				KaraCos('body').append('<div id="Shopping_cart"/>');
				this.win = KaraCos('#Shopping_cart');
			}
		},
		/**
		 * Shows the shopping cart
		 */
		show: function() {
			var cart = this;
			cart.win.empty().dialog({width: '600px',modal:true}).show();
			KaraCos.getForm({
				url:KaraCos.Store.store_url,
				form:'get_shopping_cart',
				callback: function(data,form) {
					cart.template = jsontemplate.Template(form, KaraCos.jst_options);
					cart.data = data;
					cart.process_render();
					cart.check_state();
				}
			});
			return this;
		},
		/**
		 * Process rendering and event bindings
		 */
		process_render: function() {
			var cart = this;
			cart.win.empty().append(cart.template.expand(cart.data));
			
			cart.find('.set_shipping_button').click(function(){
				KaraCos.authManager.provideLoginUI(function(){
					KaraCos.Store.cart.add_adr('shipping');
				});
			}); // click
			cart.find('.set_billing_button').click(function(){
				KaraCos.authManager.provideLoginUI(function(){
					KaraCos.Store.cart.add_adr('billing');
				});
			}); // click
			cart.check_state();
			
			KaraCos.Store.activate_item_cart_buttons("#shopping_cart_grid",function(model) {
				cart.process_change_number(model);
			});
			KaraCos.button(cart.find('.pay_button'),function(data){
				if (data.success) {
					document.location = data.data.url;					
				}
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
//				if (arguments[0] === true) {
					for (var i=0, len = arguments[3].length; i < len; i++) {
						if (arguments[3][i].id === model.attributes.item_id) {
							result = arguments[3][i];
							result.cart_index = i;
							return result;
						}
					}
//				} else {
//					return true;
//				}
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
			cart.calculate_shipping();
		},
		/**
		 * Check cart state
		 */
		check_state: function() {
			var cart = this;
			
			KaraCos.action({url: store.store_url,
				params: {},
				method: 'validate_cart',
				async:true,
				callback: function(data) {
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
				},
				error: function() {
					cart.find(".pay_button").hide();
				}
			});
		}
	};
	KaraCos.ShoppingCart = function() {
		/**
		 * The Shopping Cart object
		 */
		this.init();
		return this;
	};
	KaraCos.ShoppingCart.prototype = jQuery.extend(true,KaraCos.ShoppingCart.prototype,shoppingCartProto);
})(KaraCos, document);