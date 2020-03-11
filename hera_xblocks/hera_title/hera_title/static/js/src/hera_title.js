/* Javascript for HeraTitleXBlock. */
function HeraTitleXBlock(runtime, element, initArgs) {
    var blockId = initArgs.block_id;

    $(function ($) {
        $('.button-next-' + blockId, element).click(function() {
            $('.sequence-nav-button.button-next').get(0).click();
        });
    });
}
