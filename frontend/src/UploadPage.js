import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import InputPhotoSection from "./components/InputPhotoSection";
import CloudUploadIcon from "@material-ui/icons/CloudUpload";
import { Button } from "@material-ui/core";
import Loading from "./components/Loading";
import "./App.css";

function UploadPage() {
  let navigate = useNavigate();
  const [submit, setSubmit] = useState(false);
  const [croppedId, setCroppedId] = useState("");
  const [backgroundId, setBackgroundId] = useState("");

  const handleSubmit = () => {
    setSubmit(true);
  };

  const reset = () => {
    setSubmit(false);
  };

  useEffect(() => {
    console.log(submit, croppedId, backgroundId);
    if (!submit && croppedId && backgroundId) {
      console.log(croppedId, backgroundId);
      console.log("route");
      navigate(`/crop/${croppedId}`);
    }
  }, [submit, croppedId, backgroundId]);

  return (
    <div className="border-section">
      <div>
        <div className="photo-section">
          <InputPhotoSection
            label={"contained-cropped-file-url"}
            setId={setCroppedId}
            submitting={submit}
            reset={reset}
          />
          <InputPhotoSection
            label={"contained-background-file-url"}
            setId={setBackgroundId}
            submitting={submit}
            reset={reset}
          />
        </div>
      </div>
      <div className="flex-all-center" style={{ marginTop: "30px" }}>
        {submit ? (
          <Loading />
        ) : (
          <Button
            variant="outlined"
            startIcon={<CloudUploadIcon />}
            onClick={handleSubmit}
          >
            Submit
          </Button>
        )}
      </div>
    </div>
  );
}

export default UploadPage;
