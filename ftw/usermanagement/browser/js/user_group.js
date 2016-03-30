$(function(){

   function initUserGroupManagement(){
          initGroupOverlay();
          initUserOverlay();
          editUser();
          deleteUsers();
          notifyUsers();
          notifyUsersPassword();
          addUser();
          deleteGroups();
          addGroup();
   }

   //Show a overlay with selected and available groups, per user
   function initGroupOverlay(){
       $.ajaxSetup ({
           // Disable caching of AJAX responses
           cache: false
       });

       $('[href*=user_membership]').prepOverlay({
           subtype:'ajax',
           formselector:'form',
           config:{onBeforeLoad: function(e){
             var $select = $('[name="new_groups:list"]', this.getOverlay());
             if($select.length) {
               $select.multiselect({sortable: false});
               $multi = $select.data('multiselect');
               if(!$multi){
                 $multi = $select.data('ui-multiselect');
               }
               // It seems that, ui.multiselect has some style problem in a overlay
               $multi.container.css('width','601px');
               $multi.availableActions.css('width','300px');
               $multi.availableContainer.css('width','300px');
               $multi.selectedActions.css('width','300px');
               $multi.selectedContainer.css('width','300px');
               $multi.availableList.css('height','250px');
               $multi.selectedList.css('height','250px');
             }
           }},
           afterpost: function(el, overlay){
               var api = overlay.data('overlay');
               //reload table
               load_status_messages();
               tabbedview.reload_view();
               initUserGroupManagement();
               api.close();
           },
             'closeselector':'[name="form.Cancel"]'
       });
   }


   function deleteUsers(){
       $('[name="delete.users"]').bind('click', function(e){
           e.stopPropagation();
           e.preventDefault();
           $form = $(this).closest('form');
           var $fakelink = $('[href*=user_delete]');
           if (!$fakelink.length)
               $fakelink = $('<a style="display:none" href="./user_delete">dfdf</a>');
           $(this).after($fakelink);
           $fakelink.prepOverlay({
               subtype:'ajax',
               'closeselector':'[name="form.Cancel"]',
               config:{onBeforeLoad: function(e){
                   var $overlay = this.getOverlay();
                   var $list = $('ul.userList', $overlay);

                   $('input:checked', $form).each(function(i, o){
                       $list.append('<li>' + $(o).attr('value') + '</li>');
                   });

                   var $del_button = $('[name="form.submitted"]', $overlay);
                   $del_button.bind('click', function(e){
                       e.stopPropagation();
                       e.preventDefault();

                       var $form = $('form[name="tabbedview_form"]').serializeArray();
                       var url = (window.portal_url + "/user_delete/delete");

                       $.post(url, $form, function(data){

                           load_status_messages();
                           tabbedview.reload_view();
                           initUserGroupManagement();
                           $overlay.data('overlay').close();
                       });
                   });
               }}
           });
      // load overlay
      $fakelink.trigger('click');
      });
   }

   function editUser(){
       $('[href*=user-information]').prepOverlay({
           subtype:'ajax',
           formselector:'form.edit-form',
           closeselector:'[name="form.Cancel"]',
           filter: '#content > *',
           noform: function(el){
               tabbedview.reload_view();
               initUserGroupManagement();
               return 'close';
           }
       });
   }

   function addUser(){
       $('table.addusertable input[name="submit.add"]').bind('click', function(e,o){
           // add a new user
            e.preventDefault();

            var $form = $('form[name="add_member_form"]').serializeArray();
            var url = (window.portal_url + "/user_register");
            jquery_post_request(url, $form);
       });
   }

   function notifyUsers(){
       $('div#users_management_overview input[name="notify.users"]').bind('click', function(e,o){
           // notify users without pw-reset
            e.preventDefault();
            var $form = $('form[name="tabbedview_form"]').serializeArray();
            var url = (window.portal_url + "/user_notify");
            jquery_post_request(url, $form);
       });
   }

   function notifyUsersPassword(){
       $('div#users_management_overview input[name="notify.users.password"]').bind('click', function(e,o){
           // notify users with pw-reset
            e.preventDefault();
            var $form = $('form[name="tabbedview_form"]').serializeArray();
            var url = (window.portal_url + "/user_notify");
            $form.push({'name':"reset_pw", 'value':"True"});
            jquery_post_request(url, $form);
       });
   }


   //Show an overlay with selected and available users, per group
   function initUserOverlay(){
       $.ajaxSetup ({
           // Disable caching of AJAX responses
           cache: false
       });

       $('[href*=group_membership]').prepOverlay({
           subtype:'ajax',
           formselector:'form',
           config:{onBeforeLoad: function(e){
             var $select = $('[name="new_users:list"]', this.getOverlay());
             if($select.length) {
               $select.multiselect({sortable: false});
               $multi = $select.data('multiselect');
               if(!$multi){
                 $multi = $select.data('ui-multiselect');
               }
               // It seems that, ui.multiselect has some style problem in a overlay
               $multi.container.css('width','601px');
               $multi.availableActions.css('width','300px');
               $multi.availableContainer.css('width','300px');
               $multi.selectedActions.css('width','300px');
               $multi.selectedContainer.css('width','300px');
               $multi.availableList.css('height','250px');
               $multi.selectedList.css('height','250px');
             }
           }},
           afterpost: function(el, overlay){
               var api = overlay.data('overlay');
               //reload table
               load_status_messages();
               tabbedview.reload_view();
               initUserGroupManagement();
               api.close();
           },
             'closeselector':'[name="form.Cancel"]'
       });
   }



   function deleteGroups(){
      $('[name="delete.groups"]').bind('click', function(e){
          e.stopPropagation();
          e.preventDefault();
          $form = $(this).closest('form');
          var $fakelink = $('[href*=group_delete]');
          if (!$fakelink.length)
              $fakelink = $('<a style="display:none" href="./group_delete">dfdf</a>');
          $(this).after($fakelink);
          $fakelink.prepOverlay({
              subtype:'ajax',
              'closeselector':'[name="form.Cancel"]',
              config:{onBeforeLoad: function(e){
                  var $overlay = this.getOverlay();
                  var $list = $('ul.groupList', $overlay);

                  $('input:checked', $form).each(function(i, o){
                      $list.append('<li>' + $(o).attr('value') + '</li>');
                  });

                  var $del_button = $('[name="form.submitted"]', $overlay);
                  $del_button.bind('click', function(e){
                      e.stopPropagation();
                      e.preventDefault();

                      var $form = $('form[name="tabbedview_form"]').serializeArray();
                      var url = (window.portal_url + "/group_delete/delete");

                      $.post(url, $form, function(data){
                          load_status_messages();
                          tabbedview.reload_view();
                          initUserGroupManagement();
                          $overlay.data('overlay').close();
                      });
                  });
              }}
          });
     // load overlay
     $fakelink.trigger('click');
     });

   }
   function addGroup(){
       $('table.addgrouptable input[name="add.group"]').bind('click', function(e,o){
           // add a new group
            e.preventDefault();
            var $form = $('form[name="add_group_form"]').serializeArray();
            var url = (window.portal_url + "/group_add");
            jquery_post_request(url, $form);
       });
   }

   function load_status_messages(){
       remove_status_messages();
       $.get('./global_statusmessage', {}, function(response){
           var $messages = $('<div />').append(response).find('dl.portalMessage:not(#kssPortalMessage)');
           $('#content').before($messages);
       });
   }

   function remove_status_messages(){
       $('dl.portalMessage:not(#kssPortalMessage)').remove();
   }

   function jquery_post_request(url, $form){
       $.post(url, $form, function(data){
           load_status_messages();
           tabbedview.reload_view();
           initUserGroupManagement();
       });
   }

   // Initialize the the management.
   initUserGroupManagement();

   /*
   For extjs compatibility we need this ugly hack.
   The last triggered event is the gridRendered, but on this time the content
   isn't load. So we need a timeout to grant the content is fully loaded.
   */
   $('.tab_container').bind('gridRendered', function(event) {
       window.setTimeout(initUserGroupManagement, 10);
   });

});
