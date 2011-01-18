jq(function(){
   
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
               jq('div#usertable').load('./@@user_management/render_table', function(){
                   initGroupOverlay();
               });
               api.close();
           },
             'closeselector':'[name=form.Cancel]'
       });
   }
   initGroupOverlay();
   
   function deleteUsers(){
       
   }
   
}); 