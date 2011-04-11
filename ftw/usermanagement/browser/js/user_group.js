jq(function(){
   
   function initUserGroupManagement(){
          initGroupOverlay();
          editUser();
          deleteUsers();
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
               jq('div#usertable').load('./@@tabbedview/render_listing', function(){
                   initUserGroupManagement();
               });
               api.close();
           },
             'closeselector':'[name=form.Cancel]'
       });
   }
  

   function deleteUsers(){
       jq('[name=delete.user]').bind('click', function(e){
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
                       $list.append('<li'> + jq(o).attr('value') + '</li>');
                   });
                   
                   var $del_button = jq('[name=form.submitted]', $overlay);
                   $del_button.bind('click', function(e){
                       e.stopPropagation();
                       e.preventDefault();
                       // Simulate delete button
                       $form.append('<input type="hidden" name="delete.user" value="1" />');
                       $form.submit();
                       $overlay.data('overlay').close();
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
               jq('div#usertable').load('./@@user_management/render_table', function(){
                   initUserGroupManagement();
               });
               return 'close';
           }
       });
   }

   initUserGroupManagement();
}); 