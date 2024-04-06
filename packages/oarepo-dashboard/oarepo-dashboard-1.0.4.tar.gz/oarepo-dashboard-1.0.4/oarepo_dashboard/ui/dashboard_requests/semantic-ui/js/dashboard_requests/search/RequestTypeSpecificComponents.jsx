import {
  LabelTypeEditRecord,
  LabelTypeDeleteRecord,
  LabelTypePublishRecord,
} from "./labels/TypeLabels";
import {
  PublishRecordIcon,
  DeleteRecordIcon,
  EditRecordIcon,
} from "./icons/TypeIcons";

export const requestTypeSpecificComponents = {
  [`RequestTypeLabel.layout.documents_edit_record`]: LabelTypeEditRecord,
  [`RequestTypeLabel.layout.documents_delete_record`]: LabelTypeDeleteRecord,
  [`RequestTypeLabel.layout.documents_publish_draft`]: LabelTypePublishRecord,
  [`InvenioRequests.RequestTypeIcon.layout.documents_edit_record`]:
    EditRecordIcon,
  [`InvenioRequests.RequestTypeIcon.layout.documents_delete_record`]:
    DeleteRecordIcon,
  [`InvenioRequests.RequestTypeIcon.layout.documents_publish_draft`]:
    PublishRecordIcon,
};
