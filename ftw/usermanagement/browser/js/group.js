jq(function(){
    
   function initGroupManagement(){
          deleteGroups();
          addGroup();
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
                      
                      var $form = jq('form[name="group_overview_form"]').serializeArray();
                      var url = (window.portal_url + "/group_delete/delete");
                      
                      jq.post(url, $form, function(data){
                          
                          tabbedview.reload_view();
                          initGroupManagement();
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
   function jquery_post_request(url, $form){
       
       jq.post(url, $form, function(data){
           
           tabbedview.reload_view();
           initGroupManagement();
           
       });
       
   }

   initGroupManagement();
});