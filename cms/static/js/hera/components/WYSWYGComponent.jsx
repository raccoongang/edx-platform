import React from 'react';


export default class WYSWYGComponent extends React.Component {

    changeHandler(e) {
        this.props.saveContent(this.props.index, e.target.getContent());
    }

    getSelectorName() {
        return `.${this.getClassName()}`;
    }

    getClassName() {
        return `hera-tinymce${this.props.index}`;
    }

    componentDidMount() {
        const self = this;

        tinymce.init({
            selector: self.getSelectorName(),
            theme: "modern",
            skin: 'studio-tmce4',
            // skin_url: "https://cdnjs.cloudflare.com/ajax/libs/tinymce/4.5.10/skins/lightgray/,
            schema: "html5",
            visual: false,
            plugins: "textcolor, link, image, codemirror, table",
            codemirror: {
              path: baseUrl + "/js/vendor"
            },
            image_advtab: true,

            /*
            We may want to add "styleselect" when we collect all styles used throughout the LMS
             */
            toolbar: "table | formatselect | fontselect | bold italic underline forecolor wrapAsCode | " + "alignleft aligncenter alignright alignjustify | " + "bullist numlist outdent indent blockquote | link unlink " + ((this.new_image_modal ? 'insertImage' : 'image') + " | code"),
            block_formats: interpolate("%(paragraph)s=p;%(preformatted)s=pre;%(heading3)s=h3;%(heading4)s=h4;%(heading5)s=h5;%(heading6)s=h6", {
              paragraph: gettext("Paragraph"),
              preformatted: gettext("Preformatted"),
              heading3: gettext("Heading 3"),
              heading4: gettext("Heading 4"),
              heading5: gettext("Heading 5"),
              heading6: gettext("Heading 6")
            }, true),
            width: '100%',
            // height: '400px',
            menubar: false,
            statusbar: false,
            init_instance_callback: editor => {
                editor.on('change', e => {
                    self.changeHandler(e);
                });
                if (!self.editor) {
                    self.editor = editor;
                }
            }
        });
    }

    render() {
        // hack to load newly loaded content into editor
        if (this.editor && this.props.shouldReset) {
            this.editor.setContent(this.props.content);
        }
        return (
            <textarea key={this.props.index} className={this.getClassName()} placeholder="Enter a content" defaultValue={this.props.content}>
            </textarea>
        )
    }
}
