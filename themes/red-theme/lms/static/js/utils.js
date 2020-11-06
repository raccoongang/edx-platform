$( document ).ready(function() {
setTimeout(function(){ 
console.log("TIME!!!")
$('input').on( "click", function(){
	var parentElem = $(this).parent()
	var myElem = parentElem.find("[id$='validation-error-msg']")
	var myElemParent = parentElem.find("[id$='validation-error']")
	var len = myElem.html().length;
	if( len == 0 ){
		myElemParent.attr('style', 'display: none !important');
    } else {
		myElemParent.attr('style', 'display: block !important');
	}     
});
$('.input-inline').on( "click", function(){
	// console.log($(this).attr('id'))
	var parentElem = $(this).parent()
	var myElem = parentElem.find("[id$='validation-error-msg']")
	var myElemParent = parentElem.find("[id$='validation-error']")
	var len = myElem.html().length;
	if( len == 0 ){
		myElemParent.attr('style', 'display: none !important');
    } else {
		myElemParent.attr('style', 'display: block !important');
	}     
});
function doOnOrientationChange() {
    switch(window.orientation) {  
      case -90: case 90:
        $('.videoContainer iframe').css('height','90vh');
		$('.videoContainer').css('padding-bottom','90vh');
        break; 
      default:
        $('.videoContainer iframe').css('height','100%');
		$('.videoContainer').css('padding-bottom','85%');
        break; 
    }
}
  
window.addEventListener('orientationchange', doOnOrientationChange);
  
// Initial execution if needed
doOnOrientationChange();

 }, 2000);
});
