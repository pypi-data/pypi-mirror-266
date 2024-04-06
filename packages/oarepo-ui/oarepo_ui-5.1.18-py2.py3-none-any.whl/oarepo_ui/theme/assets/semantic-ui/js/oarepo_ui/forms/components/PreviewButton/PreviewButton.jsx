import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_ui/i18next";
import { useFormikContext } from "formik";

export const PreviewButton = React.memo(({ ...uiProps }) => {
  const { handleSubmit, isSubmitting } = useFormikContext();
  return (
    <Button
      name="preview"
      disabled
      loading={isSubmitting}
      color="grey"
      onClick={handleSubmit}
      icon="eye"
      labelPosition="left"
      content={i18next.t("Preview")}
      type="button"
      {...uiProps}
    />
  );
});

export default PreviewButton;
