import React from "react";
import { Typography } from "@material-ui/core";

export default function TitleSection({ title }) {
  return (
    <div className="flex-all-center title-margin">
      <div className="function-title">
        <div className="flex-all-center">
          <Typography variant="h4" component="h2">
            {title}
          </Typography>
        </div>
      </div>
    </div>
  );
}
