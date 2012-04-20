define("store/toolkit.AddFolderAction", 
		["jquery",
		 "site/script",
		 'karacos/lib/toolkit.DragnDropFilesSink',
		 "karacos/lib/toolkit.ImageProcessor",
		 "karacos/lib/toolkit.FileUploader",
		], function($, innovatech, DragnDropFilesSink, ImageProcessor, FileUploader) {
	var 
		addFolderAction, auth, karacos;
	function AddFolderAction(config) {
		if (typeof config === "undefined") {
			config = {};
		}
		this.config = config;
		this.dialog_elem = config.dialog_elem;
		addFolderAction = this;
		$('body').bind('kcauth', function(){
			karacos = KaraCos;
			auth = karacos.authManager;
			if (typeof addFolderAction.config.url === "undefined") {
				addFolderAction.config.url = karacos.config.page_url;
			}
		});
		$('body').bind('kcui', function(){
			if (typeof addFolderAction.dialog_elem === "undefined") {
				addFolderAction.dialog_elem = $("#addFolderDialog");
			}
			if (addFolderAction.dialog_elem.length === 0) {
				addFolderAction.dialog_elem = $('<div id="addFolderDialog"></div>');
				$('body').append(addFolderAction.dialog_elem);
			}
		});
	}
	$.extend(AddFolderAction.prototype, {
		/**
		 * Folder form template
		 */
		addFolderForm:  $('<form> \
				<div class="image_holder dropImageContainer">Drop image\
				<span style="text-underline-style: solid;"> or click here</span></div> \
				<div class="field_holder_small"><label for="name">Nom</label> \
					<input type="text" name="name"/></div> \
				<div class="field_holder_small"><label for="title">Titre</label> \
					<input type="text" name="title"/></div> \
				<div class="textarea_holder"><label for="content">Description</label> \
					<textarea name="content"></textarea></div> \
				<div class="field_holder">\
				<button type="submit">Ajouter</button> \
				<button type="cancel">Annuler</button>\
				</div></form>'),
		/**
		 * Button for sidebar
		 */
		addFolderButton: $('<a href="#">Ajouter une section</a>'),
		/**
		 * Set Button's click handler
		 */
		init_addFolderButton: function() {
			addFolderAction.addFolderButton.click(function(e) {
				e.preventDefault();
				e.stopImmediatePropagation();
				addFolderAction.dialog_elem.empty().append(addFolderAction.addFolderForm);
				addFolderAction.init_addFolderForm();
				addFolderAction.dialog_elem.dialog({width: '400px', modal: true, title: "Nouvelle section magasin"});
				addFolderAction.dialog_elem.show();
			});
		},
		/**
		 * Configure filedropEvent using karacos Dropsink
		 */
		initFileDrop: function(dropImageContainer) {
			var dropsink = new DragnDropFilesSink();
			dropsink.setBodyDropHandler();
			$('body').bind("dropFiles", function(e, dropSink){
				var 
					file,
					reader;
				function avoidDrop(e) {
					e.preventDefault();
					e.stopImmediatePropagation();
					//TODO: notify user a file dropped is already processing
				}
				$('body').bind("dropFiles", avoidDrop);
				console.debug("file dropped");
				if (dropSink.target.get(0) === dropImageContainer.get(0)) {
					dropImageContainer.css("border", "5px solid #A0A0A0");
					if (dropSink.droppedFilesCount !== 1) {
						// Error, more than one file dropped
						// TODO: user notification
						return; // end execution
					}
					file = addFolderAction.file = dropSink.files[0];
					if (file.type.match(/image/) === null) {
						// Error, file is not an image
						// TODO: user notification
						return; // end file drop event handler
					}
					// User action is verification ok, processing file
					dropImageContainer.empty().append("<small>Correction de la taille des images</small>");
					reader = new FileReader();
					reader.onloadend = function() {
						addFolderAction.droppedImageOrigData = reader.result;
						imgProcessor = new ImageProcessor();
						imgProcessor.resizeImage(addFolderAction.droppedImageOrigData,
								// Generate version for classic browser
								{max_width: 1024, max_height: 1024},
								function(data) {
							addFolderAction.droppedImage1024 = data;
							imgProcessor.resizeImage(data, 
									// Generate mobile browser version
									{max_width: 400, max_height: 400},
									function(data) {
								addFolderAction.droppedImage400 = data;
								imgProcessor.resizeImage(data, 
									// generate Thumbnail
									{max_width: 100, max_height: 100},
									function(data) {
										var thumbnail = $("<img>");
										addFolderAction.droppedImage100 = data;
										dropImageContainer.css("width", 100);
										dropImageContainer.css("height", 100);
										dropImageContainer.css("border", "1px solid white");
										dropImageContainer.empty().append(thumbnail);
										thumbnail.attr("src", data);
										$('body').unbind("dropFiles", avoidDrop);
								});
							});
						})
		            };
		            reader.readAsDataURL(file);
				}
			});
		},
		/**
		 * UpdateCallback
		 */
		uploadFilesCallback: function(data) {
			var fileUploader;
			if (data.success && typeof addFolderAction.droppedImage1024 !== "undefined") {
				// Store item is created, uploading it's files
				//TODO: display upload progress
				debugger;
				fileUploader = new FileUploader({
					// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
					// !!!!!!!!!!! params is undefined     !!!!!!!!!!!!!!!!!!!!!!!
					url: karacos.config.page_url + "/" + params.name
					// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				});
				fileUploader.uploadFile(
						{
							fileName: "main1024.png",
							fileSize: addFolderAction.droppedImage1024.length,
							type: "image/png",
							data: addFolderAction.droppedImage1024
						},
						{onload: function(xhr){
							var jsonresp = $.parseJSON(this.responseText);
							if (jsonresp.success) {
								fileUploader.uploadFile(
									{
										fileName: "main400.png",
										fileSize: addFolderAction.droppedImage400.length,
										type: "image/png",
										data:addFolderAction.droppedImage400
									},
									{onload: function(xhr){
										var jsonresp = $.parseJSON(this.responseText);
										if (jsonresp.success) {
											fileUploader.uploadFile(
												{
													fileName: "main100.png",
													fileSize: addFolderAction.droppedImage100.length,
													type: "image/png",
													data: addFolderAction.droppedImage100
												},
												{onload:function(xhr){
													var jsonresp = $.parseJSON(this.responseText);
													
												}
											}); //fileUploader.uploadFile 100
										}
									}
								}); ////fileUploader.uploadFile 400
							} // if success 1025
						} // onload 1024
					}); //fileUploader.uploadFile 1024
			} // if success && file to upload else do nothing
		},
		submitForm: function(form,callback) {
			var
				options = {
					async: true,
					error: function(data) {
						validateButton.button('enable');
						cancelButton.button('enable');
						form.closest('.ui-dialog-titlebar-close').show();
					}
				},
				refField			= form.find('input[name="name"]'),
				validateButton		= form.find('button[type="submit"]'),
				cancelButton		= form.find('button[type="cancel"]');
			if (addFolderAction.validateForm()) {
				validateButton.button('disable');
				cancelButton.button('disable');
				form.closest('.ui-dialog-titlebar-close').hide();
				if (refField.attr("disabled") !== true) {
					options.url = addFolderAction.config.url;
					options.params = {};
					options.method = "create_store_folder";
					options.callback = function(data) {
						if (typeof callback === "function") {
							refField.attr("disabled", true);
							callback(data);
						}
					};
				} else {
					options.url = addFolderAction.config.url + "/" + refField.val();
					options.params = {};
					options.method = "_update";
					options.callback = function(data) {
						if (typeof callback === "function") {
							callback(data);
						}
					};
				}
				$.each(form.serializeArray(), function(i,e) {
					options.params[e.name] = e.value;
				});
				karacos.action(options);
			}
		},
		/**
		 * Returns true if form is validated
		 */
		validateForm: function(form) {
			var
				form				= addFolderAction.dialog_elem.find('form'),
				validateButton		= form.find('button[type="submit"]'),
				dropImageContainer	= form.find('.dropImageContainer'),
				cancelButton		= form.find('button[type="cancel"]');
			validation = true;
			$.each(form.data('state'), function(field, valid) {
				validation = validation && valid;
			});
			if (validation) {
				validateButton.button("enable");
				dropImageContainer.find('span').show();
			} else {
				validateButton.button("disable");
				dropImageContainer.find('span').hide();
			}
			return validation;
		},
		/**
		 *  mark a field as invalid
		 */
		invalidField: function(field, errorlabel) {
			var form				= addFolderAction.dialog_elem.find('form'),
				validateButton		= form.find('button[type="submit"]'),
				dropImageContainer	= form.find('.dropImageContainer'),
				name = field.attr('name'),
				state = form.data('state');
			state[name] = false;
			form.data('state', state);
			field.addClass("error_highlight_field");
			validateButton.button("disable");
			dropImageContainer.find('span').hide();
		},
		/**
		 * mark a field as valid then try to validate form
		 */
		validField: function(field) {
			var form = addFolderAction.dialog_elem.find('form'),
				name = field.attr('name'),
				state = form.data('state');
			state[name] = true;
			form.data('state', state);
			field.removeClass("error_highlight_field");
			addFolderAction.validateForm();
		},
		/**
		 * Init form and ui bindings
		 */
		init_addFolderForm: function() {
			var
				form				= addFolderAction.dialog_elem.find('form'),
				validateButton		= form.find('button[type="submit"]'),
				cancelButton		= form.find('button[type="cancel"]'),
				refField			= form.find('input[name="name"]'),
				dropImageContainer	= form.find('.dropImageContainer'),
				/**
			     * Handles click on dropImageContainer for all browsers (including non html5 browsers)
			     */
				showUploadWindow	= function(){
					var uploadFileWin = $("#uploadFileWin");
					if (uploadFileWin.length === 0) {
						uploadFileWin = $('<div id="uploadFileWin">');
						$('body').append(uploadFileWin);
					}
					addFolderAction.submitForm(form,function(){ //save user data in form as page will be refreshed
						uploadFileWin.empty().append('<form method="POST" action="' + 
								addFolderAction.config.url + "/" + refField.val() + //<input type="hidden" name="fileName" value="">\
								'" enctype="multipart/form-data">\
								<input type="hidden" name="method" value="add_attachment"/>\
								<div data-role="fieldcontain"> \
								<label for="att_file" class="left">Fichier</label>\
								<input type="FILE" value="" name="att_file">\
								</div>\
								<button kc-action="add_attachment" type="submit">Upload</button>\
						</form>');
						// 
						uploadFileWin.dialog({modal: true, width: "90%"})
					}); 
				};
			
			addFolderAction.initFileDrop(dropImageContainer);
			
			dropImageContainer.bind("dragenter", function() {
				dropImageContainer.css("border", "5px solid white");
			});
			dropImageContainer.bind("dragleave", function() {
				dropImageContainer.css("border", "5px solid #A0A0A0");
			});
			dropImageContainer.find('span').click(showUploadWindow);
			dropImageContainer.find('span').hide();
			// submit handler
			form.submit(function(e){
				e.preventDefault();
				e.stopImmediatePropagation();
				addFolderAction.submitForm(form,function(data){
					debugger;
					addFolderAction.uploadFilesCallback(data);
					addFolderAction.dialog_elem.dialog('destroy');

				});
			});
			cancelButton.click(function() {
				addFolderAction.dialog_elem.dialog('destroy');
			});
			cancelButton.button();
			validateButton.button();
			form.data('state', {"name": false}); // all elements of data must be true...
			validateButton.button("disable");
			// Fields value handler for validation
			// TODO: add ui notification about fields validation
			refField.bind("keyup", function() {
				var val = refField.val();
				if (val !== "" && val.match(new RegExp("^[a-z,A-Z,0-9]*$")) !== null) {
					addFolderAction.validField(refField);
				} else {
					addFolderAction.invalidField(refField);
				}
			});
		},
	});
	return AddFolderAction;
});