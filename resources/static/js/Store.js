define('store/Store',
	['jquery'], function($){
	var 
		karacos,
		store = {
			/**
			 * 
			 */
			get_user_adr: function() {
				var cart = this;
				karacos.action({
					url: '/store',
					method: 'get_user_adresses',
					params: {},
					async: false,
					callback: function(data) {
						cart.user_adresses = data.data;
						cart.user_adrs_list = [];
						$.each(cart.user_adresses, function(i,e) {
							cart.user_adrs_list.push(e.label);
						});
					}
				});
			},
			/**
			 * 
			 */
			ready: function(callback) {
				$('body').bind('kcstore', callback);
//					if (this.is_ready) {
//						callback(this);
//					} else {
//						this.ready_func.push(callback);
//					}
			},
			
			/**
			 * Store initialization method
			 */
			init: function(config) {
				var store = this;
				try {
					if (this.is_ready && this.store_url === config.url) {
						console.log('store already initialized at that url');
						return;
					} else {
						store.store_url = config.url;
						$.ajax({
							url: store.store_url,
							context: document.body,
							type: "GET",
							dataType: "json",
							contentType: 'application/json',
							cache: false,
							async: true,
							success: function(data) {
								if (data.success === true) {
									console.log('Initializing store at url ' + store.store_url);
									store.id = data.data.id;
									store.base_id = data.data.base_id;
									$('body').trigger('kcstore', [store]);
									
								}
							}
							
						})
						/**
						 * Formatter for numbers in jsontemplates
						 */
						karacos.jst_options.more_formatters['fprice'] = function (s) {
							number = Number(s);
							return (number.toFixed(2)).toString();
						};
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
				var selected = $('body');
				if (typeof selector !== "undefined") {
					selected = $(selector);
				}
				try {
					selected.find('.inc_number').button({
						icons: {primary: "ui-icon-carat-1-n"}, 
						text: false})
						.click(function(){
							var item_cart,
							number, m,
							kcmethod = $(this).closest("[about]");
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
							kcmethod = $(this).closest("[about]");
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
			},
			show_page: function(url,method,count,page){
				$($("#store_page_nav_header li").get(page)).addClass('ui-state-over');
				var store = this;
				console.log("Running show_page");
				store.page = {};
				try {
					var template,
					len;
					$.ajax({ url: "/fragment/get_items_list.jst",
						context: document.body,
						type: "GET",
						async: false,
						success: function(jstsrc) {
							template = jsontemplate.Template(jstsrc, karacos.jst_options);
							karacos.action({ url: url,
								method: method,
								async: false,
								params:{count:count,page:page},
								callback: function(data) {
									var main_content = $('#StoreContent');
									console.log("items list fetched");
									try {
										main_content.empty();
										main_content.append(template.expand(data));
										main_content.find('.karacos_store_item').panel({
											collapsible:false
										});
//							.sortable({
//									placeholder: "ui-state-highlight"
//								});
										store.activate_item_cart_buttons();							
									} catch(e) {
										console.log("Exception in show_page");
										console.log(e);
									}
								}
							});
						}});
				} catch(e) {
					console.log(e);
				}
				$('body').bind('kcui', function(){
					$("#store_page_nav_header li").button({}).click(
							function(event){
								event.stopImmediatePropagation();
								event.preventDefault();
								var $this = $(this), url;
								url = $this.find('a').attr("href");
								History.pushState(null, null, url);
								$.ajax({
									url: url,
									headers: {'Karacos-Fragment': 'true'},
									success: function(data) {
										$('#MainContent').empty().append(data);
									}
								});
							});
				});
					
			} // function store.sow_page
	};
	$('body').bind('kcready', function(){
		$('body').createPromiseEvent('kcstore');
		$('body').createPromiseEvent('kcstoreloaded');
		console.log('Starting store Initialization');
		karacos = KaraCos;
		//TODO: remove later
		// Setting a global (compatibility issue)
		karacos.Store = store;
		$('body').trigger('kcstoreloaded', [store]);
	})
	// If payment_validation
	if (window.kc_method_result !== false) {
		if (typeof window.kc_method_result.datatype !== "undefined") {
			if (window.kc_method_result.datatype === "payment_validation") {
				(function(){ // immediate function for scope variables declaration
					var payment_validation = $("#payment_validation");
					if (payment_validation.length === 0) {
						payment_validation = $('<div style="display:none" id="payment_validation"></div>');
						$('body').append(payment_validation);
					}
					$('body').bind('kcui', function(){
						if (window.kc_method_result.success) {
							payment_validation.empty()
								.append("<p>Votre commande est validée</p>" +
										"<p>Merci pour votre confiance</p>")
								.dialog({modal: true}).show();
						} else {
							payment_validation.empty()
							.append("<p>Erreur lors de la validation du paiement</p>" +
									"<p>Votre commande est annulée</p>")
							.dialog({modal: true}).show();
						}
					});
					
				})();
			}
		}
	}
	// Inform user about it's payment transaction status
	
	
	return store;
});