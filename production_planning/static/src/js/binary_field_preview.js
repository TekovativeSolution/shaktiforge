/** @odoo-module **/

import { registry } from "@web/core/registry";                // Correct import for registry
import { BinaryField } from "@web/views/fields/binary/binary_field";  // Binary field import
import { useService } from "@web/core/utils/hooks";           // Import to use Odoo services
import { standardFieldProps } from "@web/views/fields/standard_field_props"; // Import for standard field props
import { _t } from "@web/core/l10n/translation";              // Translation import for _t
import { Dialog } from "@web/core/dialog/dialog";            // Dialog component for preview
import { Component, xml } from "@odoo/owl";                  // OWL (Odoo Web Library) components

const style = document.createElement('style');
style.textContent = `
    .o_field_binary_preview {
        display: flex;
        align-items: center;
        width:100%;
    }
    .preview-button {
        order: 1;
        margin-right: 5px;
    }
    .image-preview-dialog {
        text-align: center;
    }
    .image-preview-dialog img {
        max-width: 100%;
        max-height: 80vh;
        object-fit: contain;
    }
`;
document.head.appendChild(style);

// Image preview dialog component
class ImagePreviewDialog extends Component {
    static template = xml`
        <Dialog title="'Image Preview'">
            <div class="image-preview-dialog">
                <img t-att-src="props.imageUrl" alt="Image Preview"/>
            </div>
            <t t-set-slot="footer">
                <button class="btn btn-primary" t-on-click="() => props.close()">Close</button>
            </t>
        </Dialog>
    `;
    static components = { Dialog };
    static props = ["close", "imageUrl"];
}

// Binary field preview widget to show the attachment preview button
export class BinaryFieldPreview extends BinaryField {
    static template = "production_planning.BinaryFieldPreview"; // Template reference
    static components = { BinaryField };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");
    }

    static props = {
        ...standardFieldProps,
        acceptedFileExtensions: { type: String, optional: true },
        fileNameField: { type: String, optional: true },
    };

    static defaultProps = {
        acceptedFileExtensions: "*",
    };

    // Open the preview when the eye icon is clicked
    async openPreview() {
        const model = this.props.record.resModel;
        const fieldName = this.props.name;
        const recordId = this.props.record.resId;

        if (!model || !fieldName || !recordId) {
            console.error("Missing required information to fetch attachment");
            return;
        }

        try {
            const attachment = await this.orm.call(
                "mrp.production",  // The model name
                "get_attachment_preview",  // Function name defined in the Python model
                [model, fieldName, recordId]
            );
            if (attachment && attachment.url) {
                const refreshedUrl = `${attachment.url}?t=${new Date().getTime()}`;
                    if (attachment.is_image) {
                        this.dialog.add(ImagePreviewDialog, {
                            imageUrl: refreshedUrl,
                        });
                    } else if (attachment.mimetype === 'application/pdf') {
                        window.open(refreshedUrl, '_blank');
                    } else {
                        this.action.doAction({
                            type: "ir.actions.act_url",
                            url: refreshedUrl,
                            target: "New",
                        });
                    }
            } else {
                console.error("No valid attachment URL received");
            }
        } catch (error) {
            console.error("Error fetching attachment:", error);
        }
    }

    get fileName() {
        return (
            this.props.record.data[this.props.fileNameField] ||
            this.props.record.data[this.props.name] ||
            ""
        ).slice(0, 100);  // Truncate filename for display
    }
}

// Register the widget in Odoo's registry
export const binaryFieldPreview = {
    component: BinaryFieldPreview,
    displayName: _t("File"),
    supportedOptions: [
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
    ],
    supportedTypes: ["binary"],
    extractProps: ({ attrs }) => ({
        acceptedFileExtensions: attrs.accepted_file_extensions,
        fileNameField: attrs.filename,
    }),
};

registry.category("fields").add("binary_preview", binaryFieldPreview);
