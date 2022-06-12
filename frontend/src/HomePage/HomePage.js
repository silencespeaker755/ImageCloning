import { useNavigate, useParams } from "react-router-dom";
import { makeStyles } from "@material-ui/core/styles";
import { Typography } from "@material-ui/core";
import { Button } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  Background: {
    background: `linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url(homepage.png)`,
    backgroundPosition: "center",
    backgroundSize: "cover",
    backgroundRepeat: "no-repeat",
    backgroundAttachment: "fixed",
    opacity: 0.7,
    height: "100%",
    [`@media (min-height: 650px)`]: {
      height: "100vh",
    },
  },
}));

export default function HomePage() {
  const classes = useStyles();
  let navigate = useNavigate();

  return (
    <div className={classes.Background}>
      <div
        className="flex-all-center height-100"
        style={{ flexDirection: "column" }}
      >
        <Typography
          variant="h4"
          component="h2"
          style={{ color: "white", fontWeight: 700 }}
        >
          Instant Image Cloning
        </Typography>
        <div className="flex-all-center" style={{ marginTop: "30px" }}>
          <Button
            onClick={() => navigate("/upload")}
            size="large"
            style={{ color: "white", fontWeight: 500, fontSize: 25 }}
          >
            start
          </Button>
        </div>
      </div>
    </div>
  );
}
