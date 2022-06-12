import React from "react";
import CircularProgress from "@material-ui/core/CircularProgress";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles(() => ({
  loading: {
    marginTop: "10px",
    color: "#bbbbbb",
  },
}));

export default function Loading() {
  const classes = useStyles();
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <CircularProgress className={classes.loading} />
    </div>
  );
}
