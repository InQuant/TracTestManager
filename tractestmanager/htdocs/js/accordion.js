jQuery(document).ready(function($) {
    // initalize Accordion (hide all containers except first)
    $('.toggle_container').hide();
    $(".toggle_container").first().show()

    // Show / hide container when clicking on the step's headline
    $('.trigger').click( function() {
        var trig = $(this);
        var duration = 100;
        if (trig.hasClass('trigger_active')) {
            trig.next('.toggle_container').slideToggle(duration);
        } else {
            $('.trigger_active').next('.toggle_container').slideToggle(duration);
            trig.next('.toggle_container').slideToggle(duration);
        };
        // TODO: do we need this false?
        return false;
    });

    // handle the button clicks (skipped / passed /failed)
    $('button:button').click(function(){
        var actionid = parseInt(this.parentNode.id);
        if(this.name==='skip_remaining') skip_remaining(this.parentNode.id);
        else set_status(actionid, this.value);
        return false;
    });
});

var clickButton = function(element){
    $('#' + element.id + ' button[value=' + this + ']')[0].click()
}

var skip_remaining = function(data){
    // called if skip_remaining is clicked
    // get all containers
    var containers = $('div.toggle_container').toArray();

    // remove previous steps and sort inplace
    containers = containers.filter(function(element){if(element.id>=this)return true}, data);
    containers = containers.sort(function(a,b){return a.id-b.id});
    // now click skipped :)
    containers.forEach(clickButton,"skipped");
};

var set_status_success =  function(data){
    //callback when setting the status was successful
    json = jQuery.parseJSON(data);
    var toggle_container_id = parseInt(json.toggle_container_id);

    // change clolor of step according to json.status
    $("#accordion" + toggle_container_id)[0].children[1].style['background'] = json.color;
    var duration = 100;

    // hide current container
    var toggle_container = $("#" + toggle_container_id);
    toggle_container.slideToggle(duration);

    // show next container
    try{
        var next_toggle_container = $("#" + (toggle_container_id + 1));
        if(next_toggle_container != null){
            if(next_toggle_container[0].style.display != "block"){
                next_toggle_container.slideToggle(duration);
            }
        };
    }catch(TypeError){console.log("no container left");}
};


var set_status_error =  function(data){
    //callback when setting the status wasn't successful
    json = jQuery.parseJSON(data.responseText);
    alert(json.message);
};


var set_status = function(id, value){
    var inputs = $("#accordion" + id + ' :input');
    var values = {};
    values["toggle_container_id"] = id;

    values["option"]= false;
    inputs.each(function(){
        if (this.name == "option") {
            if(this.checked == true) {
                values['option'] = $(this).val();
            }
        }else{
            values[this.name] = $(this).val();
        }
    });

    if(values["comment"] && value == "passed"){
        values['status']  = "passed with comment";
    }
    else{
        values['status']  = value;
    }
    var fullurl = window.location.href;
    var url = fullurl.slice(0, fullurl.search(/TestManager/)) + "json_testaction";
    // do the post request
    $.ajax({
      type: 'POST',
      url: url,
      data: values,
      success: set_status_success,
      error: set_status_error,
      async:false
    });
    var testrun = $('input[name=testrun]').first().val();
    if(values['option'] == 'attach_file' && json.update != 'failed'){
        window.location.href = '/trac/attachment/ticket/' + testrun + '?action=new&testman_cnum=' + json.cnum;
    }
};
