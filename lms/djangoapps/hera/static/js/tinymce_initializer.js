(function () {
    tinymce.init({
        selector: 'textarea',
        theme: "modern",
        skin: 'studio-tmce4',
        // skin_url: "https://cdnjs.cloudflare.com/ajax/libs/tinymce/4.5.10/skins/lightgray/,
        schema: "html5",
        visual: false,
        plugins: "textcolor, link, image, codemirror, table",
        codemirror: {
          path: '/static/' + "/js/vendor"
        },
        image_advtab: true,

        /*
        We may want to add "styleselect" when we collect all styles used throughout the LMS
         */
        toolbar: "table | formatselect | fontsizeselect | fontselect | bold italic underline forecolor wrapAsCode | " + "alignleft aligncenter alignright alignjustify | " + "bullist numlist outdent indent blockquote | link unlink " + ((this.new_image_modal ? 'insertImage' : 'image') + " | code"),
        block_formats: interpolate("%(paragraph)s=p;%(preformatted)s=pre;%(heading3)s=h3;%(heading4)s=h4;%(heading5)s=h5;%(heading6)s=h6", {
          paragraph: gettext("Paragraph"),
          preformatted: gettext("Preformatted"),
          heading3: gettext("Heading 3"),
          heading4: gettext("Heading 4"),
          heading5: gettext("Heading 5"),
          heading6: gettext("Heading 6")
        }, true),
        width: '60%',
        menubar: false,
        statusbar: false,
        relative_urls: false,
    });
})();
