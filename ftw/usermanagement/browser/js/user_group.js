jq(function(){

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
       jq.ajaxSetup ({
           // Disable caching of AJAX responses
           cache: false
       });

       jq('[href*=user_membership]').prepOverlay({
           subtype:'ajax',
           formselector:'form',
           config:{onBeforeLoad: function(e){
               var $select = jq('[name=new_groups:list]', e.target.getOverlay());
                $select.multiselect({sortable: false});
                $multi = $select.data('multiselect');
               // It seems that, ui.multiselect has some style problem in a overlay
               $multi.container.css('width','601px');
               $multi.availableActions.css('width','300px');
               $multi.availableContainer.css('width','300px');
               $multi.selectedActions.css('width','300px');
               $multi.selectedContainer.css('width','300px');
               $multi.availableList.css('height','250px');
               $multi.selectedList.css('height','250px');
           }},
           afterpost: function(el, overlay){
               var api = overlay.data('overlay');
               //reload table
               load_status_messages();
               tabbedview.reload_view();
               initUserGroupManagement();
               api.close();
           },
             'closeselector':'[name=form.Cancel]'
       });
   }


   function deleteUsers(){
       jq('[name=delete.users]').bind('click', function(e){
           e.stopPropagation();
           e.preventDefault();
           $form = jq(this).closest('form');
           var $fakelink = jq('[href*=user_delete]');
           if (!$fakelink.length)
               $fakelink = jq('<a style="display:none" href="./user_delete">dfdf</a>');
           jq(this).after($fakelink);
           $fakelink.prepOverlay({
               subtype:'ajax',
               'closeselector':'[name=form.Cancel]',
               config:{onBeforeLoad: function(e){
                   var $overlay = e.target.getOverlay();
                   var $list = jq('ul.userList', $overlay);

                   jq('input:checked', $form).each(function(i, o){
                       $list.append('<li>' + jq(o).attr('value') + '</li>');
                   });

                   var $del_button = jq('[name=form.submitted]', $overlay);
                   $del_button.bind('click', function(e){
                       e.stopPropagation();
                       e.preventDefault();

                       var $form = jq('form[name="tabbedview_form"]').serializeArray();
                       var url = (window.portal_url + "/user_delete/delete");

                       jq.post(url, $form, function(data){

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
       jq('[href*=user-information]').prepOverlay({
           subtype:'ajax',
           formselector:'form.edit-form',
           closeselector:'[name=form.Cancel]',
           filter: '#content > *',
           noform: function(el){
               tabbedview.reload_view();
               initUserGroupManagement();
               return 'close';
           }
       });
   }

   function addUser(){
       jq('table.addusertable input[name="submit.add"]').bind('click', function(e,o){
           // add a new user
            e.preventDefault();

            var $form = jq('form[name="add_member_form"]').serializeArray();
            var url = (window.portal_url + "/user_register");
            jquery_post_request(url, $form);
       });
   }

   function notifyUsers(){
       jq('div#users_management_overview input[name="notify.users"]').bind('click', function(e,o){
           // notify users without pw-reset
            e.preventDefault();
            var $form = jq('form[name="tabbedview_form"]').serializeArray();
            var url = (window.portal_url + "/user_notify");
            jquery_post_request(url, $form);
       });
   }

   function notifyUsersPassword(){
       jq('div#users_management_overview input[name="notify.users.password"]').bind('click', function(e,o){
           // notify users with pw-reset
            e.preventDefault();
            var $form = jq('form[name="tabbedview_form"]').serializeArray();
            var url = (window.portal_url + "/user_notify");
            $form.push({'name':"reset_pw", 'value':"True"});
            jquery_post_request(url, $form);
       });
   }


   //Show an overlay with selected and available users, per group
   function initUserOverlay(){
       jq.ajaxSetup ({
           // Disable caching of AJAX responses
           cache: false
       });

       jq('[href*=group_membership]').prepOverlay({
           subtype:'ajax',
           formselector:'form',
           config:{onBeforeLoad: function(e){
               var $select = jq('[name=new_users:list]', e.target.getOverlay());
                $select.multiselect({sortable: false});
                $multi = $select.data('multiselect');
               // It seems that, ui.multiselect has some style problem in a overlay
               $multi.container.css('width','601px');
               $multi.availableActions.css('width','300px');
               $multi.availableContainer.css('width','300px');
               $multi.selectedActions.css('width','300px');
               $multi.selectedContainer.css('width','300px');
               $multi.availableList.css('height','250px');
               $multi.selectedList.css('height','250px');
           }},
           afterpost: function(el, overlay){
               var api = overlay.data('overlay');
               //reload table
               load_status_messages();
               tabbedview.reload_view();
               initUserGroupManagement();
               api.close();
           },
             'closeselector':'[name=form.Cancel]'
       });
   }



   function deleteGroups(){
      jq('[name=delete.groups]').bind('click', function(e){
          e.stopPropagation();
          e.preventDefault();
          $form = jq(this).closest('form');
          var $fakelink = jq('[href*=group_delete]');
          if (!$fakelink.length)
              $fakelink = jq('<a style="display:none" href="./group_delete">dfdf</a>');
          jq(this).after($fakelink);
          $fakelink.prepOverlay({
              subtype:'ajax',
              'closeselector':'[name=form.Cancel]',
              config:{onBeforeLoad: function(e){
                  var $overlay = e.target.getOverlay();
                  var $list = jq('ul.groupList', $overlay);

                  jq('input:checked', $form).each(function(i, o){
                      $list.append('<li>' + jq(o).attr('value') + '</li>');
                  });

                  var $del_button = jq('[name=form.submitted]', $overlay);
                  $del_button.bind('click', function(e){
                      e.stopPropagation();
                      e.preventDefault();

                      var $form = jq('form[name="tabbedview_form"]').serializeArray();
                      var url = (window.portal_url + "/group_delete/delete");

                      jq.post(url, $form, function(data){
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
       jq('table.addgrouptable input[name="add.group"]').bind('click', function(e,o){
           // add a new group
            e.preventDefault();
            var $form = jq('form[name="add_group_form"]').serializeArray();
            var url = (window.portal_url + "/group_add");
            jquery_post_request(url, $form);
       });
   }

   function load_status_messages(){
       remove_status_messages();
       jq.get('./global_statusmessage', {}, function(response){
           var $messages = jq('<div />').append(response).find('dl.portalMessage:not(#kssPortalMessage)');
           jq('#content').before($messages);
       });
   }

   function remove_status_messages(){
       jq('dl.portalMessage:not(#kssPortalMessage)').remove();
   }

   function jquery_post_request(url, $form){
       jq.post(url, $form, function(data){
           load_status_messages();
           tabbedview.reload_view();
           initUserGroupManagement();
       });
   }

   initUserGroupManagement();

});